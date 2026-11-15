from __future__ import annotations

import json
from pathlib import Path

import jsonschema

_REPO_ROOT = Path(__file__).resolve().parents[4]


def _resolver(schema_name: str) -> jsonschema.RefResolver:
    schema_path = _REPO_ROOT / "schemas" / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    return jsonschema.RefResolver(
        base_uri=schema_path.as_uri(),
        referrer=schema,
        store={
            "https://eda.local/get/schemas/common.schema.json": json.loads(
                (_REPO_ROOT / "schemas/common.schema.json").read_text(encoding="utf-8")
            ),
            "https://eda.local/get/schemas/knowledge-item.schema.json": json.loads(
                (_REPO_ROOT / "schemas/knowledge-item.schema.json").read_text(encoding="utf-8")
            ),
        },
    )


def validate_master(instance: dict) -> list[str]:
    schema_path = _REPO_ROOT / "schemas" / "master.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(instance=instance, schema=schema, resolver=_resolver("master.schema.json"))
        return []
    except jsonschema.ValidationError as exc:
        return [exc.message]


def validate_fascicle(instance: dict) -> list[str]:
    schema_path = _REPO_ROOT / "schemas" / "fascicle-roundtrip.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(
            instance=instance,
            schema=schema,
            resolver=_resolver("fascicle-roundtrip.schema.json"),
        )
        return []
    except jsonschema.ValidationError as exc:
        return [exc.message]