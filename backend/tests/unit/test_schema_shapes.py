from __future__ import annotations

import json

from app.services.packages.llm_shapes import POINT_LIST_SHAPES, build_llm_shapes
from app.services.packages.schema_shapes import (
    development_point_field_enums,
    load_get_package_schema,
    point_list_keys,
    point_list_shapes,
)


def test_point_list_shapes_match_schema_defs() -> None:
    schema = load_get_package_schema()
    keys = point_list_keys(schema)
    assert len(keys) == 10
    shapes = point_list_shapes(schema)
    assert set(shapes) == set(keys)
    assert shapes["development_guidance"]["element_kind"] == "string"
    assert shapes["must_include"]["element_kind"] == "object"
    assert shapes["must_include"]["required_keys"] == ["text"]
    assert shapes["knowledge_item_ids"]["id_policy"] == "refs_only"
    assert shapes["knowledge_item_ids"]["creatable"] is False


def test_point_shapes_module_matches_schema() -> None:
    assert POINT_LIST_SHAPES == point_list_shapes()


def test_development_point_enums_from_schema() -> None:
    enums = development_point_field_enums()
    assert "draft" in enums["status"]
    assert "bounded" in enums["llm_freedom"]


def test_export_llm_shapes_collections_use_schema_shapes() -> None:
    default_lists = json.loads(
        '{"development_guidance":[],"perspectives":[],"questions_to_answer":[],'
        '"must_include":[],"limits_and_exclusions":[],"examples":[],'
        '"open_questions":[],"acceptance_criteria":[],"knowledge_item_ids":[],"reference_ids":[]}'
    )
    payload = {
        "block": {
            "id": "11111111-1111-4111-8111-111111111111",
            "display_code": "F01_B01",
            "title": "t",
            "objective": "o",
            "scope": "s",
            "target_output": {},
        },
        "development_points": [
            {
                "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                "sort_order": 1,
                "title": "p",
                "core_idea": "c",
                "intended_outcome": "i",
                "lists": default_lists,
                "status": "draft",
                "llm_freedom": "bounded",
            }
        ],
        "premises": [],
    }
    shapes = build_llm_shapes("block", payload)
    col = shapes["collections"]["payload.development_points[].lists.must_include"]
    assert col["element_kind"] == "object"
    assert col["required_keys"] == ["text"]
    pt_col = shapes["collections"]["payload.development_points[]"]
    assert pt_col.get("status_enum") is not None
    assert pt_col.get("llm_freedom_enum") is not None