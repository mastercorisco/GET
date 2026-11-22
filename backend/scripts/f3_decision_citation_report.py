#!/usr/bin/env python3
"""F3 — contagens de citação de KnowledgeItem decision nos pontos do projecto."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from app.deps import get_settings
from app.services.f3_reuse_reports import build_decision_citation_report
from app.services.project_service import ProjectError
from app.services.workspace_service import workspace_session


def main() -> int:
    parser = argparse.ArgumentParser(description="Relatório F3 — decisões citadas em ≥2 pontos.")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    with workspace_session(settings) as (session, _):
        try:
            report = build_decision_citation_report(session, args.project_id)
        except ProjectError as exc:
            print(str(exc), file=sys.stderr)
            return 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Decisões activas: {report['decision_count']}")
        print(f"Critério F3 (≥2 pontos): {report['f3_criterion_met_count']} decisão(ões)")
        for row in report["decisions"]:
            mark = "OK" if row["f3_criterion_met"] else "—"
            print(f"  [{mark}] {row['title'][:60]} — {row['citation_count']} citação(ões)")
        if report["uncited_decision_count"]:
            print(f"Sem citações: {report['uncited_decision_count']}")
        if report["non_decision_knowledge_refs"]:
            print(f"Refs KI não-decision nos pontos: {len(report['non_decision_knowledge_refs'])}")
        print(f"Piloto F3 pronto: {'sim' if report['f3_pilot_ready'] else 'não'}")

    if report["decision_count"] == 0:
        return 3
    if report["f3_criterion_met_count"] < 1:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())