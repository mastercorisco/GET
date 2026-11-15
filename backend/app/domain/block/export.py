from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

import jsonschema
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.block.catalogs import exchange_package_schema
from app.domain.block.models import DevelopmentPoint, Premise
from app.domain.block.schemas import PointLists
from app.models.document import DocumentNode
from app.models.knowledge import KnowledgeDraft, KnowledgeItem, KnowledgeRevision
from app.models.reference import Reference
from app.services.document_service import compute_display_codes
from app.services.export.serializer import dumps_deterministic


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_lists(raw: str) -> PointLists:
    try:
        data = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        data = {}
    return PointLists.model_validate(data)


def _origin_level(kind: str) -> str:
    return kind


def premise_to_resolved(row: Premise) -> dict[str, Any]:
    return {
        "id": row.id,
        "statement": row.statement,
        "importance": row.importance,
        "source_type": row.source_type,
        "confidence": row.confidence,
        "origin_level": _origin_level(row.owner_kind),
        "origin_id": row.owner_id,
        "reference_id": row.reference_id,
        "notes": row.notes,
    }


def load_premises(session: Session, owner_kind: str, owner_id: str) -> list[Premise]:
    return list(
        session.scalars(
            select(Premise)
            .where(Premise.owner_kind == owner_kind, Premise.owner_id == owner_id)
            .order_by(Premise.created_at, Premise.id)
        )
    )


def resolved_premises_for_point(
    session: Session,
    project_id: str,
    fascicle_id: str | None,
    block_id: str,
    point_id: str,
) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for kind, oid in (
        ("project", project_id),
        ("fascicle", fascicle_id),
        ("block", block_id),
        ("development_point", point_id),
    ):
        if oid is None:
            continue
        for row in load_premises(session, kind, oid):
            if row.id in seen:
                continue
            seen.add(row.id)
            result.append(premise_to_resolved(row))
    return result


def block_level_premises(
    session: Session,
    project_id: str,
    fascicle_id: str | None,
    block_id: str,
) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for kind, oid in (("project", project_id), ("fascicle", fascicle_id), ("block", block_id)):
        if oid is None:
            continue
        for row in load_premises(session, kind, oid):
            if row.id in seen:
                continue
            seen.add(row.id)
            result.append(premise_to_resolved(row))
    return result


def find_fascicle_id(session: Session, block: DocumentNode) -> str | None:
    current: DocumentNode | None = block
    while current is not None:
        if current.node_type == "fascicle":
            return current.id
        if current.parent_id is None:
            break
        current = session.get(DocumentNode, current.parent_id)
    return None


def _knowledge_snapshot(session: Session, item_id: str) -> dict[str, Any] | None:
    item = session.get(KnowledgeItem, item_id)
    if item is None:
        return None
    rev = session.scalar(
        select(KnowledgeRevision)
        .where(KnowledgeRevision.item_id == item_id)
        .order_by(KnowledgeRevision.revision_num.desc())
        .limit(1)
    )
    if rev is not None:
        return {
            "id": item.id,
            "title": rev.title,
            "content": rev.content_md,
            "knowledge_type": rev.knowledge_type,
            "lifecycle": rev.lifecycle,
            "approval": rev.approval,
        }
    draft = session.get(KnowledgeDraft, item_id)
    if draft is None:
        return {"id": item.id, "title": "", "content": ""}
    return {
        "id": item.id,
        "title": draft.title,
        "content": draft.content_md,
        "knowledge_type": draft.knowledge_type,
        "lifecycle": draft.lifecycle,
        "approval": draft.approval,
    }


def _reference_snapshot(session: Session, ref_id: str) -> dict[str, Any] | None:
    ref = session.get(Reference, ref_id)
    if ref is None:
        return None
    return {"id": ref.id, "title": ref.title, "citation": ref.citation, "notes": ref.notes}


def export_status_for_point(point: DevelopmentPoint, include_draft: bool) -> str | None:
    if point.status == "obsolete":
        return None
    if point.status in ("ready", "approved"):
        return point.status
    if include_draft and point.status in ("draft", "incomplete"):
        if point.title.strip() and point.core_idea.strip():
            return "ready"
    return None


