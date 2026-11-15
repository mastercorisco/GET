from __future__ import annotations

from app.config import AppSettings
from app.schemas.document import DocumentNodeCreateRequest
from app.schemas.knowledge import KnowledgeCreateRequest
from app.schemas.project import ProjectCreateRequest
from app.schemas.reference import ReferenceCreateRequest
from app.schemas.technical import TechnicalInstanceCreateRequest
from app.services.backup_service import create_backup
from app.services.document_service import create_document_node, list_document_nodes
from app.services.knowledge_service import create_item
from app.services.project_service import ProjectError, create_project, get_project, list_templates
from app.services.reference_service import create_reference
from app.services.technical_service import create_instance
from app.services.knowledge_service import list_items
from app.services.reference_service import list_references
from app.services.technical_service import list_instances
from app.services.workbook.types import WorkbookBundle


class WorkbookApplyError(Exception):
    pass


def _seed_library(app_settings: AppSettings) -> None:
    create_item(
        app_settings,
        KnowledgeCreateRequest(
            title="Semente biblioteca (migração workbook)",
            content="Unidade inicial criada pela migração GET workbook v1.",
            origin_context="workbook-migration",
        ),
    )


def _fascicle_code_map(app_settings: AppSettings, project_id: str) -> dict[str, str]:
    nodes = list_document_nodes(app_settings, project_id).nodes
    return {
        n.display_code: n.id
        for n in nodes
        if n.node_type == "fascicle" and n.display_code
    }


def _block_exists(
    nodes: list,
    *,
    display_code: str,
    parent_id: str,
) -> bool:
    for n in nodes:
        if n.node_type != "block":
            continue
        if n.parent_id == parent_id and n.display_code == display_code:
            return True
    return False


def _project_human_codes(app_settings: AppSettings, project_id: str) -> set[str]:
    items = list_items(app_settings, scope_type="project", scope_id=project_id)
    return {c for c in (i.human_code for i in items if i.human_code)}


def _library_human_codes(app_settings: AppSettings) -> set[str]:
    items = list_items(app_settings, scope_type="library")
    return {c for c in (i.human_code for i in items if i.human_code)}


def _project_export_codes(app_settings: AppSettings, project_id: str) -> set[str]:
    instances = list_instances(app_settings, project_id)
    return {c for c in (i.export_code for i in instances if i.export_code)}


def _library_reference_titles(app_settings: AppSettings) -> set[str]:
    refs = list_references(app_settings, "library", None)
    return {r.title.strip().lower() for r in refs}


def apply_workbook_bundle(app_settings: AppSettings, bundle: WorkbookBundle) -> str:
    create_backup(app_settings, "critical")
    _seed_library(app_settings)

    templates = list_templates(app_settings)
    if not templates or not templates[0].versions:
        raise WorkbookApplyError("Modelo de projecto em falta.")
    template_version_id = templates[0].versions[0].id

    project = create_project(
        app_settings,
        ProjectCreateRequest(
            template_version_id=template_version_id,
            name=bundle.project_name[:255],
            intervention_type="brownfield",
        ),
    )
    project_id = project.id

    for fascicle in bundle.fascicles:
        create_document_node(
            app_settings,
            project_id,
            DocumentNodeCreateRequest(
                node_type="fascicle",
                title=fascicle.designacao,
                parent_id=None,
            ),
        )

    code_map = _fascicle_code_map(app_settings, project_id)
    for block in bundle.blocks:
        parent_id = code_map.get(block.fasciculo)
        if parent_id is None:
            raise WorkbookApplyError(
                f"Fascículo pai não encontrado para bloco {block.block_code} ({block.fasciculo})."
            )
        create_document_node(
            app_settings,
            project_id,
            DocumentNodeCreateRequest(
                node_type="block",
                title=block.block_title,
                parent_id=parent_id,
            ),
        )

    for principle in bundle.principles:
        create_item(
            app_settings,
            KnowledgeCreateRequest(
                title=principle.title,
                content=principle.content,
                origin_context="workbook:03_Filosofia_Controlo",
                scope_type="project",
                scope_id=project_id,
                knowledge_type="principle",
                human_code=principle.human_code,
            ),
        )

    for artefact in bundle.artefacts:
        create_item(
            app_settings,
            KnowledgeCreateRequest(
                title=artefact.title,
                content=artefact.content,
                origin_context="workbook:04_Artefactos_GET",
                scope_type=artefact.scope_type,  # type: ignore[arg-type]
                scope_id=None if artefact.scope_type == "library" else project_id,
                knowledge_type="decision",
                human_code=artefact.human_code,
            ),
        )

    for row in bundle.a01_rows:
        create_instance(
            app_settings,
            project_id,
            TechnicalInstanceCreateRequest(
                kind="function",
                name=row.name,
                export_code=row.function_id,
                reference_note=row.reference_note,
            ),
        )

    for ref_row in bundle.references:
        create_reference(
            app_settings,
            ReferenceCreateRequest(
                scope_type="library",
                title=ref_row.title,
                citation=ref_row.citation,
                notes=ref_row.notes,
            ),
        )

    return project_id


