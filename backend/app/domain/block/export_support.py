from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.block.models import DevelopmentPoint, Premise
from app.domain.block.schemas import PointLists
from app.models.document import DocumentNode
from app.models.knowledge import KnowledgeDraft, KnowledgeItem, KnowledgeRevision
from app.models.reference import Reference


def parse_point_lists(raw: str) -> PointLists:
    try:
        data = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        data = {}
    return PointLists.model_validate(data)


def premise_to_resolved(row: Premise) -> dict[str, Any]:
    return {
        "id": row.id,
        "statement": row.statement,
        "importance": row.importance,
        "source_type": row.source_type,
        "confidence": row.confidence,
        "origin_level": row.owner_kind,
        "origin_id": row.owner_id,
        "reference_id": row.reference_id,
        "notes": row.notes,
    }


def load_premises(session: Session, owner_kind: str, owner_id: str) -> list[Premise]:
    return list(
        session.scalars(
            select(Premise)
            .where(Premise.owner_kind == owner_kind, Premise.owner_id == owner_id)
            .order_by(Premise.created_at, Premise.id)
        )
    )


def resolved_premises_for_point(
    session: Session,
    project_id: str,
    fascicle_id: str | None,
    block_id: str,
    point_id: str,
) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for kind, oid in (
        ("project", project_id),
        ("fascicle", fascicle_id),
        ("block", block_id),
        ("development_point", point_id),
    ):
        if oid is None:
            continue
        for row in load_premises(session, kind, oid):
            if row.id in seen:
                continue
            seen.add(row.id)
            result.append(premise_to_resolved(row))
    return result


def block_level_premises(
    session: Session,
    project_id: str,
    fascicle_id: str | None,
    block_id: str,
) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for kind, oid in (("project", project_id), ("fascicle", fascicle_id), ("block", block_id)):
        if oid is None:
            continue
        for row in load_premises(session, kind, oid):
            if row.id in seen:
                continue
            seen.add(row.id)
            result.append(premise_to_resolved(row))
    return result


def find_fascicle_id(session: Session, block: DocumentNode) -> str | None:
    current: DocumentNode | None = block
    while current is not None:
        if current.node_type == "fascicle":
            return current.id
        if current.parent_id is None:
            break
        current = session.get(DocumentNode, current.parent_id)
    return None


def knowledge_snapshot(session: Session, item_id: str) -> dict[str, Any] | None:
    item = session.get(KnowledgeItem, item_id)
    if item is None:
        return None
    rev = session.scalar(
        select(KnowledgeRevision)
        .where(KnowledgeRevision.item_id == item_id)
        .order_by(KnowledgeRevision.revision_num.desc())
        .limit(1)
    )
    if rev is not None:
        return {
            "id": item.id,
            "title": rev.title,
            "content": rev.content_md,
            "knowledge_type": rev.knowledge_type,
            "lifecycle": rev.lifecycle,
            "approval": rev.approval,
        }
    draft = session.get(KnowledgeDraft, item_id)
    if draft is None:
        return {"id": item.id, "title": "", "content": ""}
    return {
        "id": item.id,
        "title": draft.title,
        "content": draft.content_md,
        "knowledge_type": draft.knowledge_type,
        "lifecycle": draft.lifecycle,
        "approval": draft.approval,
    }


def reference_snapshot(session: Session, ref_id: str) -> dict[str, Any] | None:
    ref = session.get(Reference, ref_id)
    if ref is None:
        return None
    return {"id": ref.id, "title": ref.title, "citation": ref.citation, "notes": ref.notes}


def export_status_for_point(point: DevelopmentPoint, include_draft: bool) -> str | None:
    if point.status == "obsolete":
        return None
    if point.status in ("ready", "approved"):
        return point.status
    if include_draft and point.status in ("draft", "incomplete"):
        if point.title.strip() and point.core_idea.strip():
            return "ready"
    return None