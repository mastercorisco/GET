from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from app.config import AppSettings
from app.models.knowledge import Library, LibraryVersion
from app.models.project import Project, ProjectLibraryPin, ProjectTemplate, ProjectTemplateVersion
from app.schemas.project import (
    ProjectCreateRequest,
    ProjectLlmContext,
    ProjectLlmContextPatch,
    ProjectLlmContextResponse,
    ProjectResponse,
    TemplateResponse,
    TemplateVersionResponse,
)
from app.services.knowledge_service import _ensure_library
from app.services.workspace_service import workspace_session

_BROWNFIELD_CODE = "brownfield-cee-csc"
_BROWNFIELD_NAME = (
    "Central de produção de energia elétrica — remodelação brownfield do sistema de comando e controlo"
)
class ProjectError(Exception):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _current_library_version(session) -> LibraryVersion:
    library = session.scalar(select(Library).limit(1))
    if library is None:
        raise ProjectError("Biblioteca em falta. Crie conhecimento na biblioteca primeiro.")
    version = session.scalar(
        select(LibraryVersion)
        .where(LibraryVersion.library_id == library.id)
        .order_by(LibraryVersion.version.desc())
        .limit(1)
    )
    if version is None:
        raise ProjectError("Versão da biblioteca em falta.")
    return version


def _ensure_templates(session) -> None:
    template = session.scalar(select(ProjectTemplate).where(ProjectTemplate.code == _BROWNFIELD_CODE))
    if template is None:
        template = ProjectTemplate(
            code=_BROWNFIELD_CODE,
            name=_BROWNFIELD_NAME,
            description=_BROWNFIELD_NAME,
            created_at=_utcnow(),
        )
        session.add(template)
        session.flush()
        session.add(
            ProjectTemplateVersion(
                template_id=template.id,
                version=1,
                metadata_json=json.dumps({"mvp": True, "schema": "0.1.0"}, ensure_ascii=False),
                created_at=_utcnow(),
            )
        )
        session.flush()
    if session.scalar(
        select(ProjectTemplateVersion).where(
            ProjectTemplateVersion.template_id == template.id,
            ProjectTemplateVersion.version == 1,
        )
    ) is None:
        session.add(
            ProjectTemplateVersion(
                template_id=template.id,
                version=1,
                metadata_json=json.dumps({"mvp": True, "schema": "0.1.0"}, ensure_ascii=False),
                created_at=_utcnow(),
            )
        )
        session.flush()
    if session.scalar(
        select(ProjectTemplateVersion).where(
            ProjectTemplateVersion.template_id == template.id,
            ProjectTemplateVersion.version == 2,
        )
    ) is None:
        session.add(
            ProjectTemplateVersion(
                template_id=template.id,
                version=2,
                metadata_json=json.dumps(
                    {"schema": "0.2.0", "ctbj_structure_version": 3},
                    ensure_ascii=False,
                ),
                created_at=_utcnow(),
            )
        )
        session.flush()


def ensure_template_version(session, version: int) -> ProjectTemplateVersion:
    """Expõe criação de nova versão de modelo (testes / evolução)."""
    _ensure_templates(session)
    template = session.scalar(select(ProjectTemplate).where(ProjectTemplate.code == _BROWNFIELD_CODE))
    if template is None:
        raise ProjectError("Modelo brownfield em falta.")
    row = session.scalar(
        select(ProjectTemplateVersion).where(
            ProjectTemplateVersion.template_id == template.id,
            ProjectTemplateVersion.version == version,
        )
    )
    if row is not None:
        return row
    row = ProjectTemplateVersion(
        template_id=template.id,
        version=version,
        metadata_json=json.dumps({"mvp": True, "schema": "0.1.0"}, ensure_ascii=False),
        created_at=_utcnow(),
    )
    session.add(row)
    session.flush()
    return row


def _project_response(session, project: Project) -> ProjectResponse:
    pin = session.scalar(select(ProjectLibraryPin).where(ProjectLibraryPin.project_id == project.id))
    if pin is None:
        raise ProjectError("Pin da biblioteca em falta.")
    template_version = session.get(ProjectTemplateVersion, project.template_version_id)
    if template_version is None:
        raise ProjectError("Versão do modelo em falta.")
    template = session.get(ProjectTemplate, template_version.template_id)
    if template is None:
        raise ProjectError("Modelo em falta.")
    library_version = session.get(LibraryVersion, pin.library_version_id)
    if library_version is None:
        raise ProjectError("Versão da biblioteca pinada em falta.")
    return ProjectResponse(
        id=project.id,
        name=project.name,
        template_version_id=project.template_version_id,
        template_code=template.code,
        template_version=template_version.version,
        intervention_type=project.intervention_type,
        library_version_id=pin.library_version_id,
        library_version=library_version.version,
    )


