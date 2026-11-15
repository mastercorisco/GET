from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeDraft, KnowledgeItem, KnowledgeRelation, KnowledgeRevision
from app.models.technical_profile import TechnicalProfilePayload
from app.models.knowledge import RelationType

_EDIT_POLICY_DISCUSSION = {
    "mode": "propose_changes",
    "protected_fields": [
        "id",
        "revision",
        "states.approval",
        "states.lifecycle",
        "provenance",
    ],
    "editable_fields": [
        "title",
        "content",
        "rationale",
        "notes",
        "relations",
        "technical_profile.data",
    ],
    "allow_new_items": True,
    "allow_removal_proposals": True,
}

_EDIT_POLICY_EDITABLE = {
    "mode": "editable",
    "protected_fields": [
        "id",
        "revision",
        "states.approval",
        "states.lifecycle",
        "provenance",
    ],
    "editable_fields": [
        "title",
        "content",
        "rationale",
        "notes",
        "relations",
        "technical_profile.data",
    ],
    "allow_new_items": True,
    "allow_removal_proposals": True,
}


def _iso_z(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def _latest_revision(session: Session, item_id: str) -> KnowledgeRevision | None:
    return session.scalar(
        select(KnowledgeRevision)
        .where(KnowledgeRevision.item_id == item_id)
        .order_by(KnowledgeRevision.revision_num.desc())
        .limit(1)
    )


def _relations_for_export(session: Session, item_id: str) -> list[dict]:
    rows = session.execute(
        select(KnowledgeRelation, RelationType.code)
        .join(RelationType, RelationType.id == KnowledgeRelation.relation_type_id)
        .where(KnowledgeRelation.source_item_id == item_id)
    )
    return [
        {"relation_type": code, "target_id": relation.target_item_id, "note": None}
        for relation, code in rows
    ]


def _technical_profile(session: Session, revision: KnowledgeRevision | None, item_id: str) -> dict | None:
    if revision is not None:
        row = session.scalar(
            select(TechnicalProfilePayload).where(TechnicalProfilePayload.revision_id == revision.id)
        )
        if row is not None:
            import json

            try:
                data = json.loads(row.data_json)
            except json.JSONDecodeError:
                data = {}
            if not isinstance(data, dict):
                data = {}
            return {"profile_type": row.profile_type, "data": data}
    return None


def export_knowledge_item(
    session: Session,
    item: KnowledgeItem,
    *,
    profile: str,
    created_by: str,
    use_draft_if_no_revision: bool,
    edit_policy: dict | None = None,
    warnings: list[dict],
) -> dict | None:
    revision = _latest_revision(session, item.id)
    draft = session.get(KnowledgeDraft, item.id)
    if draft is None:
        return None

    if revision is None:
        if profile == "redaction" or not use_draft_if_no_revision:
            return None
        warnings.append(
            {
                "code": "DRAFT_EXPORT",
                "message": f"Unidade {item.id} exportada a partir do rascunho (sem revisão concluída).",
            }
        )
        revision_num = 1
        title = draft.title
        content = draft.content_md
        knowledge_type = draft.knowledge_type
        states = {
            "maturity": draft.maturity,
            "approval": draft.approval,
            "lifecycle": draft.lifecycle,
        }
        technical_profile = None
    else:
        revision_num = revision.revision_num
        title = revision.title
        content = revision.content_md
        knowledge_type = revision.knowledge_type
        states = {
            "maturity": revision.maturity,
            "approval": revision.approval,
            "lifecycle": revision.lifecycle,
        }
        technical_profile = _technical_profile(session, revision, item.id)

    notes = draft.origin_context
    payload = {
        "id": item.id,
        "code": item.human_code,
        "aliases": [],
        "title": title,
        "content": content,
        "rationale": None,
        "notes": notes,
        "knowledge_type": knowledge_type,
        "revision": revision_num,
        "states": states,
        "scope": {"scope_type": item.scope_type, "scope_id": item.scope_id},
        "technical_profile": technical_profile,
        "relations": _relations_for_export(session, item.id),
        "provenance": {
            "origin_type": "manual_entry",
            "origin_id": None,
            "created_by": created_by,
            "created_at": _iso_z(item.created_at),
            "source_reference_ids": [],
            "source_export_id": None,
            "source_import_id": None,
        },
        "edit_policy": edit_policy or _EDIT_POLICY_DISCUSSION,
    }
    return payload