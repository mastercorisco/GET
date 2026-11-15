#!/usr/bin/env python3
"""Inventário rápido de um workbook GET (cabeçalhos L4 + contagens)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND = REPO_ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.workbook.constants import DATA_SHEETS, DEFAULT_WORKBOOK  # noqa: E402
from app.services.workbook.extract import extract_workbook  # noqa: E402
from app.services.workbook.mapping import mapping_document  # noqa: E402
from app.services.workbook.reader import WorkbookReader  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", type=Path, default=Path(DEFAULT_WORKBOOK))
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()
    path = args.workbook.resolve()
    if not path.is_file():
        print(f"Ficheiro não encontrado: {path}", file=sys.stderr)
        return 1

    reader = WorkbookReader(path)
    inventory: dict = {"workbook": str(path), "sheets": [], "mapping": mapping_document()}
    try:
        for name in reader.sheet_names():
            headers = reader.header_row(name) if name in DATA_SHEETS or name.startswith("00_") else []
            row_count = 0
            if name in DATA_SHEETS:
                row_count = sum(1 for _ in reader.iter_data_rows(name))
            inventory["sheets"].append(
                {"name": name, "header_row_4": headers, "data_rows": row_count}
            )
    finally:
        reader.close()

    bundle, issues = extract_workbook(path)
    if bundle:
        inventory["extract_counts"] = {
            "fascicles": len(bundle.fascicles),
            "blocks": len(bundle.blocks),
            "principles": len(bundle.principles),
            "artefacts": len(bundle.artefacts),
            "a01_rows": len(bundle.a01_rows),
            "references": len(bundle.references),
        }
    inventory["issues"] = [i.as_dict() for i in issues]

    text = json.dumps(inventory, ensure_ascii=False, indent=2)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text, encoding="utf-8")
        print(f"Escrito: {args.json_out}")
    else:
        print(text)
    return 1 if any(i.severity == "error" for i in issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())