from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TerminologyConcept(Base):
    __tablename__ = "terminology_concept"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scope_type: Mapped[str] = mapped_column(String(32), nullable=False)
    scope_id: Mapped[str] = mapped_column(String(36), nullable=False)
    preferred_term: Mapped[str] = mapped_column(String(255), nullable=False)
    definition: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(16), default="pt")
    acronym: Mapped[str | None] = mapped_column(String(64), nullable=True)
    synonyms_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    avoid_terms_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    technical_translation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    domain: Mapped[str | None] = mapped_column(String(128), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ProjectTerminologyOverride(Base):
    __tablename__ = "project_terminology_override"
    __table_args__ = (UniqueConstraint("project_id", "concept_id", name="uq_project_terminology_override"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("project.id"), nullable=False)
    concept_id: Mapped[str] = mapped_column(ForeignKey("terminology_concept.id"), nullable=False)
    legacy_term: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avoid_in_project: Mapped[bool] = mapped_column(Boolean, default=False)
    usage_note: Mapped[str | None] = mapped_column(Text, nullable=True)