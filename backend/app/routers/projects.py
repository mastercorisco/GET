from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import OperationalError

from app.deps import get_settings
from app.schemas.project import (
    ProjectCreateRequest,
    ProjectLlmContextPatch,
    ProjectLlmContextResponse,
    ProjectResponse,
    TemplateResponse,
)
from app.services.deletion_service import delete_project
from app.services.project_service import (
    ProjectError,
    create_project,
    get_project,
    get_project_llm_context,
    list_projects,
    list_templates,
    patch_project_llm_context,
)
from app.services.workspace_exclusivity import WorkspaceExclusiveError
from app.services.workspace_service import WorkspaceError

router = APIRouter(prefix="/projects", tags=["projects"])


def _run(action, *, route: str = ""):
    try:
        return action()
    except (WorkspaceError, WorkspaceExclusiveError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ProjectError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except OperationalError as exc:
        if route == "project_delete":
            raise HTTPException(
                status_code=503,
                detail=(
                    "Base de dados ocupada (SQLite). Feche outras janelas do GET, confirme que não há "
                    "scripts Python antigos a usar o mesmo workspace, reinicie o uvicorn e tente de novo."
                ),
            ) from exc
        raise
    except Exception:
        raise


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


@router.get("/{project_id}/llm-context", response_model=ProjectLlmContextResponse)
def project_llm_context_get(project_id: str) -> ProjectLlmContextResponse:
    return _run(lambda: get_project_llm_context(get_settings(), project_id))


@router.patch("/{project_id}/llm-context", response_model=ProjectLlmContextResponse)
def project_llm_context_patch(project_id: str, body: ProjectLlmContextPatch) -> ProjectLlmContextResponse:
    return _run(lambda: patch_project_llm_context(get_settings(), project_id, body))


@router.delete("/{project_id}", status_code=204)
def project_delete(project_id: str) -> None:
    _run(lambda: delete_project(get_settings(), project_id), route="project_delete")