def apply_workbook_to_project(
    app_settings: AppSettings,
    project_id: str,
    bundle: WorkbookBundle,
) -> tuple[str, dict[str, int]]:
    """Anexa conteúdo do workbook a um projecto existente (sem eliminações por omissão)."""
    try:
        get_project(app_settings, project_id)
    except ProjectError as exc:
        raise WorkbookApplyError(str(exc)) from exc
    create_backup(app_settings, "critical")
    _seed_library(app_settings)

    summary = {
        "fascicles_added": 0,
        "blocks_added": 0,
        "principles_added": 0,
        "artefacts_added": 0,
        "a01_rows_added": 0,
        "references_added": 0,
    }

    nodes = list_document_nodes(app_settings, project_id).nodes
    code_map = _fascicle_code_map(app_settings, project_id)
    title_to_fascicle: dict[str, str] = {
        n.title.strip().lower(): n.id
        for n in nodes
        if n.node_type == "fascicle"
    }

    for fascicle in bundle.fascicles:
        if fascicle.codigo in code_map:
            continue
        match_id = title_to_fascicle.get(fascicle.designacao.strip().lower())
        if match_id:
            matched = next(n for n in nodes if n.id == match_id)
            if matched.display_code:
                code_map[fascicle.codigo] = match_id
            continue
        create_document_node(
            app_settings,
            project_id,
            DocumentNodeCreateRequest(
                node_type="fascicle",
                title=fascicle.designacao,
                parent_id=None,
            ),
        )
        summary["fascicles_added"] += 1

    code_map = _fascicle_code_map(app_settings, project_id)
    nodes = list_document_nodes(app_settings, project_id).nodes

    for block in bundle.blocks:
        parent_id = code_map.get(block.fasciculo)
        if parent_id is None:
            raise WorkbookApplyError(
                f"Fascículo pai não encontrado para bloco {block.block_code} ({block.fasciculo})."
            )
        if _block_exists(nodes, display_code=block.block_code, parent_id=parent_id):
            continue
        create_document_node(
            app_settings,
            project_id,
            DocumentNodeCreateRequest(
                node_type="block",
                title=block.block_title,
                parent_id=parent_id,
            ),
        )
        summary["blocks_added"] += 1
        nodes = list_document_nodes(app_settings, project_id).nodes

    project_codes = _project_human_codes(app_settings, project_id)
    library_codes = _library_human_codes(app_settings)

    for principle in bundle.principles:
        if principle.human_code in project_codes:
            continue
        create_item(
            app_settings,
            KnowledgeCreateRequest(
                title=principle.title,
                content=principle.content,
                origin_context="workbook:03_Filosofia_Controlo",
                scope_type="project",
                scope_id=project_id,
                knowledge_type="principle",
                human_code=principle.human_code,
            ),
        )
        project_codes.add(principle.human_code)
        summary["principles_added"] += 1

    for artefact in bundle.artefacts:
        code_set = library_codes if artefact.scope_type == "library" else project_codes
        if artefact.human_code in code_set:
            continue
        create_item(
            app_settings,
            KnowledgeCreateRequest(
                title=artefact.title,
                content=artefact.content,
                origin_context="workbook:04_Artefactos_GET",
                scope_type=artefact.scope_type,  # type: ignore[arg-type]
                scope_id=None if artefact.scope_type == "library" else project_id,
                knowledge_type="decision",
                human_code=artefact.human_code,
            ),
        )
        code_set.add(artefact.human_code)
        summary["artefacts_added"] += 1

    export_codes = _project_export_codes(app_settings, project_id)
    for row in bundle.a01_rows:
        if row.function_id in export_codes:
            continue
        create_instance(
            app_settings,
            project_id,
            TechnicalInstanceCreateRequest(
                kind="function",
                name=row.name,
                export_code=row.function_id,
                reference_note=row.reference_note,
            ),
        )
        export_codes.add(row.function_id)
        summary["a01_rows_added"] += 1

    ref_titles = _library_reference_titles(app_settings)
    for ref_row in bundle.references:
        key = ref_row.title.strip().lower()
        if key in ref_titles:
            continue
        create_reference(
            app_settings,
            ReferenceCreateRequest(
                scope_type="library",
                title=ref_row.title,
                citation=ref_row.citation,
                notes=ref_row.notes,
            ),
        )
        ref_titles.add(key)
        summary["references_added"] += 1

    return project_id, summary