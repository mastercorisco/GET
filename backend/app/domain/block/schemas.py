from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

LlmFreedom = Literal["strict", "bounded", "exploratory"]
PointStatus = Literal["draft", "incomplete", "ready", "approved", "obsolete"]
PremiseImportance = Literal["mandatory", "recommended", "informative"]
PremiseSourceType = Literal[
    "project_decision",
    "eda_philosophy",
    "functional_requirement",
    "standard",
    "existing_document",
    "operational_experience",
    "technical_recommendation",
    "unconfirmed_information",
]
PremiseConfidence = Literal["confirmed", "provisional", "unverified"]
OwnerKind = Literal["project", "fascicle", "block", "development_point"]
HelpLevel = Literal["essential", "normal", "detailed"]
ValidationSeverity = Literal["error", "warning", "suggestion"]


class PointLists(BaseModel):
    development_guidance: list[str] = Field(default_factory=list)
    perspectives: list[str] = Field(default_factory=list)
    questions_to_answer: list[dict[str, Any]] = Field(default_factory=list)
    must_include: list[dict[str, Any]] = Field(default_factory=list)
    limits_and_exclusions: list[dict[str, Any]] = Field(default_factory=list)
    examples: list[dict[str, Any]] = Field(default_factory=list)
    open_questions: list[dict[str, Any]] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    knowledge_item_ids: list[str] = Field(default_factory=list)
    reference_ids: list[str] = Field(default_factory=list)


class ValidationIssue(BaseModel):
    code: str
    message: str
    severity: ValidationSeverity
    point_id: str | None = None
    field: str | None = None


class BlockHeaderPatch(BaseModel):
    title: str | None = None
    objective: str | None = None
    scope: str | None = None
    target_output: dict[str, Any] | None = None
    block_status: str | None = None


class BlockHeaderResponse(BaseModel):
    id: str
    project_id: str
    fascicle_id: str | None
    display_code: str
    title: str
    objective: str
    scope: str
    target_output: dict[str, Any]
    block_status: str


class PointSummary(BaseModel):
    id: str
    order: int
    title: str
    status: str
    llm_freedom: str
    needs_review: bool
    premise_count: int
    must_include_count: int
    open_questions_count: int
    acceptance_criteria_count: int
    completeness_alerts: list[str] = Field(default_factory=list)


class BlockDetailResponse(BaseModel):
    block: BlockHeaderResponse
    points: list[PointSummary]


class DevelopmentPointCreate(BaseModel):
    title: str = ""
    template_id: str | None = None


class DevelopmentPointPatch(BaseModel):
    title: str | None = None
    core_idea: str | None = None
    intended_outcome: str | None = None
    llm_freedom: LlmFreedom | None = None
    status: PointStatus | None = None
    lists: PointLists | None = None


class DevelopmentPointResponse(BaseModel):
    id: str
    block_id: str
    order: int
    title: str
    core_idea: str
    intended_outcome: str
    llm_freedom: str
    status: str
    template_id: str | None
    needs_review: bool
    lists: PointLists
    validation_issues: list[ValidationIssue] = Field(default_factory=list)


class PointReorderRequest(BaseModel):
    point_ids: list[str] = Field(min_length=1)


class PointMoveRequest(BaseModel):
    target_block_id: str


class PremiseCreate(BaseModel):
    owner_kind: OwnerKind
    owner_id: str
    statement: str = Field(min_length=1)
    importance: PremiseImportance
    source_type: PremiseSourceType
    confidence: PremiseConfidence
    reference_id: str | None = None
    notes: str | None = None


class PremisePatch(BaseModel):
    statement: str | None = None
    importance: PremiseImportance | None = None
    source_type: PremiseSourceType | None = None
    confidence: PremiseConfidence | None = None
    reference_id: str | None = None
    notes: str | None = None


class PremiseResponse(BaseModel):
    id: str
    owner_kind: str
    owner_id: str
    statement: str
    importance: str
    source_type: str
    confidence: str
    reference_id: str | None
    notes: str | None


class BlockValidationResponse(BaseModel):
    issues: list[ValidationIssue]


class ExchangePackageOptions(BaseModel):
    include_draft: bool = False


class ExchangePackageWriteResponse(BaseModel):
    file_path: str
    markdown_path: str
    package_id: str


class WorkspacePreferencesPatch(BaseModel):
    help_level: HelpLevel | None = None


class WorkspacePreferencesResponse(BaseModel):
    help_level: str