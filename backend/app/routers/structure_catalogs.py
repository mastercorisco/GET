from __future__ import annotations

import json
from pathlib import Path

import jsonschema
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, Response

from app.schemas.structure_catalog_api import StructureCatalogListResponse, StructureCatalogSummary
from app.services.structure_seed.bootstrap_contract import build_bootstrap_contract
from app.services.structure_seed.registry import get_registry_entry, list_catalog_summaries
from app.services.workbook.catalog_structure_xlsx import build_workbook_structure_from_catalog

REPO_ROOT = Path(__file__).resolve().parents[3]
CONTRACT_SCHEMA_PATH = REPO_ROOT / "schemas" / "get_structure_contract.schema.json"

router = APIRouter(tags=["structure-catalogs"])


def _contract_schema() -> dict:
    return json.loads(CONTRACT_SCHEMA_PATH.read_text(encoding="utf-8"))


@router.get("/structure-catalogs", response_model=StructureCatalogListResponse)
def structure_catalog_list() -> StructureCatalogListResponse:
    rows = list_catalog_summaries()
    return StructureCatalogListResponse(
        catalogs=[StructureCatalogSummary.model_validate(row) for row in rows]
    )


@router.get("/structure-catalogs/{catalog_id}/bootstrap-contract")
def structure_catalog_bootstrap_contract(catalog_id: str) -> JSONResponse:
    try:
        get_registry_entry(catalog_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    body = build_bootstrap_contract(catalog_id)
    jsonschema.validate(instance=body, schema=_contract_schema())
    return JSONResponse(content=body)


@router.get("/structure-catalogs/{catalog_id}/workbook-structure.xlsx")
def structure_catalog_workbook(catalog_id: str) -> Response:
    try:
        get_registry_entry(catalog_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    data = build_workbook_structure_from_catalog(catalog_id)
    filename = f"structure_{catalog_id}.xlsx"
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )