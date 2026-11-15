from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from app.config import AppSettings
from app.models.knowledge import Library
from app.models.project import Project
from app.models.reference import Reference, StandardProfile
from app.schemas.reference import (
    ReferenceCreateRequest,
    ReferenceResponse,
    ReferenceUpdateRequest,
    StandardProfileResponse,
    StandardProfileUpsertRequest,
)
from app.services.knowledge_service import _ensure_library
from app.services.workspace_service import workspace_session

_CONTRACTUAL_ROLES = frozenset(
    {
        "informative_reference",
        "design_basis",
        "contractual_requirement",
        "compliance_target",
        "guidance_only",
    }
)


class ReferenceError(Exception):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _resolve_scope(session, scope_type: str, scope_id: str | None) -> str:
    if scope_type == "library":
        library = session.scalar(select(Library).limit(1))
        if library is None:
            raise ReferenceError("Biblioteca em falta.")
        return library.id
    if not scope_id:
        raise ReferenceError("scope_id é obrigatório para referências de projeto.")
    project = session.get(Project, scope_id)
    if project is None:
        raise ReferenceError("Projeto não encontrado.")
    return project.id


def _standard_response(row: StandardProfile | None) -> StandardProfileResponse | None:
    if row is None:
        return None
    return StandardProfileResponse(
        reference_id=row.reference_id,
        code=row.code,
        issuing_body=row.issuing_body,
        edition=row.edition,
        year=row.year,
        lifecycle_state=row.lifecycle_state,
        contractual_role=row.contractual_role,
        applicability_text=row.applicability_text,
        clauses_json=row.clauses_json,
        eda_interpretation=row.eda_interpretation,
        evidence_required=row.evidence_required,
        verification_state=row.verification_state,
        internal_location=row.internal_location,
    )


def _to_response(reference: Reference, standard: StandardProfile | None) -> ReferenceResponse:
    return ReferenceResponse(
        id=reference.id,
        scope_type=reference.scope_type,  # type: ignore[arg-type]
        scope_id=reference.scope_id,
        title=reference.title,
        citation=reference.citation,
        notes=reference.notes,
        standard_profile=_standard_response(standard),
    )


def list_references(
    app_settings: AppSettings, scope_type: str, scope_id: str | None
) -> list[ReferenceResponse]:
    if scope_type not in {"library", "project"}:
        raise ReferenceError("Âmbito inválido.")
    with workspace_session(app_settings) as (session, _paths):
        _ensure_library(session)
        resolved = _resolve_scope(session, scope_type, scope_id)
        rows = list(
            session.scalars(
                select(Reference)
                .where(Reference.scope_type == scope_type, Reference.scope_id == resolved)
                .order_by(Reference.title)
            )
        )
        result: list[ReferenceResponse] = []
        for ref in rows:
            std = session.get(StandardProfile, ref.id)
            result.append(_to_response(ref, std))
        return result


def create_reference(app_settings: AppSettings, body: ReferenceCreateRequest) -> ReferenceResponse:
    with workspace_session(app_settings) as (session, _paths):
        _ensure_library(session)
        scope_id = _resolve_scope(session, body.scope_type, body.scope_id)
        ref = Reference(
            id=str(uuid.uuid4()),
            scope_type=body.scope_type,
            scope_id=scope_id,
            title=body.title.strip(),
            citation=body.citation,
            notes=body.notes,
            created_at=_utcnow(),
        )
        session.add(ref)
        session.flush()
        return _to_response(ref, None)


def get_reference(app_settings: AppSettings, reference_id: str) -> ReferenceResponse:
    with workspace_session(app_settings) as (session, _paths):
        ref = session.get(Reference, reference_id)
        if ref is None:
            raise ReferenceError("Referência não encontrada.")
        std = session.get(StandardProfile, ref.id)
        return _to_response(ref, std)


def update_reference(
    app_settings: AppSettings, reference_id: str, body: ReferenceUpdateRequest
) -> ReferenceResponse:
    with workspace_session(app_settings) as (session, _paths):
        ref = session.get(Reference, reference_id)
        if ref is None:
            raise ReferenceError("Referência não encontrada.")
        ref.title = body.title.strip()
        ref.citation = body.citation
        ref.notes = body.notes
        session.flush()
        std = session.get(StandardProfile, ref.id)
        return _to_response(ref, std)


def upsert_standard_profile(
    app_settings: AppSettings, reference_id: str, body: StandardProfileUpsertRequest
) -> ReferenceResponse:
    if body.contractual_role is not None and body.contractual_role not in _CONTRACTUAL_ROLES:
        raise ReferenceError("Papel contratual inválido.")
    with workspace_session(app_settings) as (session, _paths):
        ref = session.get(Reference, reference_id)
        if ref is None:
            raise ReferenceError("Referência não encontrada.")
        std = session.get(StandardProfile, reference_id)
        if std is None:
            std = StandardProfile(reference_id=reference_id)
            session.add(std)
        std.code = body.code
        std.issuing_body = body.issuing_body
        std.edition = body.edition
        std.year = body.year
        std.lifecycle_state = body.lifecycle_state
        std.contractual_role = body.contractual_role
        std.applicability_text = body.applicability_text
        std.clauses_json = body.clauses_json
        std.eda_interpretation = body.eda_interpretation
        std.evidence_required = body.evidence_required
        std.verification_state = body.verification_state
        std.internal_location = body.internal_location
        session.flush()
        return _to_response(ref, std)