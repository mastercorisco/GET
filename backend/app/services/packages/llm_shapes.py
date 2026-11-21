from __future__ import annotations

import copy
from typing import Any

from app.domain.block.models import DEFAULT_LISTS_JSON
from app.services.packages.block_merge import BLOCK_EDITABLE, POINT_EDITABLE, PREMISE_EDITABLE
from app.services.packages.package_guidance import COLLECTION_PRIORITY, PACKAGE_ANTI_PATTERNS
from app.services.packages.schema_shapes import (
    development_point_field_enums,
    point_list_keys,
    point_list_shapes,
    premise_field_enums,
)

_STRICT_INSTRUCTION = (
    "Cumprir estritamente os tipos definidos em llm_shapes. Não inferir estruturas não especificadas."
)

POINT_LIST_KEYS: tuple[str, ...] = point_list_keys()
_POINT_LIST_KEYS = POINT_LIST_KEYS

# Gerado a partir de schemas/get_package.schema.json ($defs/pointLists + x-get).
POINT_LIST_SHAPES: dict[str, dict[str, Any]] = point_list_shapes()

NEW_KNOWLEDGE_ITEM_TEMPLATE: dict[str, Any] = {
    "id": "new_001",
    "code": None,
    "aliases": [],
    "title": "",
    "content": "",
    "rationale": None,
    "notes": None,
    "knowledge_type": "unclassified",
    "revision": 1,
    "states": {
        "maturity": "captured",
        "approval": "proposed",
        "lifecycle": "active",
    },
    "scope": {
        "scope_type": "project",
        "scope_id": "00000000-0000-4000-8000-000000000000",
    },
    "technical_profile": None,
    "relations": [],
    "provenance": {
        "origin_type": "llm_return",
        "origin_id": None,
        "created_by": "external_llm",
        "created_at": "1970-01-01T00:00:00+00:00",
        "source_reference_ids": [],
        "source_export_id": None,
        "source_import_id": None,
    },
    "edit_policy": {
        "mode": "propose_changes",
        "protected_fields": [
            "id",
            "revision",
            "states.approval",
            "states.lifecycle",
            "provenance",
        ],
        "editable_fields": ["title", "content", "rationale", "notes", "relations"],
        "allow_new_items": True,
        "allow_removal_proposals": True,
    },
}

KI_FORBIDDEN_SHORTHAND = frozenset({"node_id", "question"})

KNOWLEDGE_TYPE_ENUM = [
    "fact",
    "principle",
    "requirement",
    "decision",
    "rationale",
    "example",
    "recommendation",
    "open_question",
    "exclusion",
    "authoring_instruction",
    "unclassified",
]


def normalize_point_lists(lists: dict | None) -> dict[str, Any]:
    default = __import__("json").loads(DEFAULT_LISTS_JSON)
    if not isinstance(lists, dict):
        lists = {}
    return {**default, **lists}


def _collection_entry(
    path: str,
    shape: dict[str, Any],
    *,
    sample: Any | None = None,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "path": path,
        "element_kind": shape["element_kind"],
        "creatable": shape.get("creatable", True),
    }
    if shape.get("id_policy"):
        entry["id_policy"] = shape["id_policy"]
    if shape.get("required_keys"):
        entry["required_keys"] = list(shape["required_keys"])
    if sample is not None:
        entry["sample_from_export"] = sample
    else:
        entry["item_template"] = copy.deepcopy(shape.get("item_template"))
    return entry


