from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from app.services.export.validator import validate_fascicle
from app.services.packages.constants import GET_PACKAGE_SCHEMA, SUPPORTED_GET_PACKAGE_VERSION
from app.services.packages.llm_shapes import validate_block_point_lists
from app.services.packages.rules import rules_hash


class PackageValidationError(Exception):
    pass


_REPO_ROOT = Path(__file__).resolve().parents[4]


def _parse_version(version: str) -> tuple[int, ...]:
    parts: list[int] = []
    for token in version.split("."):
        try:
            parts.append(int(token))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def _schema_resolver() -> jsonschema.RefResolver:
    schema_path = _REPO_ROOT / "schemas" / "get_package.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    store = {
        "https://eda.local/get/schemas/common.schema.json": json.loads(
            (_REPO_ROOT / "schemas/common.schema.json").read_text(encoding="utf-8")
        ),
        "https://eda.local/get/schemas/knowledge-item.schema.json": json.loads(
            (_REPO_ROOT / "schemas/knowledge-item.schema.json").read_text(encoding="utf-8")
        ),
        "https://eda.local/get/schemas/fascicle-roundtrip.schema.json": json.loads(
            (_REPO_ROOT / "schemas/fascicle-roundtrip.schema.json").read_text(encoding="utf-8")
        ),
    }
    return jsonschema.RefResolver(base_uri=schema_path.as_uri(), referrer=schema, store=store)


def validate_get_package(pkg: dict, *, project_id: str) -> None:
    if pkg.get("schema") != GET_PACKAGE_SCHEMA:
        raise PackageValidationError("Ficheiro incompatível: não é um pacote GET-PACKAGE.")
    version = pkg.get("schema_version", "0.0.0")
    if _parse_version(version) > _parse_version(SUPPORTED_GET_PACKAGE_VERSION):
        raise PackageValidationError(
            f"Ficheiro incompatível: versão {version} não suportada (máx. {SUPPORTED_GET_PACKAGE_VERSION})."
        )
    if pkg.get("rules_hash") != rules_hash():
        raise PackageValidationError("Ficheiro incompatível: regras do pacote foram alteradas.")
    rules = pkg.get("rules")
    if not isinstance(rules, list) or len(rules) != 7:
        raise PackageValidationError("Ficheiro incompatível: lista de regras inválida.")
    scope = pkg.get("scope") or {}
    if scope.get("project_id") != project_id:
        raise PackageValidationError("Ficheiro incompatível: o pacote pertence a outro projecto.")
    kind = scope.get("kind")
    if kind not in ("fascicle", "block"):
        raise PackageValidationError("Ficheiro incompatível: âmbito inválido.")

    resolver = _schema_resolver()
    schema_path = _REPO_ROOT / "schemas" / "get_package.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(instance=pkg, schema=schema, resolver=resolver)
    except jsonschema.ValidationError as exc:
        raise PackageValidationError(f"Ficheiro incompatível: {exc.message}") from exc

    payload = pkg.get("payload")
    if not isinstance(payload, dict):
        raise PackageValidationError("Ficheiro incompatível: payload em falta.")

    if kind == "fascicle":
        inner = dict(payload)
        if pkg.get("export_id"):
            inner["export_id"] = pkg["export_id"]
        fascicle_errors = validate_fascicle(inner)
        if fascicle_errors:
            raise PackageValidationError(f"Ficheiro incompatível: {fascicle_errors[0]}")
        if scope.get("fascicle_id") != (payload.get("fascicle") or {}).get("id"):
            raise PackageValidationError("Ficheiro incompatível: fascículo do âmbito não coincide.")
        ki_resolver = jsonschema.RefResolver(
            base_uri=(_REPO_ROOT / "schemas/knowledge-item.schema.json").as_uri(),
            referrer=json.loads((_REPO_ROOT / "schemas/knowledge-item.schema.json").read_text(encoding="utf-8")),
            store={
                "https://eda.local/get/schemas/common.schema.json": json.loads(
                    (_REPO_ROOT / "schemas/common.schema.json").read_text(encoding="utf-8")
                ),
            },
        )
        from app.services.imports.package_items import is_temp_new_id, is_uuid, iter_knowledge_items

        ki_schema = json.loads((_REPO_ROOT / "schemas/knowledge-item.schema.json").read_text(encoding="utf-8"))
        roundtrip = inner
        for index, item in enumerate(iter_knowledge_items(roundtrip)):
            item_id = item.get("id", "")
            if not is_temp_new_id(item_id) and not is_uuid(item_id):
                raise PackageValidationError(f"Ficheiro incompatível: ID inválido em conhecimento [{index}].")
            try:
                jsonschema.validate(instance=item, schema=ki_schema, resolver=ki_resolver)
            except jsonschema.ValidationError as exc:
                raise PackageValidationError(f"Ficheiro incompatível: conhecimento [{index}]: {exc.message}") from exc
    elif kind == "block":
        block_id = scope.get("block_id")
        block = payload.get("block") or {}
        if block_id != block.get("id"):
            raise PackageValidationError("Ficheiro incompatível: bloco do âmbito não coincide.")
        validate_block_point_lists(payload)