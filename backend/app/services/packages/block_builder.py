from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.block.models import DevelopmentPoint, Premise
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
        if not isinstance(lists, dict):
            lists = {}
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

    return {
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