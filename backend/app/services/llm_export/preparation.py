from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.block.export_support import (
    block_level_premises,
    export_status_for_point,
    find_fascicle_id,
    knowledge_snapshot,
    parse_point_lists,
    reference_snapshot,
    resolved_premises_for_point,
)
from app.domain.block.models import DevelopmentPoint
from app.models.document import DocumentNode
from app.services.document_service import compute_display_codes


def _list_texts(items: list[Any]) -> list[str]:
    texts: list[str] = []
    for item in items:
        if isinstance(item, dict):
            text = item.get("text") or item.get("title") or item.get("description")
            if text:
                texts.append(str(text).strip())
        elif isinstance(item, str) and item.strip():
            texts.append(item.strip())
    return texts


class BlockPreparationBundle:
    def __init__(
        self,
        *,
        display_code: str,
        fascicle_id: str | None,
        target_output: dict[str, Any],
        export_points: list[dict[str, Any]],
        block_premises: list[dict[str, Any]],
        knowledge_item_ids: set[str],
        reference_ids: set[str],
        scope_includes: list[str],
        scope_excludes: list[str],
        supporting_knowledge: list[dict[str, Any]],
        supporting_references: list[dict[str, Any]],
        supporting_examples: list[dict[str, Any]],
        open_questions: list[dict[str, Any]],
        missing_information: list[str],
    ) -> None:
        self.display_code = display_code
        self.fascicle_id = fascicle_id
        self.target_output = target_output
        self.export_points = export_points
        self.block_premises = block_premises
        self.knowledge_item_ids = knowledge_item_ids
        self.reference_ids = reference_ids
        self.scope_includes = scope_includes
        self.scope_excludes = scope_excludes
        self.supporting_knowledge = supporting_knowledge
        self.supporting_references = supporting_references
        self.supporting_examples = supporting_examples
        self.open_questions = open_questions
        self.missing_information = missing_information


def build_block_preparation(
    session: Session,
    block_id: str,
    *,
    include_draft: bool = False,
) -> tuple[DocumentNode, BlockPreparationBundle]:
    block = session.get(DocumentNode, block_id)
    if block is None or block.node_type != "block":
        raise ValueError("Bloco não encontrado.")

    project_id = block.project_id
    fascicle_id = find_fascicle_id(session, block)
    nodes = list(session.scalars(select(DocumentNode).where(DocumentNode.project_id == project_id)))
    codes = compute_display_codes(nodes)

    try:
        target_output = json.loads(block.target_output_json or "{}")
    except json.JSONDecodeError:
        target_output = {}
    if not isinstance(target_output, dict):
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
    scope_includes: list[str] = []
    scope_excludes: list[str] = []

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
        scope_includes.extend(_list_texts(lists.must_include))
        scope_excludes.extend(_list_texts(lists.limits_and_exclusions))
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

    bundle = BlockPreparationBundle(
        display_code=codes.get(block_id, ""),
        fascicle_id=fascicle_id,
        target_output=target_output,
        export_points=export_points,
        block_premises=block_level_premises(session, project_id, fascicle_id, block_id),
        knowledge_item_ids=all_ki_ids,
        reference_ids=all_ref_ids,
        scope_includes=scope_includes,
        scope_excludes=scope_excludes,
        supporting_knowledge=knowledge_items,
        supporting_references=references,
        supporting_examples=all_examples,
        open_questions=all_open_questions,
        missing_information=missing_information,
    )
    return block, bundle