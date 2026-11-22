from __future__ import annotations

from sqlalchemy import func, select

from app.config import AppSettings
from app.domain.block.models import DevelopmentPoint
from app.models.baseline import ExportRecord
from app.models.document import DocumentNode
from app.models.imports import ImportRecord, MergeSession
from app.models.project import Project
from app.schemas.project_summary import LatestExportSnippet, ProjectSummaryResponse
from app.services.project_service import ProjectError
from app.services.workspace_service import workspace_session


def get_project_summary(settings: AppSettings, project_id: str) -> ProjectSummaryResponse:
    with workspace_session(settings) as (session, _paths):
        if session.get(Project, project_id) is None:
            raise ProjectError("Projeto não encontrado.")

        status_rows = session.execute(
            select(DevelopmentPoint.status, func.count())
            .select_from(DevelopmentPoint)
            .join(DocumentNode, DocumentNode.id == DevelopmentPoint.block_id)
            .where(DocumentNode.project_id == project_id)
            .group_by(DevelopmentPoint.status)
        ).all()
        status_counts = {str(status): int(count) for status, count in status_rows}

        needs_review = session.scalar(
            select(func.count())
            .select_from(DevelopmentPoint)
            .join(DocumentNode, DocumentNode.id == DevelopmentPoint.block_id)
            .where(
                DocumentNode.project_id == project_id,
                DevelopmentPoint.needs_review.is_(True),
            )
        )
        staged = session.scalar(
            select(func.count())
            .select_from(ImportRecord)
            .where(ImportRecord.project_id == project_id, ImportRecord.status == "staged")
        )
        open_merges = session.scalar(
            select(func.count())
            .select_from(MergeSession)
            .where(MergeSession.project_id == project_id, MergeSession.status == "open")
        )

        export_rows = session.scalars(
            select(ExportRecord)
            .where(ExportRecord.project_id == project_id)
            .order_by(ExportRecord.created_at.desc())
            .limit(5)
        ).all()
        latest_exports = [
            LatestExportSnippet(
                export_id=row.export_id,
                package_type=row.package_type,
                created_at=row.created_at,
            )
            for row in export_rows
        ]

        return ProjectSummaryResponse(
            project_id=project_id,
            point_status_counts=status_counts,
            points_needs_review=int(needs_review or 0),
            imports_staged=int(staged or 0),
            merge_sessions_open=int(open_merges or 0),
            latest_package_exports=latest_exports,
        )