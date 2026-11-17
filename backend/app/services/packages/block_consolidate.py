from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.block.models import DEFAULT_LISTS_JSON, DevelopmentPoint, Premise
from app.models.document import DocumentNode
from app.models.imports import ChangeDecision, ChangeProposal, MergeSession


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def apply_block_proposals(session: Session, merge_session_id: str) -> dict[str, int]:
    pairs = session.execute(
        select(ChangeProposal, ChangeDecision)
        .join(ChangeDecision, ChangeDecision.proposal_id == ChangeProposal.id)
        .where(ChangeProposal.merge_session_id == merge_session_id)
    ).all()

    stats: dict[str, int] = {
        "proposals_total": len(pairs),
        "accepted": 0,
        "block_fields_applied": 0,
        "point_updates_applied": 0,
        "point_creates_applied": 0,
        "premise_updates_applied": 0,
        "premise_creates_applied": 0,
        "point_updates_missing": 0,
        "point_wrong_block": 0,
        "fields_written": 0,
        "total_writes": 0,
    }

    for proposal, decision in pairs:
        if decision.decision != "accepted":
            continue
        if proposal.protected_touch and not decision.confirmed_protected:
            raise ValueError(f"Proposta {proposal.id} requer confirmação de campos protegidos.")

    merge = session.get(MergeSession, merge_session_id)
    if merge is None:
        raise ValueError("Sessão de merge não encontrada.")
    block_id = merge.fascicle_node_id  # reused column for block scope

    for proposal, decision in pairs:
        if decision.decision != "accepted":
            continue
        stats["accepted"] += 1
        changes = json.loads(proposal.field_changes_json)
        kind = proposal.proposal_kind

        if kind == "block_field":
            block = session.get(DocumentNode, block_id)
            if block is None:
                continue
            block_wrote = False
            for field, delta in changes.items():
                proposed = delta.get("proposed")
                if proposed is None:
                    continue
                if field == "objective":
                    block.objective = str(proposed)
                elif field == "scope":
                    block.scope = str(proposed)
                elif field == "title":
                    block.title = str(proposed)
                elif field == "target_output":
                    block.target_output_json = json.dumps(proposed, ensure_ascii=False)
                else:
                    continue
                block_wrote = True
                stats["fields_written"] += 1
            if block_wrote:
                stats["block_fields_applied"] += 1
                stats["total_writes"] += 1
        elif kind == "point_update":
            point = session.get(DevelopmentPoint, proposal.target_item_id)
            if point is None:
                stats["point_updates_missing"] += 1
                continue
            if point.block_id != block_id:
                stats["point_wrong_block"] += 1
                continue
            fields_applied = 0
            for field, delta in changes.items():
                if field.startswith("_"):
                    continue
                proposed = delta.get("proposed")
                if proposed is None:
                    continue
                if field == "title":
                    point.title = str(proposed)
                elif field == "core_idea":
                    point.core_idea = str(proposed)
                elif field == "intended_outcome":
                    point.intended_outcome = str(proposed)
                elif field == "lists":
                    point.lists_json = json.dumps(proposed, ensure_ascii=False)
                else:
                    continue
                fields_applied += 1
            if fields_applied:
                point.updated_at = _utcnow()
                stats["point_updates_applied"] += 1
                stats["fields_written"] += fields_applied
                stats["total_writes"] += 1
        elif kind == "point_create":
            proposed = changes.get("full_point", {}).get("proposed", {})
            max_order = session.scalar(
                select(func.max(DevelopmentPoint.sort_order)).where(DevelopmentPoint.block_id == block_id)
            )
            sort_order = proposed.get("sort_order") or ((max_order or 0) + 1)
            lists_json = json.dumps(proposed.get("lists") or json.loads(DEFAULT_LISTS_JSON), ensure_ascii=False)
            stats["point_creates_applied"] += 1
            stats["total_writes"] += 1
            session.add(
                DevelopmentPoint(
                    id=str(uuid.uuid4()),
                    block_id=block_id,
                    sort_order=int(sort_order),
                    title=proposed.get("title", ""),
                    core_idea=proposed.get("core_idea", ""),
                    intended_outcome=proposed.get("intended_outcome", ""),
                    llm_freedom=proposed.get("llm_freedom", "bounded"),
                    status=proposed.get("status", "draft"),
                    template_id=proposed.get("template_id"),
                    needs_review=bool(proposed.get("needs_review", False)),
                    lists_json=lists_json,
                )
            )
        elif kind == "premise_update":
            premise = session.get(Premise, proposal.target_item_id)
            if premise is None:
                continue
            prem_wrote = False
            for field, delta in changes.items():
                proposed = delta.get("proposed")
                if proposed is None:
                    continue
                if field == "statement":
                    premise.statement = str(proposed)
                    prem_wrote = True
                elif field == "notes":
                    premise.notes = str(proposed) if proposed is not None else None
                    prem_wrote = True
            if prem_wrote:
                stats["premise_updates_applied"] += 1
                stats["total_writes"] += 1
                stats["fields_written"] += 1
        elif kind == "premise_create":
            proposed = changes.get("full_premise", {}).get("proposed", {})
            stats["premise_creates_applied"] += 1
            stats["total_writes"] += 1
            session.add(
                Premise(
                    id=str(uuid.uuid4()),
                    owner_kind="block",
                    owner_id=block_id,
                    statement=proposed.get("statement", ""),
                    importance=proposed.get("importance", "recommended"),
                    source_type=proposed.get("source_type", "unconfirmed_information"),
                    confidence=proposed.get("confidence", "unverified"),
                    reference_id=proposed.get("reference_id"),
                    notes=proposed.get("notes"),
                )
            )

    return stats