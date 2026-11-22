#!/usr/bin/env python3
"""F2 — gate M2: must_include + glossário + checklist T2.0 (read-only)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_SCRIPTS = Path(__file__).resolve().parent


def _run(script: str, args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(_SCRIPTS / script), *args],
        cwd=_SCRIPTS.parent,
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    parser = argparse.ArgumentParser(description="Gate piloto M2 / pré-T2.0")
    parser.add_argument("--draft", type=Path, required=True)
    parser.add_argument("--block-json", type=Path, required=True)
    parser.add_argument("--terminology-json", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    checks: list[dict] = []
    rc_must, out_must = _run(
        "f2_review_report.py",
        ["--draft", str(args.draft.resolve()), "--block-json", str(args.block_json.resolve())],
    )
    checks.append({"id": "must_include", "ok": rc_must == 0, "detail": out_must.strip()[:500]})

    rc_gloss = 0
    gloss_detail = "omitido"
    if args.terminology_json and args.terminology_json.is_file():
        rc_gloss, gloss_detail = _run(
            "f2_glossary_report.py",
            [
                "--draft",
                str(args.draft.resolve()),
                "--terminology-json",
                str(args.terminology_json.resolve()),
            ],
        )
        checks.append({"id": "glossary_avoid", "ok": rc_gloss == 0, "detail": gloss_detail.strip()[:500]})

    tooling_ok = all(c["ok"] for c in checks)
    t2_gate = {
        "m2_tooling_dry_run": tooling_ok,
        "m2_production_redacao": "pendente (humano)",
        "m2_get_package_review": "pendente se necessário",
        "t2_mcp_code_unblocked": False,
    }

    payload = {"checks": checks, "tooling_ok": tooling_ok, "t2_readiness": t2_gate}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for c in checks:
            mark = "OK" if c["ok"] else "FALHA"
            print(f"[{mark}] {c['id']}")
        print(f"Tooling M2: {'PASS' if tooling_ok else 'FAIL'}")
        print("T2.0 MCP: bloqueado até M2 produção fechado em GET_MACRO_PLAN.")
    return 0 if tooling_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())