def build_exchange_package(
    session: Session,
    block_id: str,
    *,
    include_draft: bool = False,
    package_id: str | None = None,
    exported_at: str | None = None,
) -> dict[str, Any]:
    block = session.get(DocumentNode, block_id)
    if block is None or block.node_type != "block":
        raise ValueError("Bloco não encontrado.")

    project_id = block.project_id
    fascicle_id = find_fascicle_id(session, block)
    nodes = list(
        session.scalars(select(DocumentNode).where(DocumentNode.project_id == project_id))
    )
    codes = compute_display_codes(nodes)

    try:
        target_output = json.loads(block.target_output_json or "{}")
    except json.JSONDecodeError:
        target_output = {}

    points_db = list(
        session.scalars(
            select(DevelopmentPoint)
            .where(DevelopmentPoint.block_id == block_id)
            .order_by(DevelopmentPoint.sort_order, DevelopmentPoint.id)
        )
    )

    export_points: list[dict[str, Any]] = []
    all_ki_ids: set[str] = set()
    all_ref_ids: set[str] = set()
    all_examples: list[dict[str, Any]] = []
    all_open_questions: list[dict[str, Any]] = []
    missing_information: list[str] = []

    for point in points_db:
        export_status = export_status_for_point(point, include_draft)
        if export_status is None:
            continue
        lists = _parse_lists(point.lists_json)
        premises = resolved_premises_for_point(
            session, project_id, fascicle_id, block_id, point.id
        )
        export_points.append(
            {
                "id": point.id,
                "order": point.sort_order,
                "title": point.title,
                "core_idea": point.core_idea,
                "intended_outcome": point.intended_outcome or "",
                "development_guidance": lists.development_guidance,
                "perspectives": lists.perspectives,
                "questions_to_answer": lists.questions_to_answer,
                "premises": premises,
                "must_include": lists.must_include,
                "limits_and_exclusions": lists.limits_and_exclusions,
                "examples": lists.examples,
                "knowledge_item_ids": sorted(set(lists.knowledge_item_ids)),
                "reference_ids": sorted(set(lists.reference_ids)),
                "open_questions": lists.open_questions,
                "acceptance_criteria": lists.acceptance_criteria,
                "llm_freedom": point.llm_freedom,
                "status": export_status,
            }
        )
        all_ki_ids.update(lists.knowledge_item_ids)
        all_ref_ids.update(lists.reference_ids)
        all_examples.extend(lists.examples)
        all_open_questions.extend(lists.open_questions)
        if point.needs_review:
            missing_information.append(
                f"Ponto {point.sort_order} ({point.title or point.id}) requer revisão após alteração aprovada."
            )

    knowledge_items = []
    for kid in sorted(all_ki_ids):
        snap = _knowledge_snapshot(session, kid)
        if snap:
            knowledge_items.append(snap)

    references = []
    for rid in sorted(all_ref_ids):
        snap = _reference_snapshot(session, rid)
        if snap:
            references.append(snap)

    package = {
        "schema_version": "1.0.0",
        "package_id": package_id or str(uuid.uuid4()),
        "exported_at": exported_at or _utcnow_iso(),
        "scope": {
            "project_id": project_id,
            "fascicle_id": fascicle_id or block_id,
            "block_id": block_id,
            "display_code": codes.get(block_id, ""),
            "title": block.title,
        },
        "authoritative_content": {
            "block": {
                "objective": block.objective or "",
                "scope": block.scope or "",
                "target_output": target_output if isinstance(target_output, dict) else {},
            },
            "applicable_premises": block_level_premises(session, project_id, fascicle_id, block_id),
            "development_points": export_points,
        },
        "supporting_context": {
            "knowledge_items": knowledge_items,
            "references": references,
            "examples": all_examples,
        },
        "unresolved_matters": {
            "open_questions": all_open_questions,
            "missing_information": missing_information,
        },
        "generation_instructions": {
            "develop_each_point": True,
            "preserve_point_order": True,
            "do_not_invent_requirements": True,
            "do_not_resolve_open_questions": True,
            "identify_suggestions_separately": True,
            "output_language": "pt-PT",
            "additional_instructions": [
                "Não inventar requisitos nem resolver silenciosamente lacunas.",
                "Apresentar sugestões separadas do conteúdo autoritativo.",
            ],
        },
    }
    schema = exchange_package_schema()
    if schema:
        jsonschema.validate(instance=package, schema=schema)
    return package


def deterministic_exchange_json(
    session: Session,
    block_id: str,
    *,
    include_draft: bool = False,
) -> str:
    package = build_exchange_package(
        session,
        block_id,
        include_draft=include_draft,
        package_id="deterministic-package-id",
        exported_at="2000-01-01T00:00:00+00:00",
    )
    return dumps_deterministic(package)