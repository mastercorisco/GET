#!/usr/bin/env python3
"""Validacao offline de um ficheiro GET-PACKAGE (F0 checklist pre-import)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from app.services.packages.package_semantic import package_conceptual_warnings
from app.services.packages.validate_strict import PackageValidationError, validate_get_package


def main() -> int:
    parser = argparse.ArgumentParser(description="Validar ficheiro GET-PACKAGE antes de importar (F0).")
    parser.add_argument("path", type=Path)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--warnings-only", action="store_true")
    args = parser.parse_args()

    path = args.path.resolve()
    if not path.is_file():
        print(f"ERRO: ficheiro nao encontrado: {path}", file=sys.stderr)
        return 2

    try:
        pkg = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERRO: JSON ilegivel: {exc}", file=sys.stderr)
        return 2

    if not args.warnings_only:
        try:
            validate_get_package(pkg, project_id=args.project_id)
        except PackageValidationError as exc:
            print(f"ERRO validacao: {exc}", file=sys.stderr)
            return 1
        print("OK: validacao estrita GET-PACKAGE passou.")

    warns = package_conceptual_warnings(pkg)
    for line in warns:
        print(f"AVISO: {line}")
    if not warns:
        print("OK: sem avisos conceptuais heuristicos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())