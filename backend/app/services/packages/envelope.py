from __future__ import annotations

from typing import Any

from app.services.packages.constants import GET_PACKAGE_SCHEMA, SUPPORTED_GET_PACKAGE_VERSION
from app.services.packages.llm_brief import build_llm_brief, format_brief_for_clipboard
from app.services.packages.llm_shapes import build_llm_shapes
from app.services.packages.rules import CANONICAL_RULES, rules_hash


def is_get_package(pkg: dict) -> bool:
    return pkg.get("schema") == GET_PACKAGE_SCHEMA


def wrap_package(
    *,
    scope_kind: str,
    project_id: str,
    fascicle_id: str | None,
    block_id: str | None,
    export_id: str,
    payload: dict[str, Any],
    display_code: str | None = None,
    llm_notes: str | None = None,
) -> dict[str, Any]:
    scope: dict[str, str] = {"kind": scope_kind, "project_id": project_id}
    if scope_kind == "fascicle" and fascicle_id:
        scope["fascicle_id"] = fascicle_id
    if scope_kind == "block" and block_id:
        scope["block_id"] = block_id
    llm_shapes = build_llm_shapes(scope_kind, payload)
    llm_brief = build_llm_brief(
        scope_kind=scope_kind,
        export_id=export_id,
        display_code=display_code,
        user_notes=llm_notes,
    )
    return {
        "schema": GET_PACKAGE_SCHEMA,
        "schema_version": SUPPORTED_GET_PACKAGE_VERSION,
        "scope": scope,
        "rules": list(CANONICAL_RULES),
        "rules_hash": rules_hash(),
        "export_id": export_id,
        "payload": payload,
        "llm_shapes": llm_shapes,
        "llm_brief": llm_brief,
    }


def package_brief_text(pkg: dict[str, Any]) -> str:
    brief = pkg.get("llm_brief")
    if isinstance(brief, dict) and brief.get("suggested_prompt"):
        return str(brief["suggested_prompt"])
    return format_brief_for_clipboard(brief) if isinstance(brief, dict) else ""


def unwrap_fascicle_payload(pkg: dict) -> dict:
    """Return fascicle_roundtrip dict for merge (from GET-PACKAGE or legacy)."""
    if is_get_package(pkg):
        inner = dict(pkg["payload"])
        if pkg.get("export_id"):
            inner["export_id"] = pkg["export_id"]
        return inner
    return pkg


def unwrap_block_payload(pkg: dict) -> dict:
    if is_get_package(pkg):
        return dict(pkg["payload"])
    raise ValueError("Pacote não é GET-PACKAGE.")


def scope_from_package(pkg: dict) -> dict:
    if is_get_package(pkg):
        return dict(pkg.get("scope") or {})
    if pkg.get("package_type") == "fascicle_roundtrip":
        fascicle = pkg.get("fascicle") or {}
        return {
            "kind": "fascicle",
            "project_id": pkg.get("project", {}).get("id", ""),
            "fascicle_id": fascicle.get("id", ""),
        }
    return {}