"""Importa get_help_editorial.pt-PT.json para get_help_catalog.pt-PT.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "catalogs" / "get_help_catalog.pt-PT.json"
EDITORIAL = ROOT / "catalogs" / "get_help_editorial.pt-PT.json"

FIELD_MERGE = (
    "label",
    "short_help",
    "definition",
    "guiding_question",
    "instructions",
    "purpose_in_app",
    "workflow_context",
    "when_to_use",
    "what_happens_next",
    "common_confusions",
    "tips",
    "good_examples",
    "bad_examples",
)


def _bump_patch(version: str) -> str:
    parts = version.split(".")
    if len(parts) != 3:
        return version
    parts[2] = str(int(parts[2]) + 1)
    return ".".join(parts)


def main() -> None:
    path = EDITORIAL
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    if not path.is_file():
        raise SystemExit(f"Não encontrado: {path}")

    editorial = json.loads(path.read_text(encoding="utf-8"))
    if editorial.get("document_type") != "get_help_editorial":
        raise SystemExit("document_type inválido; esperado get_help_editorial")

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    fields_ed = editorial.get("fields") or {}

    for key, wrap in fields_ed.items():
        if key not in catalog["fields"]:
            catalog["fields"][key] = {"label": key, "short_help": "", "definition": ""}
        entry = catalog["fields"][key]
        editable = wrap.get("editable") if isinstance(wrap, dict) and "editable" in wrap else wrap
        if not isinstance(editable, dict):
            continue
        for f in FIELD_MERGE:
            if f in editable and editable[f] is not None:
                entry[f] = editable[f]
        protected = wrap.get("protected") or {}
        for pk, pv in protected.items():
            if pv is not None:
                entry[pk] = pv

    if editorial.get("concepts"):
        catalog["concepts"] = editorial["concepts"]
    if editorial.get("method"):
        catalog["method"] = editorial["method"]
    if editorial.get("screens"):
        for sid, patch in editorial["screens"].items():
            catalog.setdefault("screens", {})
            catalog["screens"].setdefault(sid, {})
            catalog["screens"][sid].update(patch)
    if editorial.get("workflows"):
        catalog["workflows"] = editorial["workflows"]

    old_v = catalog.get("catalog_version", "1.3.0")
    catalog["catalog_version"] = _bump_patch(old_v)
    catalog["_editorial_imported_at"] = editorial.get("exported_at")
    catalog.pop("_schema_note", None)

    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Updated", CATALOG, "version", catalog["catalog_version"])


if __name__ == "__main__":
    main()