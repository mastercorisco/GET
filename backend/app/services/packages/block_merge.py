from __future__ import annotations

import json
import re
from copy import deepcopy
from typing import Any

_TEMP_ID = re.compile(r"^new_\d{3,}$", re.I)

BLOCK_EDITABLE = frozenset({"objective", "scope", "target_output", "title"})
POINT_EDITABLE = frozenset({"title", "core_idea", "intended_outcome", "lists"})
PREMISE_EDITABLE = frozenset({"statement", "notes"})


def _json_eq(a: object, b: object) -> bool:
    return json.dumps(a, sort_keys=True, ensure_ascii=False) == json.dumps(
        b, sort_keys=True, ensure_ascii=False
    )


def _field_delta(b: object, c: object, d: object) -> dict | None:
    if _json_eq(d, b):
        return None
    return {"base": b, "current": c, "proposed": d}


def _by_id(rows: list[dict], key: str = "id") -> dict[str, dict]:
    return {row[key]: row for row in rows if row.get(key)}


def build_block_merge_proposals(
    base: dict[str, Any],
    current: dict[str, Any],
    returned: dict[str, Any],
) -> tuple[list[dict], dict]:
    proposals: list[dict] = []
    summary: dict = {
        "no_op_omissions": [],
        "skipped_already_in_db": [],
        "unchanged_vs_export_base": [],
    }

    b_block = base.get("block") or {}
    c_block = current.get("block") or {}
    d_block = returned.get("block") or {}
    for field in BLOCK_EDITABLE:
        delta = _field_delta(b_block.get(field), c_block.get(field), d_block.get(field))
        if delta and not _json_eq(delta.get("proposed"), c_block.get(field)):
            proposals.append(
                {
                    "proposal_kind": "block_field",
                    "target_item_id": d_block.get("id", "block"),
                    "title": f"Bloco: {field}",
                    "field_changes": {field: delta},
                    "conflict": not _json_eq(b_block.get(field), c_block.get(field)),
                    "protected_touch": False,
                }
            )

    b_points = _by_id(base.get("development_points") or [])
    c_points = _by_id(current.get("development_points") or [])
    d_points = _by_id(returned.get("development_points") or [])

    for pid in c_points:
        if pid not in d_points:
            summary["no_op_omissions"].append(pid)

    for pid, d_row in d_points.items():
        if _TEMP_ID.match(pid):
            proposals.append(
                {
                    "proposal_kind": "point_create",
                    "target_item_id": pid,
                    "title": f"Ponto: {d_row.get('title', pid)}",
                    "field_changes": {"full_point": {"proposed": deepcopy(d_row)}},
                    "conflict": False,
                    "protected_touch": False,
                }
            )
            continue
        b_row = b_points.get(pid, c_points.get(pid, {}))
        c_row = c_points.get(pid, b_row)
        changes: dict = {}
        had_delta_vs_base = False
        for field in POINT_EDITABLE:
            delta = _field_delta(b_row.get(field), c_row.get(field), d_row.get(field))
            if delta:
                had_delta_vs_base = True
            if delta and not _json_eq(delta.get("proposed"), c_row.get(field)):
                changes[field] = delta
        if not changes:
            if had_delta_vs_base:
                summary["skipped_already_in_db"].append(pid)
            else:
                summary["unchanged_vs_export_base"].append(pid)
            continue
        # Metadados do ponto (status, sort_order, …) não são aplicados na consolidação — só campos editáveis.
        proposals.append(
            {
                "proposal_kind": "point_update",
                "target_item_id": pid,
                "title": f"Ponto: {d_row.get('title', pid)}",
                "field_changes": changes,
                "conflict": not _json_eq(
                    {k: b_row.get(k) for k in POINT_EDITABLE},
                    {k: c_row.get(k) for k in POINT_EDITABLE},
                ),
                "protected_touch": False,
            }
        )

    b_pre = _by_id(base.get("premises") or [])
    c_pre = _by_id(current.get("premises") or [])
    d_pre = _by_id(returned.get("premises") or [])

    for pid in c_pre:
        if pid not in d_pre:
            summary["no_op_omissions"].append(pid)

    for pid, d_row in d_pre.items():
        if _TEMP_ID.match(pid):
            proposals.append(
                {
                    "proposal_kind": "premise_create",
                    "target_item_id": pid,
                    "title": f"Premissa: {d_row.get('statement', pid)[:60]}",
                    "field_changes": {"full_premise": {"proposed": deepcopy(d_row)}},
                    "conflict": False,
                    "protected_touch": False,
                }
            )
            continue
        b_row = b_pre.get(pid, c_pre.get(pid, {}))
        c_row = c_pre.get(pid, b_row)
        changes = {}
        for field in PREMISE_EDITABLE:
            delta = _field_delta(b_row.get(field), c_row.get(field), d_row.get(field))
            if delta and not _json_eq(delta.get("proposed"), c_row.get(field)):
                changes[field] = delta
        if not changes:
            continue
        proposals.append(
            {
                "proposal_kind": "premise_update",
                "target_item_id": pid,
                "title": f"Premissa: {d_row.get('statement', pid)[:60]}",
                "field_changes": changes,
                "conflict": not _json_eq(b_row, c_row),
                "protected_touch": False,
            }
        )

    return proposals, summary