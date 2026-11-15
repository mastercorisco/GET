from typing import Literal

from pydantic import BaseModel, Field

ContractualRole = Literal[
    "informative_reference",
    "design_basis",
    "contractual_requirement",
    "compliance_target",
    "guidance_only",
]
ScopeType = Literal["library", "project"]


class ReferenceCreateRequest(BaseModel):
    scope_type: ScopeType
    scope_id: str | None = None
    title: str = Field(min_length=1)
    citation: str | None = None
    notes: str | None = None


class ReferenceUpdateRequest(BaseModel):
    title: str = Field(min_length=1)
    citation: str | None = None
    notes: str | None = None


class StandardProfileResponse(BaseModel):
    reference_id: str
    code: str | None
    issuing_body: str | None
    edition: str | None
    year: int | None
    lifecycle_state: str | None
    contractual_role: str | None
    applicability_text: str | None
    clauses_json: str | None
    eda_interpretation: str | None
    evidence_required: str | None
    verification_state: str | None
    internal_location: str | None


class StandardProfileUpsertRequest(BaseModel):
    code: str | None = None
    issuing_body: str | None = None
    edition: str | None = None
    year: int | None = None
    lifecycle_state: str | None = None
    contractual_role: ContractualRole | None = None
    applicability_text: str | None = None
    clauses_json: str | None = None
    eda_interpretation: str | None = None
    evidence_required: str | None = None
    verification_state: str | None = None
    internal_location: str | None = None


class ReferenceResponse(BaseModel):
    id: str
    scope_type: ScopeType
    scope_id: str
    title: str
    citation: str | None
    notes: str | None
    standard_profile: StandardProfileResponse | None = None