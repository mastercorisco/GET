"""SSOT: deriva tipos de listas e vocabulário do GET-PACKAGE a partir de get_package.schema.json."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[4]
_SCHEMA_PATH = _REPO_ROOT / "schemas" / "get_package.schema.json"


def repo_schema_path() -> Path:
    return _SCHEMA_PATH


@lru_cache
def load_get_package_schema() -> dict[str, Any]:
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


def _resolve_ref(schema: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/$defs/"):
        msg = f"Referência não suportada: {ref}"
        raise ValueError(msg)
    name = ref.rsplit("/", 1)[-1]
    defn = schema.get("$defs", {}).get(name)
    if not isinstance(defn, dict):
        msg = f"$defs.{name} em falta"
        raise ValueError(msg)
    return defn


def point_list_keys(schema: dict[str, Any] | None = None) -> tuple[str, ...]:
    sch = schema or load_get_package_schema()
    point_lists = sch["$defs"]["pointLists"]
    required = point_lists.get("required")
    if isinstance(required, list) and required:
        return tuple(required)
    return tuple(point_lists.get("properties", {}).keys())


def point_list_shapes(schema: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    """Materializa POINT_LIST_SHAPES (element_kind, required_keys, item_template, …)."""
    sch = schema or load_get_package_schema()
    point_lists = sch["$defs"]["pointLists"]
    props = point_lists.get("properties") or {}
    shapes: dict[str, dict[str, Any]] = {}
    for key, prop in props.items():
        shapes[key] = _shape_for_list_property(prop, sch)
    return shapes


def _shape_for_list_property(prop: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    xget = dict(prop.get("x-get") or {})
    items = prop.get("items") or {}
    element_kind = xget.get("element_kind")
    required_keys: list[str] | None = None
    item_template: Any = xget.get("item_template")

    if isinstance(items.get("$ref"), str):
        defn = _resolve_ref(schema, items["$ref"])
        if element_kind is None:
            element_kind = "object"
        req = defn.get("required")
        if isinstance(req, list):
            required_keys = list(req)
        if item_template is None and required_keys:
            item_template = {k: "" for k in required_keys}
    elif items.get("type") == "string":
        if element_kind is None:
            element_kind = "string"
        if item_template is None:
            item_template = ""

    out: dict[str, Any] = {
        "element_kind": element_kind or "string",
        "creatable": bool(xget.get("creatable", True)),
        "id_policy": xget.get("id_policy"),
        "item_template": item_template,
    }
    if required_keys:
        out["required_keys"] = required_keys
    return out


def development_point_field_enums(schema: dict[str, Any] | None = None) -> dict[str, list[str]]:
    sch = schema or load_get_package_schema()
    props = sch["$defs"]["developmentPoint"].get("properties") or {}
    out: dict[str, list[str]] = {}
    for field in ("status", "llm_freedom"):
        enum = props.get(field, {}).get("enum")
        if isinstance(enum, list):
            out[field] = list(enum)
    return out


def premise_field_enums(schema: dict[str, Any] | None = None) -> dict[str, list[str]]:
    sch = schema or load_get_package_schema()
    props = sch["$defs"]["premise"].get("properties") or {}
    out: dict[str, list[str]] = {}
    for field in ("importance", "source_type", "confidence"):
        enum = props.get(field, {}).get("enum")
        if isinstance(enum, list):
            out[field] = list(enum)
    return out


def list_schema_examples(schema: dict[str, Any] | None = None) -> dict[str, Any]:
    """Exemplos estáticos do schema (fallback quando export não tem sample)."""
    sch = schema or load_get_package_schema()
    props = sch["$defs"]["pointLists"].get("properties") or {}
    examples: dict[str, Any] = {}
    for key, prop in props.items():
        ex = prop.get("examples")
        if ex:
            examples[key] = ex[0] if isinstance(ex, list) else ex
        items = prop.get("items") or {}
        if isinstance(items.get("$ref"), str):
            defn = _resolve_ref(sch, items["$ref"])
            def_ex = defn.get("examples")
            if def_ex and key not in examples:
                examples[key] = def_ex[0] if isinstance(def_ex, list) else def_ex
    return examples