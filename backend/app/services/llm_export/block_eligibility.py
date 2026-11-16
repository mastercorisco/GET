from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.block.export_support import export_status_for_point
from app.domain.block.models import DevelopmentPoint


def block_has_exportable_points(session: Session, block_id: str, *, include_draft: bool) -> bool:
    points = list(session.scalars(select(DevelopmentPoint).where(DevelopmentPoint.block_id == block_id)))
    for point in points:
        if export_status_for_point(point, include_draft) is not None:
            return True
    return False


def count_exportable_points(session: Session, block_id: str, *, include_draft: bool) -> int:
    points = list(session.scalars(select(DevelopmentPoint).where(DevelopmentPoint.block_id == block_id)))
    return sum(1 for p in points if export_status_for_point(p, include_draft) is not None)