from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from app.config import AppSettings
from app.models.project import Project
from app.models.technical import TechnicalClass, TechnicalInstance
from app.schemas.technical import (
    TechnicalClassCreateRequest,
    TechnicalClassResponse,
    TechnicalInstanceCreateRequest,
    TechnicalInstanceResponse,
)
from app.services.workspace_service import workspace_session

_DEFAULT_CLASSES = (
    ("system", "scada", "Sistema SCADA"),
    ("equipment", "mcc", "Quadro elétrico (MCC)"),
    ("function", "cmd", "Função de comando"),
)


class TechnicalError(Exception):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_default_classes(session) -> None:
    existing = {row.code for row in session.scalars(select(TechnicalClass))}
    for kind, code, label in _DEFAULT_CLASSES:
        if code not in existing:
            session.add(TechnicalClass(kind=kind, code=code, label=label))
    session.flush()


def _instance_depth(session, instance_id: str) -> int:
    node = session.get(TechnicalInstance, instance_id)
    if node is None or node.parent_id is None:
        return 0
    return _instance_depth(session, node.parent_id) + 1


def list_classes(app_settings: AppSettings) -> list[TechnicalClassResponse]:
    with workspace_session(app_settings) as (session, _paths):
        _ensure_default_classes(session)
        rows = list(session.scalars(select(TechnicalClass).order_by(TechnicalClass.kind, TechnicalClass.code)))
        return [
            TechnicalClassResponse(id=row.id, kind=row.kind, code=row.code, label=row.label)
            for row in rows
        ]


def create_class(app_settings: AppSettings, body: TechnicalClassCreateRequest) -> TechnicalClassResponse:
    with workspace_session(app_settings) as (session, _paths):
        _ensure_default_classes(session)
        existing = session.scalar(
            select(TechnicalClass).where(
                TechnicalClass.kind == body.kind,
                TechnicalClass.code == body.code.strip(),
            )
        )
        if existing is not None:
            raise TechnicalError("Classe técnica já existe.")
        row = TechnicalClass(kind=body.kind, code=body.code.strip(), label=body.label.strip())
        session.add(row)
        session.flush()
        return TechnicalClassResponse(id=row.id, kind=row.kind, code=row.code, label=row.label)


def _require_project(session, project_id: str) -> Project:
    project = session.get(Project, project_id)
    if project is None:
        raise TechnicalError("Projeto não encontrado.")
    return project


def list_instances(app_settings: AppSettings, project_id: str) -> list[TechnicalInstanceResponse]:
    with workspace_session(app_settings) as (session, _paths):
        _require_project(session, project_id)
        instances = list(
            session.scalars(
                select(TechnicalInstance)
                .where(TechnicalInstance.project_id == project_id)
                .order_by(TechnicalInstance.created_at)
            )
        )
        return [
            TechnicalInstanceResponse(
                id=row.id,
                project_id=row.project_id,
                parent_id=row.parent_id,
                class_id=row.class_id,
                kind=row.kind,
                name=row.name,
                export_code=row.export_code,
                location_note=row.location_note,
                reference_note=row.reference_note,
                depth=_instance_depth(session, row.id),
            )
            for row in instances
        ]


def create_instance(
    app_settings: AppSettings,
    project_id: str,
    body: TechnicalInstanceCreateRequest,
) -> TechnicalInstanceResponse:
    with workspace_session(app_settings) as (session, _paths):
        _require_project(session, project_id)
        parent_id = body.parent_id
        if parent_id:
            parent = session.get(TechnicalInstance, parent_id)
            if parent is None or parent.project_id != project_id:
                raise TechnicalError("Instância pai inválida.")
        if body.class_id:
            tech_class = session.get(TechnicalClass, body.class_id)
            if tech_class is None:
                raise TechnicalError("Classe técnica inválida.")
        row = TechnicalInstance(
            id=str(uuid.uuid4()),
            project_id=project_id,
            parent_id=parent_id,
            class_id=body.class_id,
            kind=body.kind,
            name=body.name.strip(),
            export_code=body.export_code,
            location_note=body.location_note,
            reference_note=body.reference_note,
            created_at=_utcnow(),
        )
        session.add(row)
        session.flush()
        depth = _instance_depth(session, row.id)
        return TechnicalInstanceResponse(
            id=row.id,
            project_id=row.project_id,
            parent_id=row.parent_id,
            class_id=row.class_id,
            kind=row.kind,
            name=row.name,
            export_code=row.export_code,
            location_note=row.location_note,
            reference_note=row.reference_note,
            depth=depth,
        )