"""Enriquecimento de cabeçalhos de bloco e estados de pontos para autoracao."""

from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.block.models import DevelopmentPoint
from app.models.document import DocumentNode

TARGET_OUTPUT = {
    "format": "spec_section",
    "language": "pt-PT",
    "tone": "formal_technical",
}
DEFAULT_GUIDANCE = (
    "Desenvolver apenas com factos e decisões já aprovados; distinguir o que está em aberto; "
    "não inventar requisitos quantitativos, marcas ou arquitecturas não decididas."
)
INTENDED_OUTCOME = (
    "O tópico fica descrito no caderno de encargos com fronteiras claras, "
    "sem inventar requisitos não fornecidos."
)


def _parse_lists(raw: str) -> dict:
    try:
        data = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _default_objective(title: str) -> str:
    return (
        f"Preparar «{title}» para o caderno de encargos da "
        "remodelação do sistema de comando e controlo da CTBJ."
    )


def _default_scope(titles: list[str]) -> str:
    if titles:
        shown = titles[:14]
        tail = "…" if len(titles) > len(shown) else ""
        return "Pontos previstos neste bloco: " + "; ".join(shown) + tail + "."
    return "Âmbito a detalhar a partir da estrutura CTBJ v3."


def enrich_block_header(
    block: DocumentNode,
    point_titles: list[str],
    *,
    force: bool = False,
) -> dict[str, bool]:
    changed = {"objective": False, "scope": False, "target_output": False, "block_status": False}
    if force or not (block.objective or "").strip():
        block.objective = _default_objective(block.title)
        changed["objective"] = True
    if force or not (block.scope or "").strip():
        block.scope = _default_scope(point_titles)
        changed["scope"] = True
    try:
        tgt = json.loads(block.target_output_json or "{}")
    except json.JSONDecodeError:
        tgt = {}
    if not isinstance(tgt, dict) or not tgt:
        block.target_output_json = json.dumps(TARGET_OUTPUT, ensure_ascii=False)
        changed["target_output"] = True
    if block.block_status != "active":
        block.block_status = "active"
        changed["block_status"] = True
    return changed


def classify_point_for_authoring(point: DevelopmentPoint, *, clear_needs_review: bool = True) -> dict:
    """decisões firmes: llm_freedom strict; mínimo ready se core_idea preenchida."""
    before = {"status": point.status, "llm_freedom": point.llm_freedom, "needs_review": point.needs_review}
    point.llm_freedom = "strict"
    if clear_needs_review:
        point.needs_review = False
    if point.status in ("draft", "incomplete"):
        if (point.core_idea or "").strip() and (point.title or "").strip():
            point.status = "ready"
        elif point.status == "draft":
            point.status = "incomplete"
    if not (point.intended_outcome or "").strip():
        point.intended_outcome = INTENDED_OUTCOME
    lists = _parse_lists(point.lists_json)
    guidance = lists.get("development_guidance")
    if not guidance:
        lists["development_guidance"] = [DEFAULT_GUIDANCE]
        point.lists_json = json.dumps(lists, ensure_ascii=False)
    return {"before": before, "after": {"status": point.status, "llm_freedom": point.llm_freedom}}


def enrich_project_authoring(
    session: Session,
    project_id: str,
    *,
    run_id: str = "enrich",
    clear_needs_review: bool = True,
) -> dict:
    del run_id
    blocks = list(
        session.scalars(
            select(DocumentNode).where(
                DocumentNode.project_id == project_id,
                DocumentNode.node_type == "block",
            )
        )
    )
    stats = {
        "blocks": len(blocks),
        "headers_patched": 0,
        "points_classified": 0,
        "points_ready": 0,
        "points_incomplete": 0,
        "draft_remaining": 0,
        "strict_points": 0,
    }
    for block in blocks:
        points = list(
            session.scalars(
                select(DevelopmentPoint)
                .where(DevelopmentPoint.block_id == block.id)
                .where(DevelopmentPoint.status != "obsolete")
                .order_by(DevelopmentPoint.sort_order)
            )
        )
        titles = [p.title for p in points if (p.title or "").strip()]
        header_changed = enrich_block_header(block, titles)
        if any(header_changed.values()):
            stats["headers_patched"] += 1
        for point in points:
            classify_point_for_authoring(point, clear_needs_review=clear_needs_review)
            stats["points_classified"] += 1
            if point.status == "ready":
                stats["points_ready"] += 1
            elif point.status == "incomplete":
                stats["points_incomplete"] += 1
            elif point.status == "draft":
                stats["draft_remaining"] += 1
            if point.llm_freedom == "strict":
                stats["strict_points"] += 1
    session.flush()
    return stats