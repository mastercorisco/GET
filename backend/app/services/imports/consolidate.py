from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.config import AppSettings
from app.models.document import DocumentNode
from app.models.imports import ChangeDecision, ChangeProposal, ImportRecord, MergeSession
from app.models.knowledge import KnowledgeDraft, KnowledgeItem, KnowledgeRevision, Library
from app.models.technical_profile import TechnicalProfileDraft, TechnicalProfilePayload
from app.services.backup_service import create_backup
from app.services.workspace_service import workspace_session


class ConsolidateError(Exception):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _apply_draft_fields(draft: KnowledgeDraft, changes: dict) -> None:
    for field, delta in changes.items():
        if field.startswith("_") or field in ("full_item", "removal"):
            continue
        proposed = delta.get("proposed")
        if proposed is None:
            continue
        if field == "content":
            draft.content_md = str(proposed)
        elif field == "title":
            draft.title = str(proposed)
        elif field == "notes":
            draft.origin_context = str(proposed)
        elif field == "rationale":
            if draft.origin_context:
                draft.origin_context = f"{draft.origin_context}\n{proposed}"
            else:
                draft.origin_context = str(proposed)
    draft.updated_at = _utcnow()


def _conclude_revision(session: Session, item_id: str) -> None:
    draft = session.get(KnowledgeDraft, item_id)
    if draft is None:
        raise ConsolidateError(f"Rascunho em falta para {item_id}.")
    last = session.scalar(
        select(KnowledgeRevision.revision_num)
        .where(KnowledgeRevision.item_id == item_id)
        .order_by(KnowledgeRevision.revision_num.desc())
        .limit(1)
    )
    revision_num = (last or 0) + 1
    revision = KnowledgeRevision(
        item_id=item_id,
        revision_num=revision_num,
        title=draft.title,
        content_md=draft.content_md,
        origin_context=draft.origin_context,
        knowledge_type=draft.knowledge_type,
        maturity=draft.maturity,
        approval=draft.approval,
        lifecycle=draft.lifecycle,
        created_at=_utcnow(),
    )
    session.add(revision)
    session.flush()
    profile_draft = session.get(TechnicalProfileDraft, item_id)
    if profile_draft is not None:
        session.add(
            TechnicalProfilePayload(
                revision_id=revision.id,
                profile_type=profile_draft.profile_type,
                data_json=profile_draft.data_json,
            )
        )
    session.execute(
        text(
            """
            INSERT INTO knowledge_revision_fts(item_id, kind, title, content, origin_context)
            VALUES (:item_id, 'revision', :title, :content, :origin_context)
            """
        ),
        {
            "item_id": item_id,
            "title": revision.title,
            "content": revision.content_md,
            "origin_context": revision.origin_context,
        },
    )


def _consolidate_in_session(session: Session, merge_session_id: str) -> None:
    merge = session.get(MergeSession, merge_session_id)
    if merge is None:
        raise ConsolidateError("Sessão de merge não encontrada.")
    import_row = session.get(ImportRecord, merge.import_id)
    if import_row is None:
        raise ConsolidateError("Importação não encontrada.")

    pairs = session.execute(
        select(ChangeProposal, ChangeDecision)
        .join(ChangeDecision, ChangeDecision.proposal_id == ChangeProposal.id)
        .where(ChangeProposal.merge_session_id == merge_session_id)
    ).all()

    for proposal, decision in pairs:
        if decision.decision != "accepted":
            continue
        if (proposal.protected_touch or proposal.conflict) and not decision.confirmed_protected:
            raise ConsolidateError(
                f"Proposta {proposal.id} requer confirmação de campos protegidos ou conflito."
            )

    for proposal, decision in pairs:
        if decision.decision != "accepted":
            continue
        changes = json.loads(proposal.field_changes_json)
        if proposal.proposal_kind == "update":
            draft = session.get(KnowledgeDraft, proposal.target_item_id)
            if draft is None:
                raise ConsolidateError(f"Item {proposal.target_item_id} não encontrado.")
            item = session.get(KnowledgeItem, proposal.target_item_id)
            if decision.destination == "library" and item:
                lib = session.scalar(select(Library).limit(1))
                item.scope_type = "library"
                if lib:
                    item.scope_id = lib.id
            _apply_draft_fields(draft, changes)
            _conclude_revision(session, proposal.target_item_id)
        elif proposal.proposal_kind == "create":
            proposed_item = changes.get("full_item", {}).get("proposed", {})
            new_id = str(uuid.uuid4())
            dest = decision.destination or "project"
            scope_type = "library" if dest == "library" else "project"
            scope_id = merge.project_id
            if scope_type == "library":
                lib = session.scalar(select(Library).limit(1))
                if lib:
                    scope_id = lib.id
            session.add(
                KnowledgeItem(
                    id=new_id,
                    scope_type=scope_type,
                    scope_id=scope_id,
                    human_code=proposed_item.get("code"),
                    created_at=_utcnow(),
                )
            )
            states = proposed_item.get("states") or {}
            session.add(
                KnowledgeDraft(
                    item_id=new_id,
                    title=proposed_item.get("title", "Sem título"),
                    content_md=proposed_item.get("content", ""),
                    origin_context=str(proposed_item.get("notes") or proposed_item.get("rationale") or "import"),
                    knowledge_type=proposed_item.get("knowledge_type", "decision"),
                    maturity=states.get("maturity", "draft"),
                    approval=states.get("approval", "proposed"),
                    lifecycle=states.get("lifecycle", "active"),
                    updated_at=_utcnow(),
                )
            )
            session.flush()
            _conclude_revision(session, new_id)
        elif proposal.proposal_kind == "removal":
            draft = session.get(KnowledgeDraft, proposal.target_item_id)
            if draft is None:
                continue
            draft.lifecycle = "withdrawn"
            draft.updated_at = _utcnow()
            _conclude_revision(session, proposal.target_item_id)
        elif proposal.proposal_kind == "structure":
            for node_id, node_changes in changes.items():
                if not isinstance(node_changes, dict):
                    continue
                node = session.get(DocumentNode, node_id)
                if node is None:
                    continue
                title_delta = node_changes.get("title")
                if title_delta and title_delta.get("proposed"):
                    node.title = str(title_delta["proposed"])

    merge.status = "consolidated"
    import_row.status = "consolidated"


def consolidate_merge_session(app_settings: AppSettings, merge_session_id: str) -> str:
    backup = create_backup(app_settings, "critical")
    with workspace_session(app_settings) as (session, _paths):
        _consolidate_in_session(session, merge_session_id)
        session.flush()
    return backup.id