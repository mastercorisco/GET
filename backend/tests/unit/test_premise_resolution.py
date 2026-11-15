from __future__ import annotations

from app.domain.block.export import premise_to_resolved
from app.domain.block.models import Premise


def test_premise_to_resolved_origin() -> None:
    row = Premise(
        id="prem-1",
        owner_kind="block",
        owner_id="block-1",
        statement="Condição assumida.",
        importance="mandatory",
        source_type="project_decision",
        confidence="confirmed",
    )
    out = premise_to_resolved(row)
    assert out["origin_level"] == "block"
    assert out["origin_id"] == "block-1"