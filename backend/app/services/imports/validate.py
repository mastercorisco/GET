from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from app.services.export.validator import validate_fascicle
from app.services.imports.constants import SUPPORTED_SCHEMA_VERSION
from app.services.imports.package_items import is_temp_new_id, is_uuid, iter_knowledge_items
from app.services.imports.ingest import IngestError

_REPO_ROOT = Path(__file__).resolve().parents[4]

KNOWLEDGE_SCHEMA = json.loads(
    (_REPO_ROOT / "schemas" / "knowledge-item.schema.json").read_text(encoding="utf-8")
)


def _parse_version(version: str) -> tuple[int, ...]:
    parts: list[int] = []
    for token in version.split("."):
        try:
            parts.append(int(token))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def _knowledge_resolver():
    schema_path = _REPO_ROOT / "schemas" / "knowledge-item.schema.json"
    schema = KNOWLEDGE_SCHEMA
    return jsonschema.RefResolver(
        base_uri=schema_path.as_uri(),
        referrer=schema,
        store={
            "https://eda.local/get/schemas/common.schema.json": json.loads(
                (_REPO_ROOT / "schemas" / "common.schema.json").read_text(encoding="utf-8")
            ),
        },
    )


def validate_package(pkg: dict) -> tuple[list[dict], list[dict]]:
    """Return (staged_items, quarantine_rows). Raises IngestError on fatal errors."""
    if pkg.get("package_type") != "fascicle_roundtrip":
        raise IngestError("Apenas pacotes fascicle_roundtrip são reimportáveis.")
    schema_version = pkg.get("schema_version", "0.0.0")
    if _parse_version(schema_version) > _parse_version(SUPPORTED_SCHEMA_VERSION):
        raise IngestError(f"schema_version {schema_version} não suportada (máx. {SUPPORTED_SCHEMA_VERSION}).")
    fascicle_errors = validate_fascicle(pkg)
    if fascicle_errors:
        raise IngestError(f"Pacote inválido: {fascicle_errors[0]}")

    staged: list[dict] = []
    quarantine: list[dict] = []
    resolver = _knowledge_resolver()

    for index, item in enumerate(iter_knowledge_items(pkg)):
        path = f"knowledge_items[{index}]"
        item_id = item.get("id", "")
        if not is_temp_new_id(item_id) and not is_uuid(item_id):
            quarantine.append(
                {
                    "path": path,
                    "error_code": "INVALID_ID",
                    "message": f"ID inválido: {item_id}",
                    "payload_json": json.dumps(item, ensure_ascii=False),
                }
            )
            continue
        try:
            jsonschema.validate(instance=item, schema=KNOWLEDGE_SCHEMA, resolver=resolver)
        except jsonschema.ValidationError as exc:
            quarantine.append(
                {
                    "path": path,
                    "error_code": "SCHEMA",
                    "message": exc.message,
                    "payload_json": json.dumps(item, ensure_ascii=False),
                }
            )
            continue
        staged.append({"entity_kind": "knowledge_item", "entity_key": item_id, "payload": item})

    structure = pkg.get("fascicle", {}).get("structure", [])
    staged.append(
        {
            "entity_kind": "document_structure",
            "entity_key": pkg.get("fascicle", {}).get("id", "fascicle"),
            "payload": structure,
        }
    )
    return staged, quarantine