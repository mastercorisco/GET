from fastapi import APIRouter, HTTPException, Query

from app.deps import get_settings
from app.schemas.reference import (
    ReferenceCreateRequest,
    ReferenceResponse,
    ReferenceUpdateRequest,
    StandardProfileUpsertRequest,
)
from app.services.deletion_service import delete_reference
from app.services.reference_service import (
    ReferenceError,
    create_reference,
    get_reference,
    list_references,
    update_reference,
    upsert_standard_profile,
)
from app.services.workspace_service import WorkspaceError

router = APIRouter(prefix="/references", tags=["references"])


def _run(action):
    try:
        return action()
    except WorkspaceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ReferenceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[ReferenceResponse])
def references_list(
    scope_type: str = Query(default="library"),
    scope_id: str | None = Query(default=None),
) -> list[ReferenceResponse]:
    return _run(lambda: list_references(get_settings(), scope_type, scope_id))


@router.post("", response_model=ReferenceResponse)
def references_create(body: ReferenceCreateRequest) -> ReferenceResponse:
    return _run(lambda: create_reference(get_settings(), body))


@router.get("/{reference_id}", response_model=ReferenceResponse)
def references_get(reference_id: str) -> ReferenceResponse:
    return _run(lambda: get_reference(get_settings(), reference_id))


@router.patch("/{reference_id}", response_model=ReferenceResponse)
def references_update(reference_id: str, body: ReferenceUpdateRequest) -> ReferenceResponse:
    return _run(lambda: update_reference(get_settings(), reference_id, body))


@router.put("/{reference_id}/standard-profile", response_model=ReferenceResponse)
def references_standard_profile(
    reference_id: str, body: StandardProfileUpsertRequest
) -> ReferenceResponse:
    return _run(lambda: upsert_standard_profile(get_settings(), reference_id, body))


@router.delete("/{reference_id}", status_code=204)
def references_delete(reference_id: str) -> None:
    _run(lambda: delete_reference(get_settings(), reference_id))