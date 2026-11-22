#!/usr/bin/env python3
"""F2 — workflow M2: materialize → draft (opcional) → gate."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent


def _run(script: str, args: list[str]) -> int:
    proc = subprocess.run(
        [sys.executable, str(_SCRIPTS / script), *args],
        cwd=_SCRIPTS.parent,
    )
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Cadeia M2 após export GET-LLM.")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--block", default="F04_B07")
    parser.add_argument("--profile", default="discussion")
    parser.add_argument("--draft-from-export", action="store_true", help="Gera REDACAO-*.md (dry-run)")
    parser.add_argument("--skip-gate", action="store_true")
    args = parser.parse_args()

    rc = _run(
        "f2_m2_materialize.py",
        [
            "--project-id",
            args.project_id,
            "--block",
            args.block,
            "--profile",
            args.profile,
            "--outline",
        ],
    )
    if rc:
        return rc

    redir = Path(f"redaction/{args.block.upper()}")
    block_json = redir / f"{args.block.upper()}_{args.profile}_llm.json"
    draft = redir / f"REDACAO-{args.block.upper()}.md"
    term_json = redir / f"terminology_{args.profile}_llm.json"

    if args.draft_from_export:
        if not block_json.is_file():
            print(f"ERRO: {block_json} em falta — execute desde a raiz do workspace.", file=sys.stderr)
            return 1
        rc = _run(
            "f2_draft_from_export.py",
            [str(block_json), "--out", str(draft), "--block", args.block.upper()],
        )
        if rc:
            return rc

    if args.skip_gate or not draft.is_file():
        print("Materialização concluída. Preencha o rascunho e execute f2_m2_gate.py.")
        return 0

    gate_args = [
        "--draft",
        str(draft),
        "--block-json",
        str(block_json),
    ]
    if term_json.is_file():
        gate_args += ["--terminology-json", str(term_json)]
    return _run("f2_m2_gate.py", gate_args)


if __name__ == "__main__":
    raise SystemExit(main())