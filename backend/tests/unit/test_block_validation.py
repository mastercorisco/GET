from __future__ import annotations

import json

from app.domain.block.models import DevelopmentPoint
from app.domain.block.schemas import PointLists
from app.domain.block.service import validate_point, suggested_status


class _Session:
    def get(self, _model, _id):
        return None


def test_suggested_status_ready() -> None:
    point = DevelopmentPoint(
        id="p1",
        block_id="b1",
        sort_order=1,
        title="Título",
        core_idea="Afirmação técnica.",
        lists_json=json.dumps(
            PointLists(development_guidance=["orientação"]).model_dump(),
            ensure_ascii=False,
        ),
    )
    issues = validate_point(_Session(), point)
    assert suggested_status(point, issues) == "ready"


def test_core_idea_writing_suggestion() -> None:
    point = DevelopmentPoint(
        id="p1",
        block_id="b1",
        sort_order=1,
        title="T",
        core_idea="Explicar o comportamento do PLC.",
        lists_json=json.dumps(PointLists().model_dump()),
    )
    issues = validate_point(_Session(), point)
    codes = {i.code for i in issues}
    assert "core_idea_writing_instruction" in codes