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

from app.services.packages.validate_strict import PackageValidationError, validate_get_package


def conceptual_warnings(pkg: dict) -> list[str]:
    warnings: list[str] = []
    scope = pkg.get("scope") or {}
    kind = scope.get("kind")
    payload = pkg.get("payload") or {}

    if kind == "block":
        pts = payload.get("development_points") or []
        for i, pt in enumerate(pts):
            lists = pt.get("lists") or {}
            for key in ("must_include", "open_questions", "questions_to_answer", "development_guidance"):
                for j, item in enumerate(lists.get(key) or []):
                    if isinstance(item, str):
                        warnings.append(
                            f"block point[{i}].lists.{key}[{j}]: string solta (esperado objecto tipado)."
                        )
        ek = payload.get("editable_knowledge")
        if ek and any(ek.get(b) for b in ("knowledge_items", "decisions", "open_questions")):
            warnings.append(
                "Pacote scope=block mas editable_knowledge preenchido — verificar modo F0."
            )

    if kind == "fascicle":
        inner = payload
        structure = inner.get("structure") or inner.get("document_structure")
        if structure and (inner.get("development_points") or inner.get("block")):
            warnings.append("Fasciculo com estrutura e payload de bloco — risco de modo misto.")

    return warnings


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

    warns = conceptual_warnings(pkg)
    for line in warns:
        print(f"AVISO: {line}")
    if not warns:
        print("OK: sem avisos conceptuais heuristicos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
