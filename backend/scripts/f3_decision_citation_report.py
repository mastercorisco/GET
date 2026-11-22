#!/usr/bin/env python3
"""F3 — contagens de citação de KnowledgeItem decision nos pontos do projecto."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from sqlalchemy import or_, select

from app.deps import get_settings
from app.domain.block.models import DevelopmentPoint
from app.models.baseline import BaselineDocumentCode
from app.models.document import DocumentNode
from app.models.knowledge import KnowledgeDraft, KnowledgeItem
from app.models.project import Project
from app.services.project_service import ProjectError
from app.services.workspace_service import workspace_session


def build_decision_citation_report(session, project_id: str) -> dict:
    project = session.get(Project, project_id)
    if project is None:
        raise ProjectError(f"Projecto {project_id!r} não encontrado.")

    decision_rows = session.execute(
        select(KnowledgeItem, KnowledgeDraft)
        .join(KnowledgeDraft, KnowledgeDraft.item_id == KnowledgeItem.id)
        .where(
            KnowledgeDraft.knowledge_type == "decision",
            KnowledgeDraft.lifecycle == "active",
            or_(
                KnowledgeItem.scope_type == "library",
                (KnowledgeItem.scope_type == "project") & (KnowledgeItem.scope_id == project_id),
            ),
        )
    ).all()
    decisions_by_id = {item.id: {"item_id": item.id, "title": draft.title, "scope_type": item.scope_type} for item, draft in decision_rows}

    citations: dict[str, list[dict]] = defaultdict(list)
    other_ki_refs: dict[str, list[dict]] = defaultdict(list)

    point_rows = session.execute(
        select(DevelopmentPoint, BaselineDocumentCode.display_code)
        .join(DocumentNode, DevelopmentPoint.block_id == DocumentNode.id)
        .outerjoin(
            BaselineDocumentCode,
            BaselineDocumentCode.document_node_id == DocumentNode.id,
        )
        .where(DocumentNode.project_id == project_id)
        .order_by(DevelopmentPoint.sort_order)
    ).all()

    for point, block_code in point_rows:
        lists = json.loads(point.lists_json or "{}")
        for kid in lists.get("knowledge_item_ids") or []:
            cite = {
                "point_id": point.id,
                "point_title": point.title,
                "block_code": block_code,
                "status": point.status,
            }
            if kid in decisions_by_id:
                citations[kid].append(cite)
            elif kid:
                other_ki_refs[kid].append(cite)

    decision_reports: list[dict] = []
    for kid, meta in decisions_by_id.items():
        cites = citations.get(kid, [])
        distinct_points = {c["point_id"] for c in cites}
        distinct_blocks = {c["block_code"] for c in cites if c["block_code"]}
        decision_reports.append(
            {
                **meta,
                "citation_count": len(cites),
                "distinct_point_count": len(distinct_points),
                "distinct_block_count": len(distinct_blocks),
                "f3_criterion_met": len(distinct_points) >= 2,
                "citations": cites,
            }
        )
    decision_reports.sort(key=lambda row: (-row["citation_count"], row["title"]))

    multi = [row for row in decision_reports if row["f3_criterion_met"]]
    uncited = [row for row in decision_reports if row["citation_count"] == 0]

    return {
        "project_id": project_id,
        "decision_count": len(decision_reports),
        "decisions": decision_reports,
        "f3_criterion_met_count": len(multi),
        "uncited_decision_count": len(uncited),
        "f3_pilot_ready": len(multi) >= 1,
        "non_decision_knowledge_refs": [
            {"item_id": kid, "citation_count": len(cites), "citations": cites}
            for kid, cites in sorted(other_ki_refs.items(), key=lambda x: (-len(x[1]), x[0]))
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Relatório F3 — decisões citadas em ≥2 pontos.")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--min-citations", type=int, default=2, help="Aviso se nenhuma decisão atinge N pontos")
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