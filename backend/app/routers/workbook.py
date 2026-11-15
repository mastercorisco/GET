from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from app.services.workbook.template_builder import (
    TEMPLATE_IDS,
    build_workbook_template,
    template_filename,
)
from app.services.workbook.validate import validate_workbook_bytes

router = APIRouter(tags=["workbook"])


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