from typing import Literal

from pydantic import BaseModel, Field

KnowledgeType = Literal[
    "fact",
    "principle",
    "requirement",
    "decision",
    "rationale",
    "example",
    "recommendation",
    "open_question",
    "exclusion",
    "authoring_instruction",
    "unclassified",
]
Maturity = Literal["captured", "structured", "reviewed", "mature"]
Approval = Literal["unreviewed", "proposed", "confirmed", "approved", "rejected"]
Lifecycle = Literal["active", "superseded", "withdrawn", "archived"]
ScopeType = Literal["library"]


class KnowledgeCreateRequest(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    origin_context: str = Field(min_length=1)
    knowledge_type: KnowledgeType = "unclassified"
    human_code: str | None = None
    maturity: Maturity = "captured"
    approval: Approval = "unreviewed"
    lifecycle: Lifecycle = "active"


class DraftUpdateRequest(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    origin_context: str = Field(min_length=1)
    knowledge_type: KnowledgeType = "unclassified"
    maturity: Maturity = "captured"
    approval: Approval = "unreviewed"
    lifecycle: Lifecycle = "active"


class RelationCreateRequest(BaseModel):
    source_item_id: str = Field(min_length=1)
    target_item_id: str = Field(min_length=1)
    relation_type: str = Field(min_length=1)


class RevisionResponse(BaseModel):
    id: str
    revision_num: int
    title: str
    content: str
    origin_context: str
    knowledge_type: str
    maturity: str
    approval: str
    lifecycle: str


class RelationResponse(BaseModel):
    id: str
    relation_type: str
    source_item_id: str
    target_item_id: str


class KnowledgeResponse(BaseModel):
    id: str
    scope_type: ScopeType
    scope_id: str
    human_code: str | None
    title: str
    content: str
    origin_context: str
    knowledge_type: str
    maturity: str
    approval: str
    lifecycle: str
    status_label: str
    revision_count: int
    latest_revision_num: int | None
    revisions: list[RevisionResponse] = Field(default_factory=list)
    relations: list[RelationResponse] = Field(default_factory=list)
