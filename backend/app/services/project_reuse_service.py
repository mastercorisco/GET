from __future__ import annotations

from app.config import AppSettings
from app.schemas.project_reuse import ProjectReuseReportResponse
from app.services.f3_reuse_reports import build_f3_reuse_report
from app.services.workspace_service import workspace_session


def get_project_reuse_report(settings: AppSettings, project_id: str) -> ProjectReuseReportResponse:
    with workspace_session(settings) as (session, _paths):
        payload = build_f3_reuse_report(session, project_id)
    return ProjectReuseReportResponse.model_validate(payload)