from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.deps import get_settings
from app.schemas.structure_export import StructureExportRequest
from app.services.structure_export.collect import StructureExportError
from app.services.structure_export.orchestrate import export_document_structure
from app.services.workspace_service import WorkspaceError

router = APIRouter(tags=["structure-export"])


@router.post("/projects/{project_id}/document-structure/export")
def export_structure(project_id: str, body: StructureExportRequest) -> Response:
    settings = get_settings()
    try:
        payload, file_name, media_type, _meta = export_document_structure(settings, project_id, body)
    except WorkspaceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except StructureExportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return Response(
        content=payload,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )