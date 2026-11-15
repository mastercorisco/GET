from __future__ import annotations

import re

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.I,
)


def is_temp_new_id(item_id: str) -> bool:
    return item_id.startswith("new_")


def is_uuid(item_id: str) -> bool:
    return bool(_UUID_RE.match(item_id))


def iter_knowledge_items(pkg: dict) -> list[dict]:
    items: list[dict] = []
    seen: set[str] = set()
    protected = pkg.get("protected_context", {}).get("knowledge_items", [])
    for row in protected:
        item_id = row.get("id")
        if item_id and item_id not in seen:
            seen.add(item_id)
            items.append(row)
    editable = pkg.get("editable_knowledge", {})
    for key in ("knowledge_items", "decisions", "open_questions"):
        for row in editable.get(key, []):
            item_id = row.get("id")
            if item_id and item_id not in seen:
                seen.add(item_id)
                items.append(row)
    return items


def knowledge_items_by_id(pkg: dict) -> dict[str, dict]:
    return {row["id"]: row for row in iter_knowledge_items(pkg) if row.get("id")}