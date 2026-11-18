"""Ordem sequencial de pontos de desenvolvimento por bloco."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.block.models import DevelopmentPoint


def normalize_block_point_orders(session: Session, block_id: str, *, run_id: str = "normalize") -> int:
    """Garante sort_order 1..n pela ordem actual (sort_order, id). Devolve n.º de pontos alterados."""
    del run_id
    points = list(
        session.scalars(
            select(DevelopmentPoint)
            .where(DevelopmentPoint.block_id == block_id)
            .where(DevelopmentPoint.status != "obsolete")
            .order_by(DevelopmentPoint.sort_order, DevelopmentPoint.id)
        )
    )
    if not points:
        return 0

    before = [p.sort_order for p in points]
    expected = list(range(1, len(points) + 1))
    if before == expected:
        return 0

    changed = sum(1 for index, old in enumerate(before, start=1) if old != index)
    for index, point in enumerate(points, start=1):
        point.sort_order = -(index + 10_000)
    session.flush()
    for index, point in enumerate(points, start=1):
        point.sort_order = index
    session.flush()
    return changed


def normalize_project_block_point_orders(session: Session, project_id: str, *, run_id: str = "normalize") -> dict:
    del run_id
    from app.models.document import DocumentNode

    block_ids = list(
        session.scalars(
            select(DocumentNode.id).where(
                DocumentNode.project_id == project_id,
                DocumentNode.node_type == "block",
            )
        )
    )
    total_changed = 0
    blocks_touched = 0
    for block_id in block_ids:
        n = normalize_block_point_orders(session, block_id)
        if n:
            blocks_touched += 1
            total_changed += n

    return {
        "blocks": len(block_ids),
        "blocks_touched": blocks_touched,
        "points_renumbered": total_changed,
    }