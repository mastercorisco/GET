from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
CATALOG_DIR = REPO_ROOT / "catalogs"
SCHEMA_DIR = REPO_ROOT / "schemas"

_HELP_CACHE: dict | None = None
_TEMPLATE_CACHE: dict | None = None
_SCHEMA_CACHE: dict | None = None


def _load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def help_catalog() -> dict:
    global _HELP_CACHE
    if _HELP_CACHE is None:
        data = _load_json(CATALOG_DIR / "get_help_catalog.pt-PT.json")
        _HELP_CACHE = data if data else {"fields": {}, "default_help_level": "normal"}
    return _HELP_CACHE


def field_help(field_key: str) -> dict:
    fields = help_catalog().get("fields") or {}
    entry = fields.get(field_key)
    if entry:
        return entry
    return {
        "label": field_key,
        "short_help": "Ajuda não disponível para este campo.",
    }


def development_point_templates() -> dict:
    global _TEMPLATE_CACHE
    if _TEMPLATE_CACHE is None:
        data = _load_json(CATALOG_DIR / "development_point_templates.pt-PT.json")
        _TEMPLATE_CACHE = data if data else {"templates": []}
    return _TEMPLATE_CACHE


def template_by_id(template_id: str) -> dict | None:
    for row in development_point_templates().get("templates", []):
        if row.get("id") == template_id:
            return row
    return None


def exchange_package_schema() -> dict:
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE is None:
        _SCHEMA_CACHE = _load_json(SCHEMA_DIR / "get_exchange_package.schema.json")
    return _SCHEMA_CACHE