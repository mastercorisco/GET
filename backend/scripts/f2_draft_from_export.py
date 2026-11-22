#!/usr/bin/env python3
"""F2 dry-run: rascunho MD a partir do export bloco (must_include integrados; não reimportável)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def _must_include_rows(point: dict) -> list[str]:
    rows: list[str] = []
    for item in point.get("must_include") or []:
        if isinstance(item, dict) and item.get("text"):
            rows.append(str(item["text"]))
    lists = point.get("lists") or {}
    for item in lists.get("must_include") or []:
        if isinstance(item, dict) and item.get("text"):
            rows.append(str(item["text"]))
    return rows


def _build_draft(data: dict, block_code: str) -> str:
    block = data.get("block") or {}
    points = (data.get("preparation") or {}).get("development_points") or []
    lines = [
        f"# Redação piloto — {block_code}",
        "",
        f"**Capítulo / bloco:** {block.get('title', '')}",
        "",
        "_Artefacto F2 (fora do GET). Revisão: get-review + f2_review_report._",
        "",
    ]
    for pt in points:
        if pt.get("status") not in ("ready", "approved"):
            continue
        title = (pt.get("title") or "").strip()
        lines.append(f"## {title}")
        lines.append("")
        core = (pt.get("core_idea") or "").strip()
        if core:
            lines.append(core)
            lines.append("")
        outcome = (pt.get("intended_outcome") or "").strip()
        if outcome and outcome != core:
            lines.append(outcome)
            lines.append("")
        must = _must_include_rows(pt)
        if must:
            lines.append("O texto do caderno deve reflectir, entre outros, os seguintes elementos obrigatórios:")
            lines.append("")
            for row in must:
                lines.append(f"- {row}")
            lines.append("")
            lines.append(
                "Em síntese: " + " ".join(row.rstrip(".") + "." for row in must[:2])
                + (" " + must[2] if len(must) > 2 else "")
            )
            lines.append("")
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Gerar rascunho MD M2 (dry-run get-write-spec).")
    parser.add_argument("block_json", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--block", default="", help="Código para cabeçalho (predef.: nome do ficheiro)")
    args = parser.parse_args()

    src = args.block_json.resolve()
    if not src.is_file():
        print(f"ERRO: {src}", file=sys.stderr)
        return 1
    data = json.loads(src.read_text(encoding="utf-8"))
    code = args.block or src.stem.replace("_discussion_llm", "").replace("_writing_llm", "")
    text = _build_draft(data, code)
    dest = args.out or src.with_name(f"REDACAO-{code}.md")
    dest.write_text(text, encoding="utf-8")
    print(f"Escrito: {dest} ({len(text)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())