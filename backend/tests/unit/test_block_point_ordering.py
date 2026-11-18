from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.domain.block.models import DevelopmentPoint
from app.domain.block.ordering import normalize_block_point_orders
from app.models.document import DocumentNode


def test_normalize_block_point_orders_sequential() -> None:
    engine = create_engine("sqlite:///:memory:")
    DevelopmentPoint.__table__.create(engine)
    DocumentNode.__table__.create(engine)
    session = sessionmaker(bind=engine)()

    block_id = str(uuid.uuid4())
    session.add(
        DocumentNode(
            id=block_id,
            project_id=str(uuid.uuid4()),
            parent_id=None,
            node_type="block",
            title="B",
            sort_key=10,
            created_at=datetime.now(timezone.utc),
        )
    )
    for order in (1, 2, 4, 50):
        session.add(
            DevelopmentPoint(
                block_id=block_id,
                sort_order=order,
                title=f"t{order}",
                core_idea="x",
            )
        )
    session.flush()
    changed = normalize_block_point_orders(session, block_id, run_id="test")
    assert changed == 2
    orders = [
        p.sort_order
        for p in session.query(DevelopmentPoint).order_by(DevelopmentPoint.sort_order).all()
    ]
    assert orders == [1, 2, 3, 4]