from fastapi import APIRouter, HTTPException

from app.deps import get_settings
from app.schemas.technical import (
    TechnicalClassCreateRequest,
    TechnicalClassResponse,
    TechnicalInstanceCreateRequest,
    TechnicalInstanceResponse,
)
from app.services.technical_service import (
    TechnicalError,
    create_class,
    create_instance,
    list_classes,
    list_instances,
)
from app.services.workspace_service import WorkspaceError

router = APIRouter(tags=["technical"])


def _run(action):
    try:
        return action()
    except WorkspaceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except TechnicalError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/technical/classes", response_model=list[TechnicalClassResponse])
def technical_classes() -> list[TechnicalClassResponse]:
    return _run(lambda: list_classes(get_settings()))


@router.post("/technical/classes", response_model=TechnicalClassResponse)
def technical_class_create(body: TechnicalClassCreateRequest) -> TechnicalClassResponse:
    return _run(lambda: create_class(get_settings(), body))


@router.get("/projects/{project_id}/instances", response_model=list[TechnicalInstanceResponse])
def technical_instances(project_id: str) -> list[TechnicalInstanceResponse]:
    return _run(lambda: list_instances(get_settings(), project_id))


@router.post("/projects/{project_id}/instances", response_model=TechnicalInstanceResponse)
def technical_instance_create(
    project_id: str,
    body: TechnicalInstanceCreateRequest,
) -> TechnicalInstanceResponse:
    return _run(lambda: create_instance(get_settings(), project_id, body))