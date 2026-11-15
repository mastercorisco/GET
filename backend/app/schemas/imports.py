from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ImportStatus = Literal["staged", "merged", "consolidated", "rejected"]
DecisionKind = Literal["accepted", "rejected"]
DestinationKind = Literal["project", "library", "pending", "rejected"]


class ImportRecordResponse(BaseModel):
    id: str
    project_id: str
    source_filename: str
    raw_path: str
    package_type: str
    schema_name: str
    schema_version: str
    linked_export_id: str | None
    export_record_id: str | None
    status: str
    created_at: str
    quarantine_count: int = 0
    staging_count: int = 0


class QuarantineItemResponse(BaseModel):
    id: str
    path: str
    error_code: str
    message: str


class MergeRequest(BaseModel):
    fascicle_node_id: str = Field(min_length=1)


class ProposalResponse(BaseModel):
    id: str
    proposal_kind: str
    target_item_id: str
    title: str
    field_changes: dict
    conflict: bool
    protected_touch: bool
    decision: str | None = None
    destination: str | None = None
    confirmed_protected: bool = False


class MergeSessionResponse(BaseModel):
    id: str
    import_id: str
    project_id: str
    base_export_id: str
    baseline_id: str
    fascicle_node_id: str
    status: str
    summary: dict
    proposals: list[ProposalResponse]


class ProposalDecisionRequest(BaseModel):
    decision: DecisionKind
    destination: DestinationKind = "project"
    confirmed_protected: bool = False


class ConsolidateResponse(BaseModel):
    merge_session_id: str
    backup_id: str
    import_status: str