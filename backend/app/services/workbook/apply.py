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
from app.services.project_service import create_project, list_templates
from app.services.reference_service import create_reference
from app.services.technical_service import create_instance
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