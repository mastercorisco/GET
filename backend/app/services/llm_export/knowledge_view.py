from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import AssociationRole, DocumentAssociation, DocumentNode
from app.models.knowledge import KnowledgeItem
from app.services.export.knowledge_mapper import export_knowledge_item


def _association_priority(role_code: str) -> str:
    if role_code == "mandatory_content":
        return "mandatory"
    return "recommended"


def _requirements_from_profile(technical_profile: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not technical_profile or not isinstance(technical_profile.get("data"), dict):
        return []
    data = technical_profile["data"]
    reqs = data.get("requirements")
    if isinstance(reqs, list):
        return [r for r in reqs if isinstance(r, dict)]
    return []


def _unit_view(exported: dict[str, Any], *, priority: str) -> dict[str, Any]:
    states = exported.get("states") or {}
    return {
        "id": exported["id"],
        "code": exported.get("code"),
        "title": exported["title"],
        "type": exported.get("knowledge_type"),
        "status": states.get("approval"),
        "priority": priority,
        "statement": exported.get("content") or "",
        "rationale": exported.get("rationale"),
        "requirements": _requirements_from_profile(exported.get("technical_profile")),
        "examples": [],
        "exceptions": [],
        "references": [],
    }


def collect_association_knowledge_ids(
    session: Session,
    node_ids: list[str],
) -> dict[str, str]:
    """item_id -> association role code (first wins by sort_order)."""
    if not node_ids:
        return {}
    rows = session.execute(
        select(DocumentAssociation, AssociationRole.code)
        .join(AssociationRole, AssociationRole.id == DocumentAssociation.role_id)
        .where(DocumentAssociation.document_node_id.in_(node_ids))
        .order_by(DocumentAssociation.sort_order, DocumentAssociation.id)
    )
    result: dict[str, str] = {}
    for assoc, role_code in rows:
        if assoc.knowledge_item_id not in result:
            result[assoc.knowledge_item_id] = role_code
    return result


def build_knowledge_units(
    session: Session,
    *,
    block: DocumentNode,
    fascicle_id: str | None,
    preparation_item_ids: set[str],
    profile: str,
    created_by: str,
    warnings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    node_ids = [block.id]
    if fascicle_id:
        node_ids.append(fascicle_id)
    assoc_map = collect_association_knowledge_ids(session, node_ids)
    all_ids = sorted(set(preparation_item_ids) | set(assoc_map.keys()))

    units: list[dict[str, Any]] = []
    for item_id in all_ids:
        item = session.get(KnowledgeItem, item_id)
        if item is None:
            continue
        exported = export_knowledge_item(
            session,
            item,
            profile=profile,
            created_by=created_by,
            use_draft_if_no_revision=profile == "discussion",
            warnings=warnings,
        )
        if exported is None:
            continue
        role_code = assoc_map.get(item_id, "")
        priority = _association_priority(role_code)
        units.append(_unit_view(exported, priority=priority))
    return units