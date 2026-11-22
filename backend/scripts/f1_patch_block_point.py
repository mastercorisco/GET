#!/usr/bin/env python3
"""F1 dry-run: patch mínimo num ponto do bloco (sem LLM)."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from app.services.packages.package_semantic import package_conceptual_warnings
from app.services.packages.validate_strict import PackageValidationError, validate_get_package


def _find_point(pkg: dict, *, point_id: str | None, title_contains: str | None) -> dict:
    points = (pkg.get("payload") or {}).get("development_points") or []
    if point_id:
        for row in points:
            if row.get("id") == point_id:
                return row
        raise SystemExit(f"ERRO: ponto {point_id} não encontrado.")
    if title_contains:
        needle = title_contains.lower()
        for row in points:
            if needle in (row.get("title") or "").lower():
                return row
        raise SystemExit(f"ERRO: nenhum ponto com título contendo {title_contains!r}.")
    raise SystemExit("ERRO: indique --point-id ou --title-contains.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch F1 num GET-PACKAGE bloco.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--point-id", help="UUID development_point")
    parser.add_argument("--title-contains", help="Substring do título do ponto")
    parser.add_argument("--append-guidance", help="String a acrescentar a lists.development_guidance")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    src = args.path.resolve()
    pkg = deepcopy(json.loads(src.read_text(encoding="utf-8")))
    row = _find_point(pkg, point_id=args.point_id, title_contains=args.title_contains)
    if args.append_guidance:
        lists = row.setdefault("lists", {})
        guidance = lists.setdefault("development_guidance", [])
        if not isinstance(guidance, list):
            raise SystemExit("ERRO: development_guidance não é lista.")
        guidance.append(args.append_guidance)
    else:
        raise SystemExit("ERRO: especifique --append-guidance (outras operações: futuras).")

    try:
        validate_get_package(pkg, project_id=args.project_id)
    except PackageValidationError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1

    for line in package_conceptual_warnings(pkg):
        print(f"AVISO: {line}")

    dest = args.out or src.with_name(src.stem + "_f1_grill.json")
    dest.write_text(json.dumps(pkg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: ponto {row.get('id', '')[:8]}… — guidance +1")
    print(f"Escrito: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())