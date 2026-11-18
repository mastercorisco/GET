from fastapi import APIRouter, HTTPException

from app import __version__
from app.deps import get_settings
from app.services.workspace_service import WorkspaceError, workspace_preflight

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "version": __version__,
        "features": "baseline,export,import,workbook",
    }


@router.get("/health/workspace")
def health_workspace() -> dict:
    try:
        return workspace_preflight(get_settings())
    except WorkspaceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc