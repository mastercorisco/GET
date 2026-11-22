from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class LatestExportSnippet(BaseModel):
    export_id: str
    package_type: str
    created_at: datetime


class ProjectSummaryResponse(BaseModel):
    project_id: str
    point_status_counts: dict[str, int] = Field(default_factory=dict)
    points_needs_review: int = 0
    imports_staged: int = 0
    merge_sessions_open: int = 0
    latest_package_exports: list[LatestExportSnippet] = Field(default_factory=list)
    latest_llm_export_id: str | None = None
    latest_llm_zip_path: str | None = None