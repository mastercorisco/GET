#!/usr/bin/env python3
"""Macro — painel offline M2 artefactos + F3/M3 reutilização (sem MCP)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from app.deps import get_settings
from app.services.export_service import ExportError, latest_llm_generation_export
from app.services.f3_reuse_reports import build_f3_reuse_report
from app.services.project_service import ProjectError
from app.services.project_summary_service import get_project_summary
from app.services.workspace_service import workspace_session


def main() -> int:
    parser = argparse.ArgumentParser(description="Estado piloto macro (M2 ficheiros + F3/M3).")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--block", default="F04_B07")
    parser.add_argument("--profile", default="discussion")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    block = args.block.upper()

    settings = get_settings()
    summary = get_project_summary(settings, args.project_id)

    with workspace_session(settings) as (session, paths):
        try:
            reuse = build_f3_reuse_report(session, args.project_id)
        except ProjectError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        redir = paths.root / "redaction" / block
        artefacts = {
            "redaction_dir": str(redir),
            "block_json": (redir / f"{block}_{args.profile}_llm.json").is_file(),
            "draft_md": (redir / f"REDACAO-{block}.md").is_file(),
            "outline_md": (redir / f"OUTLINE-{block}.md").is_file(),
        }

    llm_ok = False
    try:
        llm = latest_llm_generation_export(settings, args.project_id, profile=args.profile)
        llm_ok = Path(llm.zip_path).is_file()
    except ExportError:
        pass

    payload = {
        "project_id": args.project_id,
        "block": block,
        "summary": summary.model_dump(),
        "llm_zip_on_disk": llm_ok,
        "m2_redaction": artefacts,
        "m2_production_closed": False,
        "f3_m3": reuse,
        "mcp_allowed": False,
        "next_human": [
            "M2: REDACAO final + get-review (micro-F2-M2-production-checklist)",
            "F3/M3: decisão ou Reference em ≥2 pontos (f3_reuse_report)",
        ],
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    else:
        print(f"Macro piloto — {block}")
        print(f"  GET-LLM disco: {'sim' if llm_ok else 'não'}")
        print(f"  REDACAO MD: {'sim' if artefacts['draft_md'] else 'não'}")
        print(f"  F3 decisões OK: {reuse['decisions']['f3_criterion_met_count']}")
        print(f"  M3 referências OK: {reuse['references']['m3_criterion_met_count']}")
        print("  MCP: bloqueado até M2 produção")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())