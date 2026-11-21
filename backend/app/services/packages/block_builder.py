from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.block.models import DevelopmentPoint, Premise
from app.services.packages.llm_shapes import normalize_point_lists
from app.models.document import DocumentNode
from app.services.document_service import compute_display_codes


def build_block_payload(session: Session, block_id: str) -> dict[str, Any]:
    block = session.get(DocumentNode, block_id)
    if block is None or block.node_type != "block":
        raise ValueError("Bloco não encontrado.")
    nodes = list(
        session.scalars(select(DocumentNode).where(DocumentNode.project_id == block.project_id))
    )
    codes = compute_display_codes(nodes)
    try:
        target_output = json.loads(block.target_output_json or "{}")
    except json.JSONDecodeError:
        target_output = {}
    if not isinstance(target_output, dict):
        target_output = {}

    points = list(
        session.scalars(
            select(DevelopmentPoint)
            .where(DevelopmentPoint.block_id == block_id)
            .order_by(DevelopmentPoint.sort_order)
        )
    )
    point_payloads: list[dict[str, Any]] = []
    for p in points:
        try:
            lists = json.loads(p.lists_json or "{}")
        except json.JSONDecodeError:
            lists = {}
        lists = normalize_point_lists(lists)
        point_payloads.append(
            {
                "id": p.id,
                "sort_order": p.sort_order,
                "title": p.title,
                "core_idea": p.core_idea,
                "intended_outcome": p.intended_outcome,
                "lists": lists,
                "status": p.status,
                "llm_freedom": p.llm_freedom,
                "template_id": p.template_id,
                "needs_review": p.needs_review,
            }
        )

    premises = list(
        session.scalars(
            select(Premise).where(
                Premise.owner_kind == "block",
                Premise.owner_id == block_id,
            )
        )
    )
    premise_payloads = [
        {
            "id": row.id,
            "statement": row.statement,
            "importance": row.importance,
            "source_type": row.source_type,
            "confidence": row.confidence,
            "reference_id": row.reference_id,
            "notes": row.notes,
        }
        for row in premises
    ]

    structure_anchor: dict[str, Any] | None = None
    if block.parent_id:
        parent = session.get(DocumentNode, block.parent_id)
        if parent is not None and parent.node_type == "fascicle":
            siblings = [
                n
                for n in nodes
                if n.parent_id == block.parent_id and n.node_type == "block"
            ]
            siblings.sort(key=lambda n: (n.sort_key, n.created_at, n.id))
            position = next(
                (i for i, n in enumerate(siblings, start=1) if n.id == block.id),
                0,
            )
            structure_anchor = {
                "fascicle_id": parent.id,
                "fascicle_display_code": codes.get(parent.id, ""),
                "position_among_blocks": position,
                "exported_at": datetime.now(timezone.utc).isoformat(),
            }

    payload: dict[str, Any] = {
        "block": {
            "id": block.id,
            "display_code": codes.get(block.id, ""),
            "title": block.title,
            "objective": block.objective or "",
            "scope": block.scope or "",
            "target_output": target_output,
        },
        "development_points": point_payloads,
        "premises": premise_payloads,
    }
    if structure_anchor is not None:
        payload["structure_anchor"] = structure_anchor
    return payload


def normalize_block_merge_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Alinha listas de pontos para comparação three-way no merge."""
    out = copy.deepcopy(payload)
    for pt in out.get("development_points") or []:
        if isinstance(pt, dict):
            pt["lists"] = normalize_point_lists(pt.get("lists"))
    return out