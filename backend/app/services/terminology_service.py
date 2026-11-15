from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from app.config import AppSettings
from app.models.knowledge import Library
from app.models.project import Project
from app.models.terminology import ProjectTerminologyOverride, TerminologyConcept
from app.schemas.terminology import (
    TerminologyCreateRequest,
    TerminologyOverrideCreateRequest,
    TerminologyOverrideResponse,
    TerminologyResponse,
    TerminologyUpdateRequest,
)
from app.services.knowledge_service import _ensure_library
from app.services.workspace_service import workspace_session


class TerminologyError(Exception):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _resolve_scope(session, scope_type: str, scope_id: str | None) -> str:
    if scope_type == "library":
        library = session.scalar(select(Library).limit(1))
        if library is None:
            raise TerminologyError("Biblioteca em falta.")
        return library.id
    if not scope_id:
        raise TerminologyError("scope_id é obrigatório para terminologia de projeto.")
    project = session.get(Project, scope_id)
    if project is None:
        raise TerminologyError("Projeto não encontrado.")
    return project.id


def _list_from_json(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    return [str(x) for x in parsed]


def _dump_list(values: list[str]) -> str | None:
    cleaned = [v.strip() for v in values if v and v.strip()]
    return json.dumps(cleaned, ensure_ascii=False) if cleaned else None


def _to_response(row: TerminologyConcept) -> TerminologyResponse:
    return TerminologyResponse(
        id=row.id,
        scope_type=row.scope_type,  # type: ignore[arg-type]
        scope_id=row.scope_id,
        preferred_term=row.preferred_term,
        definition=row.definition,
        language=row.language,
        acronym=row.acronym,
        synonyms=_list_from_json(row.synonyms_json),
        avoid_terms=_list_from_json(row.avoid_terms_json),
        technical_translation=row.technical_translation,
        domain=row.domain,
        notes=row.notes,
    )


def list_terminology(
    app_settings: AppSettings, scope_type: str, scope_id: str | None
) -> list[TerminologyResponse]:
    if scope_type not in {"library", "project"}:
        raise TerminologyError("Âmbito inválido.")
    with workspace_session(app_settings) as (session, _paths):
        _ensure_library(session)
        resolved = _resolve_scope(session, scope_type, scope_id)
        rows = list(
            session.scalars(
                select(TerminologyConcept)
                .where(
                    TerminologyConcept.scope_type == scope_type,
                    TerminologyConcept.scope_id == resolved,
                )
                .order_by(TerminologyConcept.preferred_term)
            )
        )
        return [_to_response(row) for row in rows]


def create_terminology(app_settings: AppSettings, body: TerminologyCreateRequest) -> TerminologyResponse:
    with workspace_session(app_settings) as (session, _paths):
        _ensure_library(session)
        scope_id = _resolve_scope(session, body.scope_type, body.scope_id)
        row = TerminologyConcept(
            id=str(uuid.uuid4()),
            scope_type=body.scope_type,
            scope_id=scope_id,
            preferred_term=body.preferred_term.strip(),
            definition=body.definition.strip(),
            language=body.language.strip(),
            acronym=body.acronym,
            synonyms_json=_dump_list(body.synonyms),
            avoid_terms_json=_dump_list(body.avoid_terms),
            technical_translation=body.technical_translation,
            domain=body.domain,
            notes=body.notes,
            created_at=_utcnow(),
        )
        session.add(row)
        session.flush()
        return _to_response(row)


def get_terminology(app_settings: AppSettings, concept_id: str) -> TerminologyResponse:
    with workspace_session(app_settings) as (session, _paths):
        row = session.get(TerminologyConcept, concept_id)
        if row is None:
            raise TerminologyError("Conceito não encontrado.")
        return _to_response(row)


def update_terminology(
    app_settings: AppSettings, concept_id: str, body: TerminologyUpdateRequest
) -> TerminologyResponse:
    with workspace_session(app_settings) as (session, _paths):
        row = session.get(TerminologyConcept, concept_id)
        if row is None:
            raise TerminologyError("Conceito não encontrado.")
        row.preferred_term = body.preferred_term.strip()
        row.definition = body.definition.strip()
        row.language = body.language.strip()
        row.acronym = body.acronym
        row.synonyms_json = _dump_list(body.synonyms)
        row.avoid_terms_json = _dump_list(body.avoid_terms)
        row.technical_translation = body.technical_translation
        row.domain = body.domain
        row.notes = body.notes
        session.flush()
        return _to_response(row)


def list_terminology_overrides(
    app_settings: AppSettings, project_id: str
) -> list[TerminologyOverrideResponse]:
    with workspace_session(app_settings) as (session, _paths):
        project = session.get(Project, project_id)
        if project is None:
            raise TerminologyError("Projeto não encontrado.")
        rows = session.execute(
            select(ProjectTerminologyOverride, TerminologyConcept)
            .join(TerminologyConcept, TerminologyConcept.id == ProjectTerminologyOverride.concept_id)
            .where(ProjectTerminologyOverride.project_id == project_id)
            .order_by(TerminologyConcept.preferred_term)
        )
        return [
            TerminologyOverrideResponse(
                id=override.id,
                project_id=override.project_id,
                concept_id=override.concept_id,
                preferred_term=concept.preferred_term,
                legacy_term=override.legacy_term,
                avoid_in_project=override.avoid_in_project,
                usage_note=override.usage_note,
            )
            for override, concept in rows
        ]


def create_terminology_override(
    app_settings: AppSettings, project_id: str, body: TerminologyOverrideCreateRequest
) -> TerminologyOverrideResponse:
    with workspace_session(app_settings) as (session, _paths):
        project = session.get(Project, project_id)
        if project is None:
            raise TerminologyError("Projeto não encontrado.")
        concept = session.get(TerminologyConcept, body.concept_id)
        if concept is None:
            raise TerminologyError("Conceito não encontrado.")
        existing = session.scalar(
            select(ProjectTerminologyOverride).where(
                ProjectTerminologyOverride.project_id == project_id,
                ProjectTerminologyOverride.concept_id == body.concept_id,
            )
        )
        if existing is not None:
            raise TerminologyError("Já existe override para este conceito no projecto.")
        override = ProjectTerminologyOverride(
            id=str(uuid.uuid4()),
            project_id=project_id,
            concept_id=body.concept_id,
            legacy_term=body.legacy_term,
            avoid_in_project=body.avoid_in_project,
            usage_note=body.usage_note,
        )
        session.add(override)
        session.flush()
        return TerminologyOverrideResponse(
            id=override.id,
            project_id=override.project_id,
            concept_id=override.concept_id,
            preferred_term=concept.preferred_term,
            legacy_term=override.legacy_term,
            avoid_in_project=override.avoid_in_project,
            usage_note=override.usage_note,
        )