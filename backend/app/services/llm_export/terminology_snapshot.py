from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge import Library
from app.models.project import Project
from app.models.terminology import ProjectTerminologyOverride, TerminologyConcept


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


def _concept_entry(row: TerminologyConcept) -> dict[str, Any]:
    return {
        "id": row.id,
        "scope_type": row.scope_type,
        "preferred_term": row.preferred_term,
        "definition": row.definition,
        "language": row.language,
        "acronym": row.acronym,
        "synonyms": _list_from_json(row.synonyms_json),
        "avoid_terms": _list_from_json(row.avoid_terms_json),
        "technical_translation": row.technical_translation,
        "domain": row.domain,
        "notes": row.notes,
    }


def build_terminology_snapshot(session: Session, project_id: str) -> dict[str, Any]:
    project = session.get(Project, project_id)
    if project is None:
        raise ValueError("Projeto não encontrado.")

    library = session.scalar(select(Library).limit(1))
    library_terms: list[dict[str, Any]] = []
    if library is not None:
        rows = session.scalars(
            select(TerminologyConcept)
            .where(
                TerminologyConcept.scope_type == "library",
                TerminologyConcept.scope_id == library.id,
            )
            .order_by(TerminologyConcept.preferred_term)
        )
        library_terms = [_concept_entry(r) for r in rows]

    project_terms = [
        _concept_entry(r)
        for r in session.scalars(
            select(TerminologyConcept)
            .where(
                TerminologyConcept.scope_type == "project",
                TerminologyConcept.scope_id == project_id,
            )
            .order_by(TerminologyConcept.preferred_term)
        )
    ]

    overrides: list[dict[str, Any]] = []
    for override, concept in session.execute(
        select(ProjectTerminologyOverride, TerminologyConcept)
        .join(TerminologyConcept, TerminologyConcept.id == ProjectTerminologyOverride.concept_id)
        .where(ProjectTerminologyOverride.project_id == project_id)
        .order_by(TerminologyConcept.preferred_term)
    ):
        overrides.append(
            {
                "override_id": override.id,
                "concept_id": concept.id,
                "preferred_term": concept.preferred_term,
                "legacy_term": override.legacy_term,
                "avoid_in_project": override.avoid_in_project,
                "usage_note": override.usage_note,
            }
        )

    return {
        "project": {"id": project_id, "name": project.name},
        "library_terms": library_terms,
        "project_terms": project_terms,
        "project_overrides": overrides,
    }