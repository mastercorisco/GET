#!/usr/bin/env python3
"""F2 — detecta avoid_terms do glossário exportado no rascunho MD."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def _collect_avoid_terms(data: dict) -> list[tuple[str, str]]:
    payload = data.get("payload") or {}
    hits: list[tuple[str, str]] = []
    for key in ("library_terms", "project_terms"):
        for row in payload.get(key) or []:
            term = row.get("preferred_term") or row.get("id") or "?"
            for avoid in row.get("avoid_terms") or []:
                if avoid and str(avoid).strip():
                    hits.append((term, str(avoid).strip()))
    for row in payload.get("project_overrides") or []:
        term = row.get("preferred_term") or "override"
        for avoid in row.get("avoid_terms") or []:
            if avoid and str(avoid).strip():
                hits.append((term, str(avoid).strip()))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description="Rever avoid_terms no rascunho.")
    parser.add_argument("--draft", type=Path, required=True)
    parser.add_argument("--terminology-json", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    draft_path = args.draft.resolve()
    term_path = args.terminology_json.resolve()
    if not draft_path.is_file() or not term_path.is_file():
        print("ERRO: ficheiros em falta.", file=sys.stderr)
        return 1

    md = draft_path.read_text(encoding="utf-8").lower()
    data = json.loads(term_path.read_text(encoding="utf-8"))
    rules = _collect_avoid_terms(data)
    violations: list[dict] = []
    for preferred, avoid in rules:
        needle = re.sub(r"\s+", " ", avoid.lower())
        if needle in md:
            violations.append(
                {"preferred_term": preferred, "avoid_term": avoid, "found": True}
            )

    payload = {
        "draft": str(draft_path),
        "avoid_rules": len(rules),
        "violations": violations,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if not rules:
            print("Sem avoid_terms no glossário — nada a verificar.")
        elif not violations:
            print(f"OK: {len(rules)} regra(s) avoid; nenhuma no rascunho.")
        else:
            print(f"AVISO: {len(violations)} avoid_term(s) encontrados no texto:")
            for v in violations:
                print(f"  · {v['avoid_term']!r} (termo {v['preferred_term']!r})")
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())