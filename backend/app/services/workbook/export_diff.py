from __future__ import annotations

from sqlalchemy import select

from app.config import AppSettings
from app.models.document import DocumentNode
from app.services.document_service import compute_display_codes, list_document_nodes
from app.services.knowledge_service import list_items
from app.services.reference_service import list_references
from app.services.technical_service import list_instances
from app.services.workbook.constants import (
    SHEET_A01,
    SHEET_ARTEFACTOS,
    SHEET_BLOCOS,
    SHEET_FASCICULOS,
    SHEET_FILOSOFIA,
    SHEET_MAPA,
)
from app.services.workbook.types import MigrationIssue, WorkbookBundle
from app.services.workspace_service import workspace_session

_APPEND_MSG = (
    "Código já existe no projecto — consolidação append-only não actualiza esta linha."
)


def _norm(text: str | None) -> str:
    return (text or "").strip()


def _fascicle_objectives(app_settings: AppSettings, project_id: str) -> dict[str, str]:
    with workspace_session(app_settings) as (session, _paths):
        nodes = list(session.scalars(select(DocumentNode).where(DocumentNode.project_id == project_id)))
        codes = compute_display_codes(nodes)
        result: dict[str, str] = {}
        for n in nodes:
            if n.node_type == "fascicle":
                code = codes.get(n.id, "")
                if code:
                    result[code] = n.objective or ""
        return result


def append_only_collision_warnings(
    app_settings: AppSettings,
    project_id: str,
    bundle: WorkbookBundle,
) -> list[MigrationIssue]:
    issues: list[MigrationIssue] = []
    nodes = list_document_nodes(app_settings, project_id).nodes
    fasc_by_code = {n.display_code: n for n in nodes if n.node_type == "fascicle" and n.display_code}
    blocks_by_key: dict[tuple[str, str], object] = {}
    by_id = {n.id: n for n in nodes}
    for n in nodes:
        if n.node_type != "block" or not n.display_code or not n.parent_id:
            continue
        parent = by_id.get(n.parent_id)
        if parent and parent.display_code:
            blocks_by_key[(parent.display_code, n.display_code)] = n

    objectives = _fascicle_objectives(app_settings, project_id)

    for fascicle in bundle.fascicles:
        existing = fasc_by_code.get(fascicle.codigo)
        if existing is None:
            continue
        obj_db = objectives.get(fascicle.codigo, "")
        changed = _norm(existing.title) != _norm(fascicle.designacao) or _norm(obj_db) != _norm(
            fascicle.objetivo
        )
        msg = _APPEND_MSG if changed else "Código já existe — linha será ignorada na consolidação append-only."
        issues.append(
            MigrationIssue("warning", SHEET_FASCICULOS, fascicle.source_row, fascicle.codigo, msg)
        )

    for block in bundle.blocks:
        existing = blocks_by_key.get((block.fasciculo, block.block_code))
        if existing is None:
            continue
        changed = _norm(existing.title) != _norm(block.block_title)
        msg = _APPEND_MSG if changed else "Código já existe — linha será ignorada na consolidação append-only."
        issues.append(
            MigrationIssue("warning", SHEET_BLOCOS, block.source_row, block.block_code, msg)
        )

    project_items = {
        i.human_code: i
        for i in list_items(app_settings, scope_type="project", scope_id=project_id)
        if i.human_code
    }
    for principle in bundle.principles:
        existing = project_items.get(principle.human_code)
        if existing is None:
            continue
        same = _norm(existing.title) == _norm(principle.title) and _norm(existing.content) == _norm(
            principle.content
        )
        msg = "Código já existe — linha será ignorada na consolidação append-only." if same else _APPEND_MSG
        issues.append(
            MigrationIssue("warning", SHEET_FILOSOFIA, principle.source_row, principle.human_code, msg)
        )

    for artefact in bundle.artefacts:
        if artefact.scope_type == "library":
            continue
        existing = project_items.get(artefact.human_code)
        if existing is None:
            continue
        same = _norm(existing.title) == _norm(artefact.title) and _norm(existing.content) == _norm(
            artefact.content
        )
        msg = "Código já existe — linha será ignorada na consolidação append-only." if same else _APPEND_MSG
        issues.append(
            MigrationIssue("warning", SHEET_ARTEFACTOS, artefact.source_row, artefact.human_code, msg)
        )

    export_codes = {i.export_code for i in list_instances(app_settings, project_id) if i.export_code}
    for row in bundle.a01_rows:
        if row.function_id not in export_codes:
            continue
        issues.append(
            MigrationIssue(
                "warning",
                SHEET_A01,
                row.source_row,
                row.function_id,
                "function_id já existe — linha será ignorada na consolidação append-only.",
            )
        )

    ref_titles = {r.title.strip().lower() for r in list_references(app_settings, "library", None)}
    for ref_row in bundle.references:
        key = ref_row.title.strip().lower()
        if key not in ref_titles:
            continue
        issues.append(
            MigrationIssue(
                "warning",
                SHEET_MAPA,
                ref_row.source_row,
                ref_row.title,
                "Referência já existe na biblioteca — linha será ignorada na consolidação append-only.",
            )
        )

    return issues