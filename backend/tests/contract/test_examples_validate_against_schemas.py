from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize(
    "example_name,schema_name",
    [
        ("master.example.json", "master.schema.json"),
        ("fascicle-roundtrip.example.json", "fascicle-roundtrip.schema.json"),
        ("exchange-package.example.json", "get_exchange_package.schema.json"),
        ("llm-block-export.example.json", "get_llm_export.schema.json"),
    ],
)
def test_examples_validate(example_name: str, schema_name: str) -> None:
    schema_path = REPO_ROOT / "schemas" / schema_name
    example_path = REPO_ROOT / "examples" / example_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    instance = json.loads(example_path.read_text(encoding="utf-8"))
    resolver = jsonschema.RefResolver(
        base_uri=schema_path.as_uri(),
        referrer=schema,
        store={
            "https://eda.local/get/schemas/common.schema.json": json.loads(
                (REPO_ROOT / "schemas/common.schema.json").read_text(encoding="utf-8")
            ),
            "https://eda.local/get/schemas/knowledge-item.schema.json": json.loads(
                (REPO_ROOT / "schemas/knowledge-item.schema.json").read_text(encoding="utf-8")
            ),
        },
    )
    jsonschema.validate(instance=instance, schema=schema, resolver=resolver)