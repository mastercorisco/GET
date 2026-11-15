from fastapi import APIRouter, HTTPException

from app.deps import get_settings
from app.schemas.workspace import WorkspaceCreateRequest, WorkspaceOpenRequest, WorkspaceResponse
from app.services.workspace_service import WorkspaceError, create_workspace, get_current_workspace, open_workspace

router = APIRouter(prefix="/workspace", tags=["workspace"])


@router.get("", response_model=WorkspaceResponse | None)
def current_workspace() -> WorkspaceResponse | None:
    return get_current_workspace(get_settings())


@router.post("/create", response_model=WorkspaceResponse)
def workspace_create(body: WorkspaceCreateRequest) -> WorkspaceResponse:
    try:
        return create_workspace(get_settings(), body.root_path, body.local_user_name)
    except WorkspaceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/open", response_model=WorkspaceResponse)
def workspace_open(body: WorkspaceOpenRequest) -> WorkspaceResponse:
    try:
        return open_workspace(get_settings(), body.root_path)
    except WorkspaceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc