from fastapi import APIRouter, HTTPException

from app.deps import get_settings
from app.schemas.project import ProjectCreateRequest, ProjectResponse, TemplateResponse
from app.services.project_service import ProjectError, create_project, get_project, list_projects, list_templates
from app.services.workspace_service import WorkspaceError

router = APIRouter(prefix="/projects", tags=["projects"])


def _run(action):
    try:
        return action()
    except WorkspaceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ProjectError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/templates", response_model=list[TemplateResponse])
def project_templates() -> list[TemplateResponse]:
    return _run(lambda: list_templates(get_settings()))


@router.get("", response_model=list[ProjectResponse])
def project_list() -> list[ProjectResponse]:
    return _run(lambda: list_projects(get_settings()))


@router.post("", response_model=ProjectResponse)
def project_create(body: ProjectCreateRequest) -> ProjectResponse:
    return _run(lambda: create_project(get_settings(), body))


@router.get("/{project_id}", response_model=ProjectResponse)
def project_get(project_id: str) -> ProjectResponse:
    return _run(lambda: get_project(get_settings(), project_id))