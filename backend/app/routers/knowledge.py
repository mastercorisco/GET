from fastapi import APIRouter, HTTPException, Query

from app.deps import get_settings
from app.schemas.knowledge import (
    DraftUpdateRequest,
    KnowledgeCreateRequest,
    KnowledgeResponse,
    RelationCreateRequest,
    RelationResponse,
)
from app.services.knowledge_service import (
    KnowledgeError,
    conclude_revision,
    create_item,
    create_relation,
    get_item,
    list_items,
    search_items,
    update_draft,
)
from app.services.workspace_service import WorkspaceError

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


def _run(action):
    try:
        return action()
    except WorkspaceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except KnowledgeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[KnowledgeResponse])
def knowledge_list() -> list[KnowledgeResponse]:
    return _run(lambda: list_items(get_settings()))


@router.get("/search", response_model=list[KnowledgeResponse])
def knowledge_search(
    q: str = Query(min_length=1),
    scope_type: str = Query(default="library"),
) -> list[KnowledgeResponse]:
    return _run(lambda: search_items(get_settings(), q, scope_type))


@router.post("", response_model=KnowledgeResponse)
def knowledge_create(body: KnowledgeCreateRequest) -> KnowledgeResponse:
    return _run(lambda: create_item(get_settings(), body))


@router.post("/relations", response_model=RelationResponse)
def knowledge_relate(body: RelationCreateRequest) -> RelationResponse:
    return _run(lambda: create_relation(get_settings(), body))


@router.get("/{item_id}", response_model=KnowledgeResponse)
def knowledge_get(item_id: str) -> KnowledgeResponse:
    return _run(lambda: get_item(get_settings(), item_id))


@router.patch("/{item_id}/draft", response_model=KnowledgeResponse)
def knowledge_update_draft(item_id: str, body: DraftUpdateRequest) -> KnowledgeResponse:
    return _run(lambda: update_draft(get_settings(), item_id, body))


@router.post("/{item_id}/conclude", response_model=KnowledgeResponse)
def knowledge_conclude(item_id: str) -> KnowledgeResponse:
    return _run(lambda: conclude_revision(get_settings(), item_id))
