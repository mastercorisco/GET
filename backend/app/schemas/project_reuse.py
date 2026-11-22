from __future__ import annotations

from pydantic import BaseModel, Field


class PointCitationSnippet(BaseModel):
    point_id: str
    point_title: str
    block_code: str | None = None
    status: str


class DecisionCitationRow(BaseModel):
    item_id: str
    title: str
    scope_type: str
    citation_count: int
    distinct_point_count: int
    distinct_block_count: int
    f3_criterion_met: bool
    citations: list[PointCitationSnippet] = Field(default_factory=list)


class DecisionReuseSection(BaseModel):
    project_id: str
    decision_count: int
    decisions: list[DecisionCitationRow] = Field(default_factory=list)
    f3_criterion_met_count: int
    uncited_decision_count: int
    f3_pilot_ready: bool
    non_decision_knowledge_refs: list[dict] = Field(default_factory=list)


class ReferenceCitationRow(BaseModel):
    reference_id: str
    title: str
    scope_type: str
    citation: str | None = None
    citation_count: int
    distinct_point_count: int
    distinct_block_count: int
    m3_criterion_met: bool
    citations: list[PointCitationSnippet] = Field(default_factory=list)


class ReferenceReuseSection(BaseModel):
    project_id: str
    reference_count: int
    references: list[ReferenceCitationRow] = Field(default_factory=list)
    m3_criterion_met_count: int
    uncited_reference_count: int
    m3_reuse_ready: bool
    unknown_reference_ids: list[dict] = Field(default_factory=list)


class ProjectReuseReportResponse(BaseModel):
    project_id: str
    decisions: DecisionReuseSection
    references: ReferenceReuseSection
    f3_pilot_ready: bool
    m3_reuse_ready: bool
    reuse_pilot_ready: bool