def build_llm_shapes(scope_kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    collections: dict[str, dict[str, Any]] = {}

    if scope_kind == "block":
        for key in _POINT_LIST_KEYS:
            shape = POINT_LIST_SHAPES[key]
            sample = None
            for pt in payload.get("development_points") or []:
                lists = pt.get("lists") or {}
                rows = lists.get(key)
                if isinstance(rows, list) and rows:
                    sample = copy.deepcopy(rows[0])
                    break
            collections[f"payload.development_points[].lists.{key}"] = _collection_entry(
                f"payload.development_points[].lists.{key}",
                shape,
                sample=sample,
            )
        pt_enums = development_point_field_enums()
        collections["payload.development_points[]"] = {
            "path": "payload.development_points[]",
            "element_kind": "object",
            "creatable": True,
            "id_policy": "uuid_preserve_or_new_temp",
            "required_keys": [
                "id",
                "sort_order",
                "title",
                "core_idea",
                "intended_outcome",
                "lists",
                "status",
                "llm_freedom",
            ],
            "editable_fields": sorted(POINT_EDITABLE),
            "status_enum": pt_enums.get("status"),
            "llm_freedom_enum": pt_enums.get("llm_freedom"),
            "item_template": {
                "id": "new_001",
                "sort_order": 1,
                "title": "",
                "core_idea": "",
                "intended_outcome": "",
                "lists": __import__("json").loads(DEFAULT_LISTS_JSON),
                "status": "draft",
                "llm_freedom": "bounded",
                "template_id": None,
                "needs_review": False,
            },
        }
        prem_enums = premise_field_enums()
        collections["payload.premises[]"] = {
            "path": "payload.premises[]",
            "element_kind": "object",
            "creatable": True,
            "id_policy": "uuid_preserve_or_new_temp",
            "required_keys": ["id", "statement", "importance", "source_type", "confidence"],
            "editable_fields": sorted(PREMISE_EDITABLE),
            "importance_enum": prem_enums.get("importance"),
            "source_type_enum": prem_enums.get("source_type"),
            "confidence_enum": prem_enums.get("confidence"),
            "item_template": {
                "id": "new_001",
                "statement": "",
                "importance": "recommended",
                "source_type": "technical_recommendation",
                "confidence": "provisional",
                "reference_id": None,
                "notes": None,
            },
        }
        collections["payload.block"] = {
            "path": "payload.block",
            "element_kind": "object",
            "creatable": False,
            "editable_fields": sorted(BLOCK_EDITABLE),
        }
    elif scope_kind == "fascicle":
        editable = payload.get("editable_knowledge") or {}
        for bucket in ("knowledge_items", "decisions", "open_questions"):
            path = f"payload.editable_knowledge.{bucket}"
            rows = editable.get(bucket) or []
            sample = copy.deepcopy(rows[0]) if rows else None
            if sample is None:
                protected = (payload.get("protected_context") or {}).get("knowledge_items") or []
                if protected:
                    sample = copy.deepcopy(protected[0])
                    entry_note = "Forma de referência (protected_context); novos itens em editable_knowledge."
                else:
                    entry_note = None
            else:
                entry_note = None
            entry = {
                "path": path,
                "element_kind": "object",
                "creatable": True,
                "id_policy": "uuid_preserve_or_new_temp",
                "schema": "knowledge-item.schema.json",
                "required_keys": [
                    "id",
                    "title",
                    "content",
                    "knowledge_type",
                    "revision",
                    "states",
                    "provenance",
                    "edit_policy",
                ],
                "knowledge_type_enum": KNOWLEDGE_TYPE_ENUM,
                "forbidden_fields": sorted(KI_FORBIDDEN_SHORTHAND),
            }
            if sample is not None and rows:
                entry["sample_from_export"] = sample
            elif sample is not None and not rows and entry_note:
                entry["sample_from_export"] = sample
                entry["note"] = entry_note
            else:
                tpl = copy.deepcopy(NEW_KNOWLEDGE_ITEM_TEMPLATE)
                if bucket == "open_questions":
                    tpl["knowledge_type"] = "open_question"
                elif bucket == "decisions":
                    tpl["knowledge_type"] = "decision"
                entry["item_template"] = tpl
            collections[path] = entry

        protected = (payload.get("protected_context") or {}).get("knowledge_items") or []
        if protected:
            collections["payload.protected_context.knowledge_items[]"] = {
                "path": "payload.protected_context.knowledge_items[]",
                "element_kind": "object",
                "creatable": False,
                "id_policy": "uuid_preserve",
                "note": "Alterações só nos campos em edit_policy.editable_fields.",
                "sample_from_export": copy.deepcopy(protected[0]),
            }

    return {
        "version": "1",
        "scope_kind": scope_kind,
        "instructions": [_STRICT_INSTRUCTION],
        "collection_priority": COLLECTION_PRIORITY,
        "anti_patterns": list(PACKAGE_ANTI_PATTERNS),
        "collections": collections,
    }


def validate_block_point_lists(payload: dict[str, Any]) -> None:
    """Validação extra das listas de pontos (tipos de elemento)."""
    from app.services.packages.validate_strict import PackageValidationError

    for pi, pt in enumerate(payload.get("development_points") or []):
        lists = pt.get("lists")
        if lists is None:
            continue
        if not isinstance(lists, dict):
            raise PackageValidationError(f"Ficheiro incompatível: ponto [{pi}] lists deve ser objeto.")
        for key in POINT_LIST_KEYS:
            if key not in lists:
                raise PackageValidationError(
                    f"Ficheiro incompatível: ponto [{pi}] lists em falta a chave «{key}»."
                )
        for key, shape in POINT_LIST_SHAPES.items():
            rows = lists[key]
            if not isinstance(rows, list):
                raise PackageValidationError(f"Ficheiro incompatível: ponto [{pi}] lists.{key} deve ser array.")
            kind = shape["element_kind"]
            for ri, row in enumerate(rows):
                if kind == "string":
                    if not isinstance(row, str):
                        raise PackageValidationError(
                            f"Ficheiro incompatível: ponto [{pi}] lists.{key}[{ri}] deve ser string."
                        )
                elif kind == "object":
                    if not isinstance(row, dict):
                        raise PackageValidationError(
                            f"Ficheiro incompatível: ponto [{pi}] lists.{key}[{ri}] deve ser objeto."
                        )
                    for req in shape.get("required_keys") or []:
                        if req not in row:
                            raise PackageValidationError(
                                f"Ficheiro incompatível: ponto [{pi}] lists.{key}[{ri}] falta «{req}»."
                            )