from fastapi import APIRouter, HTTPException, Query

from app.deps import get_settings
from app.domain.block import catalogs, service
from app.domain.block.schemas import (
    BlockDetailResponse,
    BlockHeaderPatch,
    BlockHeaderResponse,
    BlockValidationResponse,
    DevelopmentPointCreate,
    DevelopmentPointPatch,
    DevelopmentPointResponse,
    ExchangePackageWriteResponse,
    PointMoveRequest,
    PointReorderRequest,
    PremiseCreate,
    PremisePatch,
    PremiseResponse,
    WorkspacePreferencesPatch,
    WorkspacePreferencesResponse,
)
from app.services.workspace_service import WorkspaceError

router = APIRouter(tags=["block"])


def _run(action):
    try:
        return action()
    except WorkspaceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except service.BlockError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/blocks/{block_id}", response_model=BlockDetailResponse)
def block_get(block_id: str) -> BlockDetailResponse:
    return _run(lambda: service.get_block_detail(get_settings(), block_id))


@router.patch("/blocks/{block_id}", response_model=BlockHeaderResponse)
def block_patch(block_id: str, body: BlockHeaderPatch) -> BlockHeaderResponse:
    return _run(lambda: service.patch_block(get_settings(), block_id, body))


@router.post("/blocks/{block_id}/development-points", response_model=DevelopmentPointResponse)
def point_create(block_id: str, body: DevelopmentPointCreate) -> DevelopmentPointResponse:
    return _run(lambda: service.create_point(get_settings(), block_id, body))


@router.get("/development-points/{point_id}", response_model=DevelopmentPointResponse)
def point_get(point_id: str) -> DevelopmentPointResponse:
    return _run(lambda: service.get_point(get_settings(), point_id))


@router.patch("/development-points/{point_id}", response_model=DevelopmentPointResponse)
def point_patch(point_id: str, body: DevelopmentPointPatch) -> DevelopmentPointResponse:
    return _run(lambda: service.patch_point(get_settings(), point_id, body))


@router.delete("/development-points/{point_id}", status_code=204)
def point_delete(point_id: str) -> None:
    _run(lambda: service.delete_point(get_settings(), point_id))


@router.post("/development-points/{point_id}/duplicate", response_model=DevelopmentPointResponse)
def point_duplicate(point_id: str) -> DevelopmentPointResponse:
    return _run(lambda: service.duplicate_point(get_settings(), point_id))


@router.post("/development-points/{point_id}/archive", response_model=DevelopmentPointResponse)
def point_archive(point_id: str) -> DevelopmentPointResponse:
    return _run(lambda: service.archive_point(get_settings(), point_id))


@router.post("/development-points/{point_id}/move", response_model=DevelopmentPointResponse)
def point_move(point_id: str, body: PointMoveRequest) -> DevelopmentPointResponse:
    return _run(lambda: service.move_point(get_settings(), point_id, body.target_block_id))


@router.post("/blocks/{block_id}/development-points/reorder", response_model=BlockDetailResponse)
def points_reorder(block_id: str, body: PointReorderRequest) -> BlockDetailResponse:
    return _run(lambda: service.reorder_points(get_settings(), block_id, body.point_ids))


@router.get("/premises", response_model=list[PremiseResponse])
def premises_list(
    owner_kind: str = Query(min_length=1),
    owner_id: str = Query(min_length=1),
) -> list[PremiseResponse]:
    return _run(lambda: service.list_premises(get_settings(), owner_kind, owner_id))


@router.post("/premises", response_model=PremiseResponse)
def premise_create(body: PremiseCreate) -> PremiseResponse:
    return _run(lambda: service.create_premise(get_settings(), body))


@router.patch("/premises/{premise_id}", response_model=PremiseResponse)
def premise_patch(premise_id: str, body: PremisePatch) -> PremiseResponse:
    return _run(lambda: service.patch_premise(get_settings(), premise_id, body))


@router.delete("/premises/{premise_id}", status_code=204)
def premise_delete(premise_id: str) -> None:
    _run(lambda: service.delete_premise(get_settings(), premise_id))


@router.get("/blocks/{block_id}/validation", response_model=BlockValidationResponse)
def block_validation(block_id: str) -> BlockValidationResponse:
    return _run(lambda: service.validate_block(get_settings(), block_id))


@router.get("/blocks/{block_id}/exchange-package")
def exchange_preview(
    block_id: str,
    include_draft: bool = Query(default=False),
) -> dict:
    return _run(lambda: service.preview_exchange(get_settings(), block_id, include_draft))


@router.post("/blocks/{block_id}/exchange-package", response_model=ExchangePackageWriteResponse)
def exchange_write(
    block_id: str,
    include_draft: bool = Query(default=False),
) -> ExchangePackageWriteResponse:
    path, package_id = _run(
        lambda: service.write_exchange(get_settings(), block_id, include_draft)
    )
    return ExchangePackageWriteResponse(file_path=path, package_id=package_id)


@router.get("/catalogs/help")
def catalog_help() -> dict:
    return catalogs.help_catalog()


@router.get("/catalogs/development-point-templates")
def catalog_templates() -> dict:
    return catalogs.development_point_templates()


@router.get("/workspace/preferences", response_model=WorkspacePreferencesResponse)
def workspace_preferences_get() -> WorkspacePreferencesResponse:
    return _run(
        lambda: WorkspacePreferencesResponse(help_level=service.get_help_level(get_settings()))
    )


@router.patch("/workspace/preferences", response_model=WorkspacePreferencesResponse)
def workspace_preferences_patch(body: WorkspacePreferencesPatch) -> WorkspacePreferencesResponse:
    level = _run(lambda: service.patch_preferences(get_settings(), body.help_level))
    return WorkspacePreferencesResponse(help_level=level)