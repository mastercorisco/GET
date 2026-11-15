from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import AppSettings
from app.domain.block.catalogs import template_by_id
from app.domain.block.export import build_exchange_package, find_fascicle_id, load_premises
from app.domain.block.models import DEFAULT_LISTS_JSON, DevelopmentPoint, Premise
from app.domain.block.schemas import (
    BlockDetailResponse,
    BlockHeaderPatch,
    BlockHeaderResponse,
    BlockValidationResponse,
    DevelopmentPointCreate,
    DevelopmentPointPatch,
    DevelopmentPointResponse,
    PointLists,
    PointSummary,
    PremiseCreate,
    PremisePatch,
    PremiseResponse,
    ValidationIssue,
)
from app.models.document import DocumentNode
from app.models.knowledge import KnowledgeDraft, KnowledgeItem, KnowledgeRevision
from app.models.reference import Reference
from app.models.workspace import WorkspaceSettings
from app.services.document_service import compute_display_codes
from app.services.workspace_service import workspace_session

TBD_PATTERN = re.compile(r"\b(tbd|por definir|confirmar)\b", re.IGNORECASE)
WRITING_VERB_PATTERN = re.compile(r"^\s*(descrever|explicar|falar sobre)\b", re.IGNORECASE)

FAILURE_BEHAVIOR_PROMPTS = [
    "condição desencadeadora",
    "comportamento esperado",
    "estado seguro",
    "sinalização",
    "condições de recuperação",
    "intervenção do operador",
    "assuntos remetidos para engenharia de detalhe",
]


class BlockError(Exception):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _parse_lists(raw: str) -> PointLists:
    try:
        data = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        data = {}
    return PointLists.model_validate(data)


def _dump_lists(lists: PointLists) -> str:
    return json.dumps(lists.model_dump(), ensure_ascii=False, separators=(",", ":"))


def _default_lists() -> PointLists:
    return PointLists.model_validate(json.loads(DEFAULT_LISTS_JSON))


def _get_block(session: Session, block_id: str) -> DocumentNode:
    block = session.get(DocumentNode, block_id)
    if block is None or block.node_type != "block":
        raise BlockError("Bloco não encontrado.")
    return block


def _display_codes(session: Session, project_id: str) -> dict[str, str]:
    nodes = list(session.scalars(select(DocumentNode).where(DocumentNode.project_id == project_id)))
    return compute_display_codes(nodes)


def _block_header(session: Session, block: DocumentNode) -> BlockHeaderResponse:
    codes = _display_codes(session, block.project_id)
    try:
        target = json.loads(block.target_output_json or "{}")
    except json.JSONDecodeError:
        target = {}
    return BlockHeaderResponse(
        id=block.id,
        project_id=block.project_id,
        fascicle_id=find_fascicle_id(session, block),
        display_code=codes.get(block.id, ""),
        title=block.title,
        objective=block.objective or "",
        scope=block.scope or "",
        target_output=target if isinstance(target, dict) else {},
        block_status=block.block_status or "active",
    )


def _text_in_lists(lists: PointLists) -> str:
    parts: list[str] = []
    parts.extend(lists.development_guidance)
    parts.extend(lists.acceptance_criteria)
    for coll in (
        lists.must_include,
        lists.limits_and_exclusions,
        lists.open_questions,
        lists.questions_to_answer,
        lists.examples,
    ):
        for row in coll:
            parts.append(json.dumps(row, ensure_ascii=False))
    return " ".join(parts).lower()


def validate_point(
    session: Session,
    point: DevelopmentPoint,
    *,
    sibling_points: list[DevelopmentPoint] | None = None,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    lists = _parse_lists(point.lists_json)
    pid = point.id

    if not point.title.strip():
        issues.append(
            ValidationIssue(
                code="title_empty",
                message="O título é obrigatório.",
                severity="error",
                point_id=pid,
                field="title",
            )
        )
    elif len(point.title) > 120:
        issues.append(
            ValidationIssue(
                code="title_long",
                message="O título ultrapassa 120 caracteres.",
                severity="warning",
                point_id=pid,
                field="title",
            )
        )

    if not point.core_idea.strip():
        issues.append(
            ValidationIssue(
                code="core_idea_empty",
                message="A ideia central é obrigatória para marcar como ready.",
                severity="error",
                point_id=pid,
                field="core_idea",
            )
        )
    elif WRITING_VERB_PATTERN.search(point.core_idea):
        issues.append(
            ValidationIssue(
                code="core_idea_writing_instruction",
                message="A ideia central pode ser uma instrução de redação em vez de afirmação técnica.",
                severity="suggestion",
                point_id=pid,
                field="core_idea",
            )
        )

    has_min_content = bool(
        lists.development_guidance
        or lists.questions_to_answer
        or lists.must_include
        or lists.acceptance_criteria
    )
    if point.status == "ready" and (not point.title.strip() or not point.core_idea.strip() or not has_min_content):
        issues.append(
            ValidationIssue(
                code="ready_min_content",
                message="Ponto ready requer título, ideia central e orientação, questão ou elemento obrigatório.",
                severity="error",
                point_id=pid,
            )
        )

    must_texts = {json.dumps(x, sort_keys=True) for x in lists.must_include}
    for lim in lists.limits_and_exclusions:
        lim_s = json.dumps(lim, sort_keys=True)
        if lim_s in must_texts:
            issues.append(
                ValidationIssue(
                    code="must_limit_conflict",
                    message="Elemento obrigatório também presente nos limites/exclusões.",
                    severity="error",
                    point_id=pid,
                )
            )

    body_text = _text_in_lists(lists) + " " + point.core_idea.lower() + " " + point.title.lower()
    if TBD_PATTERN.search(body_text) and not lists.open_questions:
        issues.append(
            ValidationIssue(
                code="tbd_without_open_question",
                message="Referência a TBD/por definir sem questão pendente.",
                severity="warning",
                point_id=pid,
            )
        )

    for ref_id in lists.reference_ids:
        if session.get(Reference, ref_id) is None:
            issues.append(
                ValidationIssue(
                    code="broken_reference",
                    message=f"Referência inexistente: {ref_id}",
                    severity="error",
                    point_id=pid,
                    field="reference_ids",
                )
            )

    for kid in lists.knowledge_item_ids:
        item = session.get(KnowledgeItem, kid)
        if item is None:
            issues.append(
                ValidationIssue(
                    code="broken_knowledge_item",
                    message=f"KnowledgeItem inexistente: {kid}",
                    severity="error",
                    point_id=pid,
                )
            )
            continue
        rev = session.scalar(
            select(KnowledgeRevision)
            .where(KnowledgeRevision.item_id == kid)
            .order_by(KnowledgeRevision.revision_num.desc())
            .limit(1)
        )
        lifecycle = rev.lifecycle if rev else (session.get(KnowledgeDraft, kid).lifecycle if session.get(KnowledgeDraft, kid) else "active")
        if lifecycle in ("withdrawn", "archived", "superseded"):
            issues.append(
                ValidationIssue(
                    code="obsolete_knowledge_item",
                    message=f"KnowledgeItem obsoleto associado: {kid}",
                    severity="warning",
                    point_id=pid,
                )
            )

    if sibling_points:
        orders = [p.sort_order for p in sibling_points if p.status != "obsolete"]
        if len(orders) != len(set(orders)):
            issues.append(
                ValidationIssue(
                    code="duplicate_order",
                    message="Ordem duplicada entre pontos do bloco.",
                    severity="error",
                    point_id=pid,
                )
            )
        fingerprint = (
            point.title.strip().lower(),
            point.core_idea.strip().lower(),
            _dump_lists(lists),
        )
        for other in sibling_points:
            if other.id == point.id or other.status == "obsolete":
                continue
            other_lists = _parse_lists(other.lists_json)
            other_fp = (
                other.title.strip().lower(),
                other.core_idea.strip().lower(),
                _dump_lists(other_lists),
            )
            if fingerprint == other_fp and fingerprint[0] and fingerprint[1]:
                issues.append(
                    ValidationIssue(
                        code="duplicate_point",
                        message="Duplicação exacta de outro ponto no bloco.",
                        severity="warning",
                        point_id=pid,
                    )
                )

    return issues


def suggested_status(point: DevelopmentPoint, issues: list[ValidationIssue]) -> str:
    if point.status == "approved" or point.status == "obsolete":
        return point.status
    errors = [i for i in issues if i.severity == "error"]
    if errors:
        if point.title.strip() or point.core_idea.strip():
            return "incomplete"
        return "draft"
    lists = _parse_lists(point.lists_json)
    if (
        point.title.strip()
        and point.core_idea.strip()
        and (
            lists.development_guidance
            or lists.questions_to_answer
            or lists.must_include
            or lists.acceptance_criteria
        )
    ):
        return "ready"
    return "draft"


def _completeness_alerts(point: DevelopmentPoint, issues: list[ValidationIssue]) -> list[str]:
    alerts = [i.message for i in issues if i.severity == "error"]
    if point.needs_review:
        alerts.append("Revisão necessária após alteração a um ponto aprovado.")
    return alerts[:4]


def _point_summary(
    session: Session,
    point: DevelopmentPoint,
    sibling_points: list[DevelopmentPoint],
) -> PointSummary:
    lists = _parse_lists(point.lists_json)
    block = _get_block(session, point.block_id)
    project_id = block.project_id
    fascicle_id = find_fascicle_id(session, block)
    premise_count = len(
        load_premises(session, "development_point", point.id)
    ) + len(load_premises(session, "block", point.block_id))
    if fascicle_id:
        premise_count += len(load_premises(session, "fascicle", fascicle_id))
    premise_count += len(load_premises(session, "project", project_id))
    issues = validate_point(session, point, sibling_points=sibling_points)
    return PointSummary(
        id=point.id,
        order=point.sort_order,
        title=point.title,
        status=point.status,
        llm_freedom=point.llm_freedom,
        needs_review=point.needs_review,
        premise_count=premise_count,
        must_include_count=len(lists.must_include),
        open_questions_count=len(lists.open_questions),
        acceptance_criteria_count=len(lists.acceptance_criteria),
        completeness_alerts=_completeness_alerts(point, issues),
    )


def _point_response(
    session: Session,
    point: DevelopmentPoint,
    sibling_points: list[DevelopmentPoint],
) -> DevelopmentPointResponse:
    issues = validate_point(session, point, sibling_points=sibling_points)
    return DevelopmentPointResponse(
        id=point.id,
        block_id=point.block_id,
        order=point.sort_order,
        title=point.title,
        core_idea=point.core_idea,
        intended_outcome=point.intended_outcome,
        llm_freedom=point.llm_freedom,
        status=point.status,
        template_id=point.template_id,
        needs_review=point.needs_review,
        lists=_parse_lists(point.lists_json),
        validation_issues=issues,
    )


def _next_sort_order(session: Session, block_id: str) -> int:
    max_order = session.scalar(
        select(func.max(DevelopmentPoint.sort_order)).where(DevelopmentPoint.block_id == block_id)
    )
    return (max_order or 0) + 1


def _lists_from_template(template_id: str | None) -> PointLists:
    lists = _default_lists()
    if template_id == "failure_behavior":
        lists.questions_to_answer = [{"prompt": label, "answer": ""} for label in FAILURE_BEHAVIOR_PROMPTS]
        return lists
    tpl = template_by_id(template_id) if template_id else None
    if tpl is None:
        return lists
    lists.questions_to_answer = [{"prompt": p, "answer": ""} for p in tpl.get("prompts", [])]
    return lists


def get_block_detail(app_settings: AppSettings, block_id: str) -> BlockDetailResponse:
    with workspace_session(app_settings) as (session, _paths):
        block = _get_block(session, block_id)
        points = list(
            session.scalars(
                select(DevelopmentPoint)
                .where(DevelopmentPoint.block_id == block_id)
                .where(DevelopmentPoint.status != "obsolete")
                .order_by(DevelopmentPoint.sort_order, DevelopmentPoint.id)
            )
        )
        summaries = [_point_summary(session, p, points) for p in points]
        return BlockDetailResponse(block=_block_header(session, block), points=summaries)


def patch_block(app_settings: AppSettings, block_id: str, body: BlockHeaderPatch) -> BlockHeaderResponse:
    with workspace_session(app_settings) as (session, _paths):
        block = _get_block(session, block_id)
        if body.title is not None:
            block.title = body.title.strip()
        if body.objective is not None:
            block.objective = body.objective
        if body.scope is not None:
            block.scope = body.scope
        if body.target_output is not None:
            block.target_output_json = json.dumps(body.target_output, ensure_ascii=False)
        if body.block_status is not None:
            block.block_status = body.block_status
        session.flush()
        return _block_header(session, block)


def create_point(
    app_settings: AppSettings, block_id: str, body: DevelopmentPointCreate
) -> DevelopmentPointResponse:
    with workspace_session(app_settings) as (session, _paths):
        _get_block(session, block_id)
        lists = _lists_from_template(body.template_id)
        point = DevelopmentPoint(
            block_id=block_id,
            sort_order=_next_sort_order(session, block_id),
            title=body.title.strip(),
            lists_json=_dump_lists(lists),
            template_id=body.template_id,
        )
        session.add(point)
        session.flush()
        siblings = list(
            session.scalars(select(DevelopmentPoint).where(DevelopmentPoint.block_id == block_id))
        )
        return _point_response(session, point, siblings)


def get_point(app_settings: AppSettings, point_id: str) -> DevelopmentPointResponse:
    with workspace_session(app_settings) as (session, _paths):
        point = session.get(DevelopmentPoint, point_id)
        if point is None:
            raise BlockError("Ponto não encontrado.")
        siblings = list(
            session.scalars(select(DevelopmentPoint).where(DevelopmentPoint.block_id == point.block_id))
        )
        return _point_response(session, point, siblings)


def patch_point(app_settings: AppSettings, point_id: str, body: DevelopmentPointPatch) -> DevelopmentPointResponse:
    with workspace_session(app_settings) as (session, _paths):
        point = session.get(DevelopmentPoint, point_id)
        if point is None:
            raise BlockError("Ponto não encontrado.")
        was_approved = point.status == "approved"
        if body.title is not None:
            point.title = body.title
        if body.core_idea is not None:
            point.core_idea = body.core_idea
        if body.intended_outcome is not None:
            point.intended_outcome = body.intended_outcome
        if body.llm_freedom is not None:
            point.llm_freedom = body.llm_freedom
        if body.lists is not None:
            point.lists_json = _dump_lists(body.lists)
        if body.status is not None:
            point.status = body.status
        point.updated_at = _utcnow()
        if was_approved and (body.model_fields_set - {"status"}):
            point.needs_review = True
        siblings = list(
            session.scalars(select(DevelopmentPoint).where(DevelopmentPoint.block_id == point.block_id))
        )
        issues = validate_point(session, point, sibling_points=siblings)
        if body.status is None and point.status not in ("approved", "obsolete"):
            point.status = suggested_status(point, issues)
        session.flush()
        return _point_response(session, point, siblings)


def delete_point(app_settings: AppSettings, point_id: str) -> None:
    with workspace_session(app_settings) as (session, _paths):
        point = session.get(DevelopmentPoint, point_id)
        if point is None:
            raise BlockError("Ponto não encontrado.")
        for row in load_premises(session, "development_point", point_id):
            session.delete(row)
        session.delete(point)


def duplicate_point(app_settings: AppSettings, point_id: str) -> DevelopmentPointResponse:
    with workspace_session(app_settings) as (session, _paths):
        src = session.get(DevelopmentPoint, point_id)
        if src is None:
            raise BlockError("Ponto não encontrado.")
        clone = DevelopmentPoint(
            block_id=src.block_id,
            sort_order=_next_sort_order(session, src.block_id),
            title=src.title + " (cópia)" if src.title else "",
            core_idea=src.core_idea,
            intended_outcome=src.intended_outcome,
            llm_freedom=src.llm_freedom,
            status="draft",
            template_id=src.template_id,
            lists_json=src.lists_json,
        )
        session.add(clone)
        session.flush()
        for prem in load_premises(session, "development_point", point_id):
            session.add(
                Premise(
                    owner_kind="development_point",
                    owner_id=clone.id,
                    statement=prem.statement,
                    importance=prem.importance,
                    source_type=prem.source_type,
                    confidence=prem.confidence,
                    reference_id=prem.reference_id,
                    notes=prem.notes,
                )
            )
        siblings = list(
            session.scalars(select(DevelopmentPoint).where(DevelopmentPoint.block_id == src.block_id))
        )
        return _point_response(session, clone, siblings)


def archive_point(app_settings: AppSettings, point_id: str) -> DevelopmentPointResponse:
    with workspace_session(app_settings) as (session, _paths):
        point = session.get(DevelopmentPoint, point_id)
        if point is None:
            raise BlockError("Ponto não encontrado.")
        point.status = "obsolete"
        point.updated_at = _utcnow()
        siblings = list(
            session.scalars(select(DevelopmentPoint).where(DevelopmentPoint.block_id == point.block_id))
        )
        return _point_response(session, point, siblings)


def move_point(app_settings: AppSettings, point_id: str, target_block_id: str) -> DevelopmentPointResponse:
    with workspace_session(app_settings) as (session, _paths):
        point = session.get(DevelopmentPoint, point_id)
        if point is None:
            raise BlockError("Ponto não encontrado.")
        _get_block(session, target_block_id)
        point.block_id = target_block_id
        point.sort_order = _next_sort_order(session, target_block_id)
        point.updated_at = _utcnow()
        siblings = list(
            session.scalars(select(DevelopmentPoint).where(DevelopmentPoint.block_id == target_block_id))
        )
        return _point_response(session, point, siblings)


def reorder_points(app_settings: AppSettings, block_id: str, point_ids: list[str]) -> BlockDetailResponse:
    with workspace_session(app_settings) as (session, _paths):
        _get_block(session, block_id)
        points = {
            p.id: p
            for p in session.scalars(select(DevelopmentPoint).where(DevelopmentPoint.block_id == block_id))
        }
        if set(point_ids) != set(points.keys()):
            raise BlockError("Lista de reordenação inválida.")
        for index, pid in enumerate(point_ids, start=1):
            points[pid].sort_order = -(index + 1000)
        session.flush()
        for index, pid in enumerate(point_ids, start=1):
            points[pid].sort_order = index
        session.flush()
        block = _get_block(session, block_id)
        active = list(
            session.scalars(
                select(DevelopmentPoint)
                .where(DevelopmentPoint.block_id == block_id)
                .where(DevelopmentPoint.status != "obsolete")
                .order_by(DevelopmentPoint.sort_order, DevelopmentPoint.id)
            )
        )
        summaries = [_point_summary(session, p, active) for p in active]
        return BlockDetailResponse(block=_block_header(session, block), points=summaries)


def validate_block(app_settings: AppSettings, block_id: str) -> BlockValidationResponse:
    with workspace_session(app_settings) as (session, _paths):
        _get_block(session, block_id)
        points = list(
            session.scalars(select(DevelopmentPoint).where(DevelopmentPoint.block_id == block_id))
        )
        issues: list[ValidationIssue] = []
        for point in points:
            if point.status == "obsolete":
                continue
            issues.extend(validate_point(session, point, sibling_points=points))
        return BlockValidationResponse(issues=issues)


def preview_exchange(app_settings: AppSettings, block_id: str, include_draft: bool) -> dict:
    with workspace_session(app_settings) as (session, _paths):
        return build_exchange_package(session, block_id, include_draft=include_draft)


def write_exchange(app_settings: AppSettings, block_id: str, include_draft: bool) -> tuple[str, str]:
    with workspace_session(app_settings) as (session, paths):
        package = build_exchange_package(session, block_id, include_draft=include_draft)
        from app.services.export.serializer import dumps_deterministic

        text = dumps_deterministic(package)
        out_dir = paths.exports_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = f"exchange-{block_id[:8]}-{package['package_id'][:8]}.json"
        out_path = out_dir / filename
        out_path.write_text(text, encoding="utf-8")
        return str(out_path), package["package_id"]


def list_premises(app_settings: AppSettings, owner_kind: str, owner_id: str) -> list[PremiseResponse]:
    with workspace_session(app_settings) as (session, _paths):
        rows = load_premises(session, owner_kind, owner_id)
        return [
            PremiseResponse(
                id=r.id,
                owner_kind=r.owner_kind,
                owner_id=r.owner_id,
                statement=r.statement,
                importance=r.importance,
                source_type=r.source_type,
                confidence=r.confidence,
                reference_id=r.reference_id,
                notes=r.notes,
            )
            for r in rows
        ]


def create_premise(app_settings: AppSettings, body: PremiseCreate) -> PremiseResponse:
    with workspace_session(app_settings) as (session, _paths):
        row = Premise(
            owner_kind=body.owner_kind,
            owner_id=body.owner_id,
            statement=body.statement.strip(),
            importance=body.importance,
            source_type=body.source_type,
            confidence=body.confidence,
            reference_id=body.reference_id,
            notes=body.notes,
        )
        session.add(row)
        session.flush()
        return PremiseResponse(
            id=row.id,
            owner_kind=row.owner_kind,
            owner_id=row.owner_id,
            statement=row.statement,
            importance=row.importance,
            source_type=row.source_type,
            confidence=row.confidence,
            reference_id=row.reference_id,
            notes=row.notes,
        )


def patch_premise(app_settings: AppSettings, premise_id: str, body: PremisePatch) -> PremiseResponse:
    with workspace_session(app_settings) as (session, _paths):
        row = session.get(Premise, premise_id)
        if row is None:
            raise BlockError("Premissa não encontrada.")
        if body.statement is not None:
            row.statement = body.statement.strip()
        if body.importance is not None:
            row.importance = body.importance
        if body.source_type is not None:
            row.source_type = body.source_type
        if body.confidence is not None:
            row.confidence = body.confidence
        if body.reference_id is not None:
            row.reference_id = body.reference_id
        if body.notes is not None:
            row.notes = body.notes
        return PremiseResponse(
            id=row.id,
            owner_kind=row.owner_kind,
            owner_id=row.owner_id,
            statement=row.statement,
            importance=row.importance,
            source_type=row.source_type,
            confidence=row.confidence,
            reference_id=row.reference_id,
            notes=row.notes,
        )


def delete_premise(app_settings: AppSettings, premise_id: str) -> None:
    with workspace_session(app_settings) as (session, _paths):
        row = session.get(Premise, premise_id)
        if row is None:
            raise BlockError("Premissa não encontrada.")
        session.delete(row)


def get_help_level(app_settings: AppSettings) -> str:
    with workspace_session(app_settings) as (session, _paths):
        settings = session.scalar(select(WorkspaceSettings).limit(1))
        return settings.help_level if settings else "normal"


def patch_preferences(app_settings: AppSettings, help_level: str | None) -> str:
    with workspace_session(app_settings) as (session, _paths):
        settings = session.scalar(select(WorkspaceSettings).limit(1))
        if settings is None:
            raise BlockError("Workspace não configurado.")
        if help_level is not None:
            settings.help_level = help_level
        session.flush()
        return settings.help_level