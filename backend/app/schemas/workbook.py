from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class WorkbookMigrateResponse(BaseModel):
    run_id: str
    status: Literal["ready", "blocked"]
    blocking_errors: int
    warnings: int
    counts: dict[str, int]
    issues: list[dict[str, Any]]
    preview: dict[str, Any] | None = None
    report_path: str | None = None


class WorkbookApplyRequest(BaseModel):
    run_id: str
    confirm: str = Field(min_length=1)
    target: Literal["new_project", "existing_project"]
    project_id: str | None = None

    @model_validator(mode="after")
    def _require_project_for_existing(self) -> WorkbookApplyRequest:
        if self.target == "existing_project" and not self.project_id:
            raise ValueError("project_id é obrigatório quando target é existing_project.")
        return self


class WorkbookApplyResponse(BaseModel):
    run_id: str
    project_id: str
    target: Literal["new_project", "existing_project"]
    applied: bool = True
    summary: dict[str, int] | None = None