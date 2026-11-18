#!/usr/bin/env python3
"""Compila catalogs/ctbj_document_structure_v3.pt-PT.json a partir do inventário Markdown."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND = REPO_ROOT / "backend"
DEFAULT_MD = REPO_ROOT / "docs" / "inventory" / "ctbj_structure_v3.inventory.md"
DEFAULT_JSON = REPO_ROOT / "catalogs" / "ctbj_document_structure_v3.pt-PT.json"

EXPECTED_FASCICLES = 20
EXPECTED_BLOCKS = 179
EXPECTED_POINTS = 869

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.structure_seed.ctbj_parser import (  # noqa: E402
    _strip_period,
    parse_ctbj_v3_inventory,
)


def _catalog_dict(parsed, source_path: Path, complements: list[dict]) -> dict:
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
        fascicles.append(
            {
                "code": f.code,
                "ordinal": f.ordinal,
                "title": f.title,
                "blocks": blocks,
            }
        )
    body: dict = {
        "id": "ctbj_v3",
        "version": 3,
        "locale": "pt-PT",
        "source": str(source_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "complements": complements,
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
    parser = argparse.ArgumentParser(description="Compilar catálogo CTBJ v3.")
    parser.add_argument("--input", type=Path, default=DEFAULT_MD)
    parser.add_argument("--output", type=Path, default=DEFAULT_JSON)
    args = parser.parse_args()

    if not args.input.is_file():
        print(f"Ficheiro em falta: {args.input}", file=sys.stderr)
        return 2

    text = args.input.read_text(encoding="utf-8")
    parsed = parse_ctbj_v3_inventory(text)
    errors: list[str] = []
    if parsed.fascicle_count != EXPECTED_FASCICLES:
        errors.append(f"fascículos: esperado {EXPECTED_FASCICLES}, obtido {parsed.fascicle_count}")
    if parsed.block_count != EXPECTED_BLOCKS:
        errors.append(f"blocos: esperado {EXPECTED_BLOCKS}, obtido {parsed.block_count}")
    if parsed.point_count != EXPECTED_POINTS:
        errors.append(f"pontos: esperado {EXPECTED_POINTS}, obtido {parsed.point_count}")

    complements = []
    for rule in parsed.complements:
        complements.append(
            {
                "target_block_codes": rule.target_block_codes,
                "target_fascicle_code": rule.target_fascicle_code,
                "replace": rule.replace,
                "development_points": [_strip_period(t) for t in rule.development_points],
            }
        )

    catalog = _catalog_dict(parsed, args.input, complements)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        f"Escrito {args.output} — "
        f"{parsed.fascicle_count}/{parsed.block_count}/{parsed.point_count} "
        f"checksum={catalog['checksum'][:12]}…"
    )
    if errors:
        for err in errors:
            print(f"AVISO: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())