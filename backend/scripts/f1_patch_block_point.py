#!/usr/bin/env python3
"""F1 dry-run: patch num ou vários pontos do bloco (sem LLM)."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

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


def _text_object(text: str) -> dict[str, str]:
    return {"text": text}


def _append_list_objects(lst: list, items: list[Any]) -> None:
    for item in items:
        if isinstance(item, str):
            lst.append(_text_object(item))
        elif isinstance(item, dict):
            lst.append(item)
        else:
            raise SystemExit(f"ERRO: item de lista inválido: {item!r}")


def _append_strings(lst: list, items: list[Any]) -> None:
    for item in items:
        if not isinstance(item, str):
            raise SystemExit(f"ERRO: esperava string em lista de guidance: {item!r}")
        lst.append(item)


def _apply_patch(row: dict, patch: dict) -> list[str]:
    """Aplica um patch a um ponto; devolve resumo de alterações."""
    notes: list[str] = []
    lists = row.setdefault("lists", {})
    if patch.get("core_idea"):
        row["core_idea"] = patch["core_idea"]
        notes.append("core_idea")
    if patch.get("intended_outcome"):
        row["intended_outcome"] = patch["intended_outcome"]
        notes.append("intended_outcome")
    for key, use_strings in (
        ("development_guidance", True),
        ("must_include", False),
        ("open_questions", False),
        ("limits_and_exclusions", False),
        ("acceptance_criteria", True),
        ("questions_to_answer", True),
    ):
        if key not in patch:
            continue
        target = lists.setdefault(key, [])
        if not isinstance(target, list):
            raise SystemExit(f"ERRO: lists.{key} não é lista.")
        items = patch[key]
        if not isinstance(items, list):
            raise SystemExit(f"ERRO: patch {key} deve ser lista.")
        if use_strings:
            _append_strings(target, items)
        else:
            _append_list_objects(target, items)
        notes.append(f"{key}+{len(items)}")
    for single, list_key, use_strings in (
        ("append_guidance", "development_guidance", True),
        ("append_must_include", "must_include", False),
        ("append_open_question", "open_questions", False),
    ):
        val = patch.get(single)
        if val is None or val == "":
            continue
        target = lists.setdefault(list_key, [])
        if use_strings:
            items = val if isinstance(val, list) else [val]
            _append_strings(target, items)
        else:
            items = val if isinstance(val, list) else [val]
            _append_list_objects(target, items)
        notes.append(single)
    return notes


def _load_patches(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit("ERRO: ficheiro --patches deve ser JSON array.")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch F1 num GET-PACKAGE bloco.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--point-id", help="UUID development_point (modo ponto único)")
    parser.add_argument("--title-contains", help="Substring do título (modo ponto único)")
    parser.add_argument("--append-guidance", help="Acrescentar development_guidance (ponto único)")
    parser.add_argument(
        "--patches",
        type=Path,
        help="JSON array: [{title_contains|point_id, append_* …}, …]",
    )
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    src = args.path.resolve()
    pkg = deepcopy(json.loads(src.read_text(encoding="utf-8")))
    applied: list[str] = []

    if args.patches:
        for patch in _load_patches(args.patches):
            pid = patch.get("point_id")
            title = patch.get("title_contains")
            if not pid and not title:
                raise SystemExit("ERRO: cada patch precisa point_id ou title_contains.")
            row = _find_point(pkg, point_id=pid, title_contains=title)
            notes = _apply_patch(row, patch)
            applied.append(f"{row.get('id', '')[:8]}… ({', '.join(notes) or 'noop'})")
    else:
        row = _find_point(pkg, point_id=args.point_id, title_contains=args.title_contains)
        if args.append_guidance:
            notes = _apply_patch(row, {"append_guidance": args.append_guidance})
            applied.append(f"{row.get('id', '')[:8]}… ({', '.join(notes)})")
        else:
            raise SystemExit("ERRO: especifique --append-guidance ou --patches.")

    try:
        validate_get_package(pkg, project_id=args.project_id)
    except PackageValidationError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1

    for line in package_conceptual_warnings(pkg):
        print(f"AVISO: {line}")

    dest = args.out or src.with_name(src.stem + "_f1_grill.json")
    dest.write_text(json.dumps(pkg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for line in applied:
        print(f"OK: ponto {line}")
    print(f"Escrito: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())