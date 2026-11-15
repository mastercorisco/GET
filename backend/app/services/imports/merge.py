from __future__ import annotations

import json
import uuid
from copy import deepcopy

from app.services.imports.constants import EDITABLE_FIELDS
from app.services.imports.package_items import is_temp_new_id, is_uuid, knowledge_items_by_id


def _json_equivalent(a: object, b: object) -> bool:
    return json.dumps(a, sort_keys=True, ensure_ascii=False) == json.dumps(
        b, sort_keys=True, ensure_ascii=False
    )


def _protected_touch(b: dict, c: dict, d: dict) -> bool:
    for key in ("revision", "provenance"):
        if not _json_equivalent(d.get(key), c.get(key)) and not _json_equivalent(d.get(key), b.get(key)):
            return True
    d_states = d.get("states") or {}
    c_states = c.get("states") or {}
    b_states = b.get("states") or {}
    for sub in ("approval", "lifecycle", "maturity"):
        if d_states.get(sub) != c_states.get(sub) and d_states.get(sub) != b_states.get(sub):
            return True
    return False


def _item_has_branch_drift(b: dict | None, c: dict | None) -> bool:
    if b is None or c is None:
        return False
    return not _json_equivalent(b, c)


def _editable_changes(b: dict, c: dict, d: dict) -> dict:
    changes: dict = {}
    for field in EDITABLE_FIELDS:
        b_val = b.get(field)
        c_val = c.get(field)
        d_val = d.get(field)
        if d_val == b_val:
            continue
        changes[field] = {"base": b_val, "current": c_val, "proposed": d_val}
    return changes


def _structure_changes(b_struct: list, c_struct: list, d_struct: list) -> dict:
    b_map = {row["node_id"]: row for row in b_struct if row.get("node_id")}
    c_map = {row["node_id"]: row for row in c_struct if row.get("node_id")}
    d_map = {row["node_id"]: row for row in d_struct if row.get("node_id")}
    changes: dict = {}
    for node_id in set(b_map) | set(c_map) | set(d_map):
        b_row = b_map.get(node_id)
        c_row = c_map.get(node_id)
        d_row = d_map.get(node_id)
        if d_row is None:
            continue
        node_changes: dict = {}
        if d_row.get("title") != (b_row or {}).get("title"):
            node_changes["title"] = {
                "base": (b_row or {}).get("title"),
                "current": (c_row or {}).get("title"),
                "proposed": d_row.get("title"),
            }
        if d_row.get("position") != (b_row or {}).get("position"):
            node_changes["position"] = {
                "base": (b_row or {}).get("position"),
                "current": (c_row or {}).get("position"),
                "proposed": d_row.get("position"),
            }
        if node_changes:
            changes[node_id] = node_changes
    return changes


def build_merge_proposals(
    base_pkg: dict,
    current_pkg: dict,
    returned_pkg: dict,
) -> tuple[list[dict], dict]:
    base_items = knowledge_items_by_id(base_pkg)
    current_items = knowledge_items_by_id(current_pkg)
    returned_items = knowledge_items_by_id(returned_pkg)

    proposals: list[dict] = []
    summary: dict = {"no_op_omissions": [], "quarantined_ids": []}

    for item_id, c_item in current_items.items():
        if item_id not in returned_items:
            summary["no_op_omissions"].append(item_id)

    for item_id, d_item in returned_items.items():
        if is_temp_new_id(item_id):
            proposals.append(
                {
                    "proposal_kind": "create",
                    "target_item_id": item_id,
                    "title": d_item.get("title", item_id),
                    "field_changes": {"full_item": {"proposed": deepcopy(d_item)}},
                    "conflict": False,
                    "protected_touch": _protected_touch({}, {}, d_item),
                }
            )
            continue
        if not is_uuid(item_id):
            summary["quarantined_ids"].append(item_id)
            continue
        b_item = base_items.get(item_id)
        c_item = current_items.get(item_id)
        if b_item is None and c_item is None:
            summary["quarantined_ids"].append(item_id)
            continue
        b_item = b_item or c_item or d_item
        c_item = c_item or b_item
        changes = _editable_changes(b_item, c_item, d_item)
        protected = _protected_touch(b_item, c_item, d_item)
        conflict = _item_has_branch_drift(b_item, c_item) and bool(changes or protected)
        if not changes and not protected:
            continue
        proposals.append(
            {
                "proposal_kind": "update",
                "target_item_id": item_id,
                "title": d_item.get("title", item_id),
                "field_changes": changes if changes else {"_protected_only": {"proposed": "touch"}},
                "conflict": conflict,
                "protected_touch": protected,
            }
        )

    for removal in returned_pkg.get("proposed_removals", []):
        target = removal.get("target_id") or removal.get("item_id") or removal.get("id") or ""
        if not target:
            continue
        proposals.append(
            {
                "proposal_kind": "removal",
                "target_item_id": target,
                "title": removal.get("title") or target,
                "field_changes": {"removal": {"proposed": removal}},
                "conflict": False,
                "protected_touch": True,
            }
        )

    for change in returned_pkg.get("change_summary", []):
        if change.get("change_type") != "removal_proposed":
            continue
        target = change.get("item_id") or change.get("target_id") or ""
        if not target:
            continue
        proposals.append(
            {
                "proposal_kind": "removal",
                "target_item_id": target,
                "title": change.get("title") or target,
                "field_changes": {"removal": {"proposed": change}},
                "conflict": False,
                "protected_touch": True,
            }
        )

    b_struct = base_pkg.get("fascicle", {}).get("structure", [])
    c_struct = current_pkg.get("fascicle", {}).get("structure", [])
    d_struct = returned_pkg.get("fascicle", {}).get("structure", [])
    struct_changes = _structure_changes(b_struct, c_struct, d_struct)
    if struct_changes:
        proposals.append(
            {
                "proposal_kind": "structure",
                "target_item_id": returned_pkg.get("fascicle", {}).get("id", "structure"),
                "title": "Estrutura do fascículo",
                "field_changes": struct_changes,
                "conflict": False,
                "protected_touch": False,
            }
        )

    return proposals, summary


def new_proposal_id() -> str:
    return str(uuid.uuid4())