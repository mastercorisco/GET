from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

import jsonschema
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.block.catalogs import exchange_package_schema
from app.domain.block.export_support import (
    block_level_premises,
    export_status_for_point,
    find_fascicle_id,
    knowledge_snapshot,
    load_premises,
    parse_point_lists,
    premise_to_resolved,
    reference_snapshot,
    resolved_premises_for_point,
)
from app.domain.block.models import DevelopmentPoint
from app.models.document import DocumentNode
from app.services.document_service import compute_display_codes
from app.services.export.serializer import dumps_deterministic
from app.services.llm_export.builder import build_llm_block_export


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_exchange_package(
    session: Session,
    block_id: str,
    *,
    include_draft: bool = False,
    package_id: str | None = None,
    exported_at: str | None = None,
    profile: str = "discussion",
    created_by: str = "local_user",
) -> dict[str, Any]:
    """Devolve pacote GET-LLM (substitui get_exchange_package em runtime)."""
    return build_llm_block_export(
        session,
        block_id,
        include_draft=include_draft,
        profile=profile,
        export_id=package_id,
        generated_at=exported_at,
        created_by=created_by,
    )


def build_legacy_exchange_package(
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
        lists = parse_point_lists(point.lists_json)
        premises = resolved_premises_for_point(session, project_id, fascicle_id, block_id, point.id)
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
        snap = knowledge_snapshot(session, kid)
        if snap:
            knowledge_items.append(snap)

    references = []
    for rid in sorted(all_ref_ids):
        snap = reference_snapshot(session, rid)
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
    package = build_llm_block_export(
        session,
        block_id,
        include_draft=include_draft,
        export_id="deterministic-package-id",
        generated_at="2000-01-01T00:00:00+00:00",
    )
    return dumps_deterministic(package)