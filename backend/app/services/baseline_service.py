from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select

from app.config import AppSettings
from app.models.baseline import Baseline, BaselineDocumentCode, BaselineEntry
from app.models.document import DocumentNode
from app.models.knowledge import KnowledgeItem, KnowledgeRevision
from app.models.project import Project, ProjectLibraryPin
from app.schemas.baseline import BaselineResponse
from app.services.document_service import compute_display_codes
from app.services.workspace_service import workspace_session


class BaselineError(Exception):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _latest_revision(session, item_id: str) -> int | None:
    rev = session.scalar(
        select(KnowledgeRevision.revision_num)
        .where(KnowledgeRevision.item_id == item_id)
        .order_by(KnowledgeRevision.revision_num.desc())
        .limit(1)
    )
    return rev


def _to_response(row: Baseline) -> BaselineResponse:
    return BaselineResponse(
        id=row.id,
        project_id=row.project_id,
        code=row.code,
        revision=row.revision,
        library_version_id=row.library_version_id,
        created_at=row.created_at.isoformat(),
    )


def get_latest_baseline(app_settings: AppSettings, project_id: str) -> BaselineResponse | None:
    with workspace_session(app_settings) as (session, _paths):
        row = session.scalar(
            select(Baseline)
            .where(Baseline.project_id == project_id)
            .order_by(Baseline.revision.desc())
            .limit(1)
        )
        if row is None:
            return None
        return _to_response(row)


def publish_baseline(app_settings: AppSettings, project_id: str) -> BaselineResponse:
    from app.services.workspace_exclusivity import workspace_exclusive

    with workspace_exclusive("publish_baseline"):
        with workspace_session(app_settings, begin_immediate=True) as (session, _paths):
            project = session.get(Project, project_id)
            if project is None:
                raise BaselineError("Projecto não encontrado.")
            pin = session.scalar(select(ProjectLibraryPin).where(ProjectLibraryPin.project_id == project_id))
            if pin is None:
                raise BaselineError("Projecto sem pin da biblioteca.")

            max_rev = session.scalar(
                select(func.max(Baseline.revision)).where(Baseline.project_id == project_id)
            )
            next_rev = (max_rev or 0) + 1
            baseline = Baseline(
                id=str(uuid.uuid4()),
                project_id=project_id,
                code=f"BL-{next_rev:04d}",
                revision=next_rev,
                library_version_id=pin.library_version_id,
                created_at=_utcnow(),
            )
            session.add(baseline)
            session.flush()

            items = list(
                session.scalars(
                    select(KnowledgeItem).where(
                        KnowledgeItem.scope_type == "project",
                        KnowledgeItem.scope_id == project_id,
                    )
                )
            )
            for item in items:
                revision_num = _latest_revision(session, item.id)
                if revision_num is None:
                    continue
                session.add(
                    BaselineEntry(
                        id=str(uuid.uuid4()),
                        baseline_id=baseline.id,
                        entity_type="knowledge_item",
                        entity_id=item.id,
                        revision_num=revision_num,
                    )
                )

            nodes = list(session.scalars(select(DocumentNode).where(DocumentNode.project_id == project_id)))
            codes = compute_display_codes(nodes)
            for node_id, code in codes.items():
                session.add(
                    BaselineDocumentCode(
                        id=str(uuid.uuid4()),
                        baseline_id=baseline.id,
                        document_node_id=node_id,
                        display_code=code,
                    )
                )
            session.flush()
            return _to_response(baseline)