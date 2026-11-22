#!/usr/bin/env python3
"""F3/M3 — relatório agregado de reutilização (decisões + referências)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from app.deps import get_settings
from app.services.f3_reuse_reports import build_f3_reuse_report
from app.services.project_service import ProjectError
from app.services.workspace_service import workspace_session


def main() -> int:
    parser = argparse.ArgumentParser(description="Painel F3/M3 — decisões e referências citadas.")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    with workspace_session(settings) as (session, _):
        try:
            report = build_f3_reuse_report(session, args.project_id)
        except ProjectError as exc:
            print(str(exc), file=sys.stderr)
            return 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        d = report["decisions"]
        r = report["references"]
        print(f"Decisões: {d['decision_count']} | F3 OK: {d['f3_criterion_met_count']}")
        print(f"Referências: {r['reference_count']} | M3 OK: {r['m3_criterion_met_count']}")
        print(f"Piloto reutilização: {'sim' if report['reuse_pilot_ready'] else 'não'}")

    if not report["reuse_pilot_ready"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())