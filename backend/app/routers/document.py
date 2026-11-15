from fastapi import APIRouter, HTTPException

from app.deps import get_settings
from app.schemas.document import (
    AssociationCreateRequest,
    AssociationResponse,
    DocumentNodeCreateRequest,
    DocumentNodeListResponse,
    DocumentNodeMoveRequest,
    DocumentNodeMutationResponse,
)
from app.services.deletion_service import delete_document_association, delete_document_node
from app.services.document_service import (
    DocumentError,
    create_association,
    create_document_node,
    list_associations,
    list_document_nodes,
    move_document_node,
)
from app.services.workspace_service import WorkspaceError

router = APIRouter(tags=["document"])


def _run(action):
    try:
        return action()
    except WorkspaceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except DocumentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/projects/{project_id}/document-nodes", response_model=DocumentNodeListResponse)
def document_nodes_list(project_id: str) -> DocumentNodeListResponse:
    return _run(lambda: list_document_nodes(get_settings(), project_id))


@router.post("/projects/{project_id}/document-nodes", response_model=DocumentNodeMutationResponse)
def document_nodes_create(project_id: str, body: DocumentNodeCreateRequest) -> DocumentNodeMutationResponse:
    return _run(lambda: create_document_node(get_settings(), project_id, body))


@router.post(
    "/projects/{project_id}/document-nodes/{node_id}/move",
    response_model=DocumentNodeMutationResponse,
)
def document_nodes_move(
    project_id: str, node_id: str, body: DocumentNodeMoveRequest
) -> DocumentNodeMutationResponse:
    return _run(lambda: move_document_node(get_settings(), project_id, node_id, body))


@router.get("/document-nodes/{node_id}/associations", response_model=list[AssociationResponse])
def document_associations_list(node_id: str) -> list[AssociationResponse]:
    return _run(lambda: list_associations(get_settings(), node_id))


@router.post("/document-nodes/{node_id}/associations", response_model=AssociationResponse)
def document_associations_create(node_id: str, body: AssociationCreateRequest) -> AssociationResponse:
    return _run(lambda: create_association(get_settings(), node_id, body))


@router.delete("/projects/{project_id}/document-nodes/{node_id}", status_code=204)
def document_nodes_delete(project_id: str, node_id: str) -> None:
    _run(lambda: delete_document_node(get_settings(), project_id, node_id))


@router.delete("/document-nodes/associations/{association_id}", status_code=204)
def document_associations_delete(association_id: str) -> None:
    _run(lambda: delete_document_association(get_settings(), association_id))