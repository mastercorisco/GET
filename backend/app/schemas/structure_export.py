from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


PointDetailLevel = Literal["none", "summary", "full"]
StructureExportFormat = Literal["markdown", "pdf", "xmind", "docx", "xlsx"]


class StructureExportRequest(BaseModel):
    format: StructureExportFormat
    root_node_id: str | None = None
    include_block_model: bool = False
    point_detail: PointDetailLevel = "none"
    include_point_premises: bool = False


class StructureExportOptionsSnapshot(BaseModel):
    include_block_model: bool
    point_detail: PointDetailLevel
    include_point_premises: bool
    format: StructureExportFormat


class BlockModelSnapshot(BaseModel):
    objective: str
    scope: str
    target_output: dict[str, Any]
    block_status: str


class PointSummarySnapshot(BaseModel):
    id: str
    order: int
    title: str
    status: str
    llm_freedom: str
    premise_count: int
    must_include_count: int
    open_questions_count: int
    acceptance_criteria_count: int


class PointFullSnapshot(BaseModel):
    id: str
    order: int
    title: str
    core_idea: str
    intended_outcome: str
    llm_freedom: str
    status: str
    template_id: str | None
    needs_review: bool
    lists: dict[str, Any]
    premises: list[dict[str, Any]] = Field(default_factory=list)


class StructureTreeNodeSnapshot(BaseModel):
    id: str
    node_type: str
    display_code: str
    title: str
    depth: int
    sort_key: int
    block_status: str | None = None
    block_model: BlockModelSnapshot | None = None
    points: list[PointSummarySnapshot] | list[PointFullSnapshot] | None = None
    children: list[StructureTreeNodeSnapshot] = Field(default_factory=list)


class DocumentStructureSnapshotV1(BaseModel):
    snapshot_schema: Literal["document-structure-export-v1"] = Field(
        default="document-structure-export-v1",
        serialization_alias="schema",
    )
    project_id: str
    project_name: str
    root_node_id: str | None
    root_display_code: str
    root_title: str
    exported_at: str
    exported_by: str
    options: StructureExportOptionsSnapshot
    tree: StructureTreeNodeSnapshot


class StructureExportResponseMeta(BaseModel):
    file_name: str
    relative_path: str
    format: StructureExportFormat
    byte_size: int
    run_id: str