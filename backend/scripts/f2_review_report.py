#!/usr/bin/env python3
"""F2 — relatório determinístico must_include vs rascunho MD (apoio get-review)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def _must_include_rows(point: dict) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    title = (point.get("title") or "").strip() or point.get("id", "")
    for item in point.get("must_include") or []:
        text = item.get("text") if isinstance(item, dict) else str(item)
        if text:
            out.append((title, text.strip()))
    lists = point.get("lists") or {}
    for item in lists.get("must_include") or []:
        if isinstance(item, dict) and item.get("text"):
            out.append((title, str(item["text"]).strip()))
    return out


def _needle(text: str, min_len: int = 24) -> str:
    t = re.sub(r"\s+", " ", text.strip().lower())
    return t[: min(len(t), max(min_len, 20))]


def main() -> int:
    parser = argparse.ArgumentParser(description="Cobertura must_include no rascunho.")
    parser.add_argument("--draft", type=Path, required=True, help="Markdown redigido")
    parser.add_argument("--block-json", type=Path, required=True, help="F04_B07_*_llm.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    draft_path = args.draft.resolve()
    block_path = args.block_json.resolve()
    if not draft_path.is_file():
        print(f"ERRO: rascunho em falta: {draft_path}", file=sys.stderr)
        return 1
    if not block_path.is_file():
        print(f"ERRO: JSON em falta: {block_path}", file=sys.stderr)
        return 1

    md = draft_path.read_text(encoding="utf-8").lower()
    data = json.loads(block_path.read_text(encoding="utf-8"))
    points = (data.get("preparation") or {}).get("development_points") or []
    rows: list[dict] = []
    for pt in points:
        if pt.get("status") not in ("ready", "approved"):
            continue
        for title, text in _must_include_rows(pt):
            hit = _needle(text) in md
            rows.append({"point": title, "must_include": text, "covered": hit})

    covered = sum(1 for r in rows if r["covered"])
    total = len(rows)
    payload = {
        "draft": str(draft_path),
        "block_json": str(block_path),
        "obligations_total": total,
        "covered": covered,
        "missing": total - covered,
        "rows": rows,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Obrigações must_include: {covered}/{total} encontradas no rascunho.")
        for row in rows:
            mark = "OK" if row["covered"] else "FALTA"
            print(f"  [{mark}] {row['point'][:50]}")
            if not row["covered"]:
                print(f"         → {row['must_include'][:72]}…")
    return 1 if total and covered < total else 0


if __name__ == "__main__":
    raise SystemExit(main())