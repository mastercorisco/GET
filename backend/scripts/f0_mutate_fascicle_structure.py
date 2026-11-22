#!/usr/bin/env python3
"""F0-structure dry-run: altera só title numa linha de fascicle.structure (para teste sem LLM)."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from copy import deepcopy
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from app.services.packages.package_semantic import package_conceptual_warnings
from app.services.packages.validate_strict import PackageValidationError, validate_get_package


def _find_structure_row(pkg: dict, *, node_id: str | None, display_code: str | None) -> dict:
    inner = pkg.get("payload") or pkg
    fascicle = inner.get("fascicle") or {}
    structure = fascicle.get("structure") or []
    if node_id:
        for row in structure:
            if row.get("node_id") == node_id:
                return row
        raise SystemExit(f"ERRO: node_id {node_id} não está em fascicle.structure")
    if display_code:
        for row in structure:
            if (row.get("display_code") or "").upper() == display_code.upper():
                return row
        raise SystemExit(f"ERRO: display_code {display_code!r} não está em fascicle.structure")
    raise SystemExit("ERRO: indique --node-id ou --display-code")


def main() -> int:
    parser = argparse.ArgumentParser(description="Mutar título estrutural num GET-PACKAGE fascículo (F0).")
    parser.add_argument("path", type=Path, help="JSON GET-PACKAGE (ex. F01_package.json)")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--display-code", help="Código do nó (ex. F01_B01)")
    parser.add_argument("--node-id", help="UUID document_node")
    parser.add_argument("--title", required=True, help="Novo título")
    parser.add_argument(
        "--out",
        type=Path,
        help="Ficheiro de saída (default: <origem>_f0_structure.json ao lado)",
    )
    parser.add_argument("--in-place", action="store_true", help="Substituir o ficheiro (cria .bak)")
    args = parser.parse_args()

    src = args.path.resolve()
    if not src.is_file():
        print(f"ERRO: não encontrado: {src}", file=sys.stderr)
        return 2

    pkg = json.loads(src.read_text(encoding="utf-8"))
    pkg = deepcopy(pkg)
    row = _find_structure_row(pkg, node_id=args.node_id, display_code=args.display_code)
    old = row.get("title", "")
    row["title"] = args.title

    try:
        validate_get_package(pkg, project_id=args.project_id)
    except PackageValidationError as exc:
        print(f"ERRO validação: {exc}", file=sys.stderr)
        return 1

    for line in package_conceptual_warnings(pkg):
        print(f"AVISO: {line}")

    if args.in_place:
        backup = src.with_suffix(src.suffix + ".bak")
        shutil.copy2(src, backup)
        dest = src
        print(f"Backup: {backup}")
    else:
        dest = args.out or src.with_name(src.stem + "_f0_structure.json")

    dest.write_text(json.dumps(pkg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    code = row.get("display_code") or row.get("node_id", "")[:8]
    print(f"OK: {code!r} title {old!r} -> {args.title!r}")
    print(f"Escrito: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())