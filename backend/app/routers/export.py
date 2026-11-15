from fastapi import APIRouter, HTTPException

from app.deps import get_settings
from app.schemas.export import ExportRecordResponse, FascicleExportRequest, MasterExportRequest
from app.services.export_service import ExportError, export_fascicle, export_master, list_exports
from app.services.workspace_service import WorkspaceError

router = APIRouter(tags=["export"])


def _run(action):
    try:
        return action()
    except WorkspaceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ExportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/projects/{project_id}/exports", response_model=list[ExportRecordResponse])
def exports_list(project_id: str) -> list[ExportRecordResponse]:
    return _run(lambda: list_exports(get_settings(), project_id))


@router.post("/projects/{project_id}/exports/master", response_model=ExportRecordResponse)
def exports_master(project_id: str, body: MasterExportRequest) -> ExportRecordResponse:
    return _run(lambda: export_master(get_settings(), project_id, body))


@router.post(
    "/projects/{project_id}/exports/fascicle/{fascicle_node_id}",
    response_model=ExportRecordResponse,
)
def exports_fascicle(
    project_id: str, fascicle_node_id: str, body: FascicleExportRequest
) -> ExportRecordResponse:
    return _run(lambda: export_fascicle(get_settings(), project_id, fascicle_node_id, body))