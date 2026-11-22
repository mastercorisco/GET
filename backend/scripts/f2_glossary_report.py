#!/usr/bin/env python3
"""F2 — detecta avoid_terms e avoid_in_project do glossário no rascunho MD."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def _collect_rules(data: dict) -> list[dict]:
    payload = data.get("payload") or {}
    rules: list[dict] = []
    for key in ("library_terms", "project_terms"):
        for row in payload.get(key) or []:
            preferred = row.get("preferred_term") or row.get("id") or "?"
            for avoid in row.get("avoid_terms") or []:
                if avoid and str(avoid).strip():
                    rules.append(
                        {
                            "kind": "avoid_term",
                            "preferred_term": preferred,
                            "needle": str(avoid).strip(),
                        }
                    )
    for row in payload.get("project_overrides") or []:
        if not row.get("avoid_in_project"):
            continue
        preferred = (row.get("preferred_term") or "").strip()
        if preferred:
            rules.append(
                {
                    "kind": "avoid_in_project",
                    "preferred_term": preferred,
                    "legacy_term": row.get("legacy_term"),
                    "needle": preferred,
                }
            )
    return rules


def main() -> int:
    parser = argparse.ArgumentParser(description="Rever glossário no rascunho.")
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
    rules = _collect_rules(data)
    violations: list[dict] = []
    for rule in rules:
        needle = re.sub(r"\s+", " ", rule["needle"].lower())
        if needle in md:
            violations.append({**rule, "found": True})

    payload = {
        "draft": str(draft_path),
        "rule_count": len(rules),
        "violations": violations,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if not rules:
            print("Sem regras avoid no glossário — nada a verificar.")
        elif not violations:
            print(f"OK: {len(rules)} regra(s); nenhuma violação no rascunho.")
        else:
            print(f"AVISO: {len(violations)} violação(ões) linguísticas:")
            for v in violations:
                if v["kind"] == "avoid_in_project":
                    leg = v.get("legacy_term") or "—"
                    print(f"  · preferido «{v['preferred_term']}» (usar legado: {leg})")
                else:
                    print(f"  · {v['needle']!r} (termo {v['preferred_term']!r})")
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())