def list_templates(app_settings: AppSettings) -> list[TemplateResponse]:
    with workspace_session(app_settings) as (session, _paths):
        _ensure_templates(session)
        templates = list(session.scalars(select(ProjectTemplate).order_by(ProjectTemplate.code)))
        result: list[TemplateResponse] = []
        for template in templates:
            versions = list(
                session.scalars(
                    select(ProjectTemplateVersion)
                    .where(ProjectTemplateVersion.template_id == template.id)
                    .order_by(ProjectTemplateVersion.version)
                )
            )
            result.append(
                TemplateResponse(
                    id=template.id,
                    code=template.code,
                    name=template.name,
                    description=template.description,
                    versions=[
                        TemplateVersionResponse(
                            id=version.id,
                            template_id=template.id,
                            template_code=template.code,
                            template_name=template.name,
                            version=version.version,
                            metadata_json=version.metadata_json,
                        )
                        for version in versions
                    ],
                )
            )
        return result


def list_projects(app_settings: AppSettings) -> list[ProjectResponse]:
    with workspace_session(app_settings) as (session, _paths):
        _ensure_templates(session)
        projects = list(session.scalars(select(Project).order_by(Project.created_at)))
        return [_project_response(session, project) for project in projects]


def get_project(app_settings: AppSettings, project_id: str) -> ProjectResponse:
    with workspace_session(app_settings) as (session, _paths):
        _ensure_templates(session)
        project = session.get(Project, project_id)
        if project is None:
            raise ProjectError("Projeto não encontrado.")
        return _project_response(session, project)


def _parse_llm_context(raw: str) -> ProjectLlmContext:
    try:
        data = json.loads(raw or "{}")
    except json.JSONDecodeError:
        data = {}
    if not isinstance(data, dict):
        data = {}
    return ProjectLlmContext.model_validate(data)


def get_project_llm_context(app_settings: AppSettings, project_id: str) -> ProjectLlmContextResponse:
    with workspace_session(app_settings) as (session, _paths):
        project = session.get(Project, project_id)
        if project is None:
            raise ProjectError("Projeto não encontrado.")
        return ProjectLlmContextResponse(
            project_id=project.id,
            context=_parse_llm_context(project.llm_context_json),
        )


def patch_project_llm_context(
    app_settings: AppSettings, project_id: str, body: ProjectLlmContextPatch
) -> ProjectLlmContextResponse:
    with workspace_session(app_settings) as (session, _paths):
        project = session.get(Project, project_id)
        if project is None:
            raise ProjectError("Projeto não encontrado.")
        project.llm_context_json = json.dumps(
            body.context.model_dump(exclude_none=False),
            ensure_ascii=False,
            sort_keys=True,
        )
        session.flush()
        return ProjectLlmContextResponse(project_id=project.id, context=body.context)


def _template_ctbj_structure_version(metadata_json: str) -> int:
    try:
        meta = json.loads(metadata_json or "{}")
    except json.JSONDecodeError:
        return 0
    if not isinstance(meta, dict):
        return 0
    return int(meta.get("ctbj_structure_version") or 0)


def create_project(app_settings: AppSettings, body: ProjectCreateRequest) -> ProjectResponse:
    seed_ctbj = False
    project_id: str
    with workspace_session(app_settings) as (session, _paths):
        _ensure_templates(session)
        _ensure_library(session)
        template_version = session.get(ProjectTemplateVersion, body.template_version_id)
        if template_version is None:
            raise ProjectError("Versão do modelo inválida.")
        library_version = _current_library_version(session)
        project = Project(
            id=str(uuid.uuid4()),
            name=body.name.strip(),
            template_version_id=template_version.id,
            intervention_type=body.intervention_type.strip(),
            llm_context_json="{}",
            created_at=_utcnow(),
        )
        session.add(project)
        session.flush()
        session.add(
            ProjectLibraryPin(
                project_id=project.id,
                library_version_id=library_version.id,
                pinned_at=_utcnow(),
            )
        )
        session.flush()
        project_id = project.id
        seed_ctbj = _template_ctbj_structure_version(template_version.metadata_json) >= 3
        response = _project_response(session, project)

    if seed_ctbj:
        from app.services.structure_seed.ctbj_v3_sync import apply_ctbj_v3_structure

        apply_ctbj_v3_structure(
            app_settings,
            project_id,
            mode="seed_empty",
            dry_run=False,
            preserve_rich_content=True,
        )
    return response