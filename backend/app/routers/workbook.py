from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse, Response

from app.deps import get_settings
from app.schemas.workbook import WorkbookApplyRequest, WorkbookApplyResponse, WorkbookMigrateResponse
from app.services.workbook.api import WorkbookApiError, apply_workbook_migration, load_migration_report, migrate_workbook_upload
from app.services.workbook.template_builder import (
    TEMPLATE_IDS,
    build_workbook_template,
    template_filename,
)
from app.services.workbook.validate import validate_workbook_bytes
from app.services.workspace_service import WorkspaceError

router = APIRouter(tags=["workbook"])


def _workspace_http(exc: WorkspaceError) -> HTTPException:
    return HTTPException(status_code=409, detail=str(exc))


def _api_http(exc: WorkbookApiError) -> HTTPException:
    return HTTPException(status_code=exc.http_status, detail=str(exc))


@router.get("/workbook/templates/{template_id}")
def download_template(template_id: str) -> Response:
    if template_id not in TEMPLATE_IDS:
        raise HTTPException(status_code=404, detail="Template não encontrado.")
    data = build_workbook_template(template_id)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{template_filename(template_id)}"'},
    )


@router.post("/workbook/validate")
async def validate_workbook(file: UploadFile = File(...)) -> dict:
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Envie um ficheiro .xlsx.")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Ficheiro vazio.")
    return validate_workbook_bytes(data)


@router.post("/workbook/migrate", response_model=WorkbookMigrateResponse)
async def migrate_workbook(
    file: UploadFile = File(...),
    dry_run: bool = Form(default=True),
) -> WorkbookMigrateResponse:
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Envie um ficheiro .xlsx.")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Ficheiro vazio.")
    settings = get_settings()
    try:
        if not dry_run:
            raise HTTPException(
                status_code=400,
                detail="Use dry_run=true na pré-importação; aplique via POST /workbook/migrate/apply.",
            )
        return migrate_workbook_upload(settings, data, file.filename or "workbook.xlsx", dry_run=True)
    except WorkspaceError as exc:
        raise _workspace_http(exc) from exc
    except WorkbookApiError as exc:
        raise _api_http(exc) from exc


@router.post("/workbook/migrate/apply", response_model=WorkbookApplyResponse)
def migrate_apply(body: WorkbookApplyRequest) -> WorkbookApplyResponse:
    settings = get_settings()
    try:
        return apply_workbook_migration(
            settings,
            body.run_id,
            confirm=body.confirm,
            target=body.target,
            project_id=body.project_id,
        )
    except WorkspaceError as exc:
        raise _workspace_http(exc) from exc
    except WorkbookApiError as exc:
        raise _api_http(exc) from exc


@router.get("/workbook/migration-reports/{run_id}")
def get_migration_report(run_id: str) -> JSONResponse:
    settings = get_settings()
    try:
        report = load_migration_report(settings, run_id)
    except WorkspaceError as exc:
        raise _workspace_http(exc) from exc
    except WorkbookApiError as exc:
        raise _api_http(exc) from exc
    return JSONResponse(content=report)