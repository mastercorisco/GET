"""F3/M3 — relatórios read-only de reutilização (decisões, referências)."""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from sqlalchemy import or_, select

from app.domain.block.models import DevelopmentPoint
from app.models.baseline import BaselineDocumentCode
from app.models.document import DocumentNode
from app.models.knowledge import KnowledgeDraft, KnowledgeItem
from app.models.project import Project
from app.models.reference import Reference
from app.services.project_service import ProjectError


def _require_project(session, project_id: str) -> Project:
    project = session.get(Project, project_id)
    if project is None:
        raise ProjectError(f"Projecto {project_id!r} não encontrado.")
    return project


def iter_project_points(session, project_id: str) -> list[tuple[DevelopmentPoint, str | None]]:
    rows = session.execute(
        select(DevelopmentPoint, BaselineDocumentCode.display_code)
        .join(DocumentNode, DevelopmentPoint.block_id == DocumentNode.id)
        .outerjoin(
            BaselineDocumentCode,
            BaselineDocumentCode.document_node_id == DocumentNode.id,
        )
        .where(DocumentNode.project_id == project_id)
        .order_by(DevelopmentPoint.sort_order)
    ).all()
    return list(rows)


def build_decision_citation_report(session, project_id: str) -> dict[str, Any]:
    _require_project(session, project_id)

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
    decisions_by_id = {
        item.id: {"item_id": item.id, "title": draft.title, "scope_type": item.scope_type}
        for item, draft in decision_rows
    }

    citations: dict[str, list[dict]] = defaultdict(list)
    other_ki_refs: dict[str, list[dict]] = defaultdict(list)

    for point, block_code in iter_project_points(session, project_id):
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


def build_reference_citation_report(session, project_id: str) -> dict[str, Any]:
    _require_project(session, project_id)

    ref_rows = session.scalars(
        select(Reference).where(
            or_(
                Reference.scope_type == "library",
                (Reference.scope_type == "project") & (Reference.scope_id == project_id),
            )
        )
    ).all()
    refs_by_id = {
        ref.id: {
            "reference_id": ref.id,
            "title": ref.title,
            "scope_type": ref.scope_type,
            "citation": ref.citation,
        }
        for ref in ref_rows
    }

    citations: dict[str, list[dict]] = defaultdict(list)
    unknown_refs: dict[str, list[dict]] = defaultdict(list)

    for point, block_code in iter_project_points(session, project_id):
        lists = json.loads(point.lists_json or "{}")
        for ref_id in lists.get("reference_ids") or []:
            cite = {
                "point_id": point.id,
                "point_title": point.title,
                "block_code": block_code,
                "status": point.status,
            }
            if ref_id in refs_by_id:
                citations[ref_id].append(cite)
            elif ref_id:
                unknown_refs[ref_id].append(cite)

    reference_reports: list[dict] = []
    for rid, meta in refs_by_id.items():
        cites = citations.get(rid, [])
        distinct_points = {c["point_id"] for c in cites}
        distinct_blocks = {c["block_code"] for c in cites if c["block_code"]}
        reference_reports.append(
            {
                **meta,
                "citation_count": len(cites),
                "distinct_point_count": len(distinct_points),
                "distinct_block_count": len(distinct_blocks),
                "m3_criterion_met": len(distinct_points) >= 2,
                "citations": cites,
            }
        )
    reference_reports.sort(key=lambda row: (-row["citation_count"], row["title"]))

    multi = [row for row in reference_reports if row["m3_criterion_met"]]
    uncited = [row for row in reference_reports if row["citation_count"] == 0]

    return {
        "project_id": project_id,
        "reference_count": len(reference_reports),
        "references": reference_reports,
        "m3_criterion_met_count": len(multi),
        "uncited_reference_count": len(uncited),
        "m3_reuse_ready": len(multi) >= 1,
        "unknown_reference_ids": [
            {"reference_id": rid, "citation_count": len(cites), "citations": cites}
            for rid, cites in sorted(unknown_refs.items(), key=lambda x: (-len(x[1]), x[0]))
        ],
    }


def build_f3_reuse_report(session, project_id: str) -> dict[str, Any]:
    decisions = build_decision_citation_report(session, project_id)
    references = build_reference_citation_report(session, project_id)
    return {
        "project_id": project_id,
        "decisions": decisions,
        "references": references,
        "f3_pilot_ready": decisions["f3_pilot_ready"],
        "m3_reuse_ready": references["m3_reuse_ready"],
        "reuse_pilot_ready": decisions["f3_pilot_ready"] or references["m3_reuse_ready"],
    }