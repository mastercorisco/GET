from __future__ import annotations

import json
from pathlib import Path

import jsonschema

_REPO_ROOT = Path(__file__).resolve().parents[4]


def _load_schema() -> dict:
    schema_path = _REPO_ROOT / "schemas" / "get_llm_export.schema.json"
    return json.loads(schema_path.read_text(encoding="utf-8"))


def validate_llm_export(instance: dict) -> list[str]:
    schema = _load_schema()
    try:
        jsonschema.validate(instance=instance, schema=schema)
        return []
    except jsonschema.ValidationError as exc:
        return [exc.message]