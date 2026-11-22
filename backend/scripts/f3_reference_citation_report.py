#!/usr/bin/env python3
"""M3 — contagens de reference_ids reutilizados em ≥2 pontos."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from app.deps import get_settings
from app.services.f3_reuse_reports import build_reference_citation_report
from app.services.project_service import ProjectError
from app.services.workspace_service import workspace_session


def main() -> int:
    parser = argparse.ArgumentParser(description="Relatório M3/F3 — referências citadas em ≥2 pontos.")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    with workspace_session(settings) as (session, _):
        try:
            report = build_reference_citation_report(session, args.project_id)
        except ProjectError as exc:
            print(str(exc), file=sys.stderr)
            return 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Referências no âmbito: {report['reference_count']}")
        print(f"Critério M3 (≥2 pontos): {report['m3_criterion_met_count']} referência(s)")
        for row in report["references"]:
            mark = "OK" if row["m3_criterion_met"] else "—"
            print(f"  [{mark}] {row['title'][:60]} — {row['citation_count']} citação(ões)")
        if report["uncited_reference_count"]:
            print(f"Sem citações nos pontos: {report['uncited_reference_count']}")
        if report["unknown_reference_ids"]:
            print(f"IDs desconhecidos nos pontos: {len(report['unknown_reference_ids'])}")
        print(f"Reutilização M3 pronta: {'sim' if report['m3_reuse_ready'] else 'não'}")

    if report["reference_count"] == 0:
        return 3
    if report["m3_criterion_met_count"] < 1:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())