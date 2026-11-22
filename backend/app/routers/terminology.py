from fastapi import APIRouter, HTTPException, Query

from app.deps import get_settings
from app.schemas.terminology import (
    TerminologyCreateRequest,
    TerminologyOverrideCreateRequest,
    TerminologyOverrideResponse,
    TerminologyResponse,
    TerminologySearchHit,
    TerminologyUpdateRequest,
)
from app.services.deletion_service import delete_terminology, delete_terminology_override
from app.services.terminology_service import (
    TerminologyError,
    create_terminology,
    create_terminology_override,
    get_terminology,
    list_terminology,
    list_terminology_overrides,
    search_terminology,
    update_terminology,
)
from app.services.workspace_service import WorkspaceError

router = APIRouter(tags=["terminology"])


def _run(action):
    try:
        return action()
    except WorkspaceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except TerminologyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/terminology", response_model=list[TerminologyResponse])
def terminology_list(
    scope_type: str = Query(default="library"),
    scope_id: str | None = Query(default=None),
) -> list[TerminologyResponse]:
    return _run(lambda: list_terminology(get_settings(), scope_type, scope_id))


@router.get("/terminology/search", response_model=list[TerminologySearchHit])
def terminology_search(
    q: str = Query(min_length=1),
    project_id: str | None = Query(default=None),
    scope_type: str = Query(default="library"),
    scope_id: str | None = Query(default=None),
) -> list[TerminologySearchHit]:
    return _run(
        lambda: search_terminology(
            get_settings(),
            q,
            project_id=project_id,
            scope_type=scope_type,
            scope_id=scope_id,
        )
    )


@router.post("/terminology", response_model=TerminologyResponse)
def terminology_create(body: TerminologyCreateRequest) -> TerminologyResponse:
    return _run(lambda: create_terminology(get_settings(), body))


@router.get("/terminology/{concept_id}", response_model=TerminologyResponse)
def terminology_get(concept_id: str) -> TerminologyResponse:
    return _run(lambda: get_terminology(get_settings(), concept_id))


@router.patch("/terminology/{concept_id}", response_model=TerminologyResponse)
def terminology_update(concept_id: str, body: TerminologyUpdateRequest) -> TerminologyResponse:
    return _run(lambda: update_terminology(get_settings(), concept_id, body))


@router.get(
    "/projects/{project_id}/terminology-overrides",
    response_model=list[TerminologyOverrideResponse],
)
def terminology_overrides_list(project_id: str) -> list[TerminologyOverrideResponse]:
    return _run(lambda: list_terminology_overrides(get_settings(), project_id))


@router.post(
    "/projects/{project_id}/terminology-overrides",
    response_model=TerminologyOverrideResponse,
)
def terminology_overrides_create(
    project_id: str, body: TerminologyOverrideCreateRequest
) -> TerminologyOverrideResponse:
    return _run(lambda: create_terminology_override(get_settings(), project_id, body))


@router.delete("/terminology/{concept_id}", status_code=204)
def terminology_delete(concept_id: str, confirm: bool = Query(default=False)) -> None:
    _run(lambda: delete_terminology(get_settings(), concept_id, confirm=confirm))


@router.delete(
    "/projects/{project_id}/terminology-overrides/{override_id}",
    status_code=204,
)
def terminology_override_delete(
    project_id: str, override_id: str, confirm: bool = Query(default=False)
) -> None:
    _run(lambda: delete_terminology_override(get_settings(), project_id, override_id, confirm=confirm))