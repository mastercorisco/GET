#!/usr/bin/env python3
"""Compila catalogs/*.json a partir de inventário Markdown genérico."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND = REPO_ROOT / "backend"
DEFAULT_MD = REPO_ROOT / "docs" / "inventory" / "structure_catalog_generic_example.inventory.md"
DEFAULT_JSON = REPO_ROOT / "catalogs" / "structure_catalog_generic_example.pt-PT.json"

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.structure_seed.generic_inventory_parser import parse_generic_structure_inventory  # noqa: E402


def _catalog_dict(
    parsed,
    *,
    catalog_id: str,
    version: int,
    source_path: Path,
    display_name: str,
) -> dict:
    fascicles = []
    for f in parsed.fascicles:
        blocks = []
        for b in f.blocks:
            blocks.append(
                {
                    "code": b.code,
                    "ordinal": b.ordinal,
                    "title": b.title,
                    "development_points": [{"text": p.text} for p in b.development_points],
                }
            )
        row = {
            "code": f.code,
            "ordinal": f.ordinal,
            "title": f.title,
            "blocks": blocks,
        }
        if f.purpose:
            row["purpose"] = f.purpose
        fascicles.append(row)

    body: dict = {
        "id": catalog_id,
        "version": version,
        "locale": "pt-PT",
        "display_name": display_name,
        "source": str(source_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "complements": [],
        "fascicles": fascicles,
        "totals": {
            "fascicles": parsed.fascicle_count,
            "blocks": parsed.block_count,
            "development_points": parsed.point_count,
        },
    }
    canonical = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    body["checksum"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return body


def main() -> int:
    parser = argparse.ArgumentParser(description="Compilar catálogo de estrutura GET.")
    parser.add_argument("--input", type=Path, default=DEFAULT_MD)
    parser.add_argument("--output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--id", default="generic_example_v1")
    parser.add_argument("--version", type=int, default=1)
    parser.add_argument("--display-name", default="Estrutura documental genérica (exemplo)")
    args = parser.parse_args()

    if not args.input.is_file():
        print(f"Ficheiro em falta: {args.input}", file=sys.stderr)
        return 2

    text = args.input.read_text(encoding="utf-8")
    parsed = parse_generic_structure_inventory(text)
    body = _catalog_dict(
        parsed,
        catalog_id=args.id,
        version=args.version,
        source_path=args.input,
        display_name=args.display_name,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK {args.output} — {body['totals']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())