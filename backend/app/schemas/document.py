from typing import Literal

from pydantic import BaseModel, Field

DocumentNodeType = Literal["fascicle", "block", "section", "subsection"]
MoveDirection = Literal["up", "down"]


class DocumentNodeCreateRequest(BaseModel):
    node_type: DocumentNodeType
    title: str = Field(min_length=1)
    parent_id: str | None = None


class DocumentNodeMoveRequest(BaseModel):
    direction: MoveDirection | None = None
    new_parent_id: str | None = None
    new_sort_key: int | None = None


class RenumberChange(BaseModel):
    node_id: str
    old_code: str | None
    new_code: str


class DocumentNodeResponse(BaseModel):
    id: str
    project_id: str
    parent_id: str | None
    node_type: str
    title: str
    sort_key: int
    depth: int
    display_code: str
    depth_warning: bool


class DocumentNodeListResponse(BaseModel):
    nodes: list[DocumentNodeResponse]
    renumber_changes: list[RenumberChange] = Field(default_factory=list)


class DocumentNodeMutationResponse(BaseModel):
    node: DocumentNodeResponse
    renumber_changes: list[RenumberChange] = Field(default_factory=list)


class AssociationCreateRequest(BaseModel):
    knowledge_item_id: str = Field(min_length=1)
    role: str = Field(min_length=1)
    usage_instruction: str | None = None
    pinned_revision_num: int | None = None


class AssociationResponse(BaseModel):
    id: str
    document_node_id: str
    knowledge_item_id: str
    role: str
    sort_order: int
    usage_instruction: str | None
    pinned_revision_num: int | None