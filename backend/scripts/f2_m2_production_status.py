#!/usr/bin/env python3
"""F2 — estado M2 produção (ficheiros workspace + summary API + gate opcional)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from app.deps import get_settings
from app.services.export_service import ExportError, latest_llm_generation_export
from app.services.project_summary_service import get_project_summary
from app.services.workspace_service import workspace_session

_SCRIPTS = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Estado piloto M2 no workspace.")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--block", default="F04_B07")
    parser.add_argument("--profile", default="discussion")
    parser.add_argument("--run-gate", action="store_true", help="Executa f2_m2_gate se o rascunho existir")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    block = args.block.upper()

    settings = get_settings()
    summary = get_project_summary(settings, args.project_id)

    with workspace_session(settings) as (_, paths):
        root = paths.root
        redir = root / "redaction" / block
        block_json = redir / f"{block}_{args.profile}_llm.json"
        term_json = redir / f"terminology_{args.profile}_llm.json"
        draft = redir / f"REDACAO-{block}.md"
        outline = redir / f"OUTLINE-{block}.md"

    artefacts = {
        "redaction_dir": str(redir),
        "block_json": block_json.is_file(),
        "terminology_json": term_json.is_file(),
        "draft_md": draft.is_file(),
        "outline_md": outline.is_file(),
    }

    llm_ok = False
    llm_export_id: str | None = None
    try:
        llm = latest_llm_generation_export(settings, args.project_id, profile=args.profile)
        llm_ok = Path(llm.zip_path).is_file()
        llm_export_id = llm.export_id
    except ExportError:
        pass

    gate: dict | None = None
    gate_rc = 0
    if args.run_gate and draft.is_file() and block_json.is_file():
        gate_args = [
            sys.executable,
            str(_SCRIPTS / "f2_m2_gate.py"),
            "--draft",
            str(draft),
            "--block-json",
            str(block_json),
            "--json",
        ]
        if term_json.is_file():
            gate_args += ["--terminology-json", str(term_json)]
        proc = subprocess.run(gate_args, cwd=_SCRIPTS.parent, capture_output=True, text=True)
        gate_rc = proc.returncode
        if proc.stdout.strip():
            try:
                gate = json.loads(proc.stdout)
            except json.JSONDecodeError:
                gate = {"raw": proc.stdout[:500]}

    human_pending = not (
        artefacts["draft_md"]
        and gate is not None
        and gate.get("tooling_ok")
    )

    payload = {
        "project_id": args.project_id,
        "block": block,
        "summary": {
            "latest_llm_export_id": summary.latest_llm_export_id,
            "latest_llm_zip_path": summary.latest_llm_zip_path,
            "points_needs_review": summary.points_needs_review,
        },
        "llm_export_on_disk": llm_ok,
        "llm_export_id": llm_export_id,
        "artefacts": artefacts,
        "gate": gate,
        "m2_production_closed": False,
        "human_next": [] if not human_pending else [
            "Redacção final get-write-spec em REDACAO-*.md",
            "get-review e actualizar micro-F2-piloto-EXECUTION-LOG",
        ],
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"M2 {block} — projecto {args.project_id[:8]}…")
        for key, present in artefacts.items():
            if key == "redaction_dir":
                print(f"  pasta: {present}")
                continue
            mark = "sim" if present else "não"
            print(f"  {key}: {mark}")
        print(f"  GET-LLM disco: {'sim' if llm_ok else 'não'} ({llm_export_id or '—'})")
        if gate is not None:
            print(f"  gate tooling: {'PASS' if gate_rc == 0 else 'FAIL'}")
        if payload["human_next"]:
            print("Pendente:")
            for line in payload["human_next"]:
                print(f"  - {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())