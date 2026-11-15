from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import OperationalError

from app.deps import get_settings
from app.schemas.project import ProjectCreateRequest, ProjectResponse, TemplateResponse
from app.services.deletion_service import delete_project
from app.services.project_service import ProjectError, create_project, get_project, list_projects, list_templates
from app.services.workspace_service import WorkspaceError

router = APIRouter(prefix="/projects", tags=["projects"])


def _run(action, *, route: str = ""):
    try:
        return action()
    except WorkspaceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ProjectError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except OperationalError as exc:
        if route == "project_delete":
            from app.debug_agent_log import agent_debug_log

            agent_debug_log(
                location="projects.py:project_delete",
                message="OperationalError on delete",
                data={"error": str(exc)[:500]},
                hypothesis_id="D",
            )
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


@router.delete("/{project_id}", status_code=204)
def project_delete(project_id: str) -> None:
    _run(lambda: delete_project(get_settings(), project_id), route="project_delete")