from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ProjectTemplate(Base):
    __tablename__ = "project_template"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ProjectTemplateVersion(Base):
    __tablename__ = "project_template_version"
    __table_args__ = (UniqueConstraint("template_id", "version", name="uq_project_template_version"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id: Mapped[str] = mapped_column(ForeignKey("project_template.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Project(Base):
    __tablename__ = "project"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    template_version_id: Mapped[str] = mapped_column(
        ForeignKey("project_template_version.id"),
        nullable=False,
    )
    intervention_type: Mapped[str] = mapped_column(String(64), nullable=False)
    llm_context_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ProjectLibraryPin(Base):
    __tablename__ = "project_library_pin"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("project.id"), nullable=False, unique=True)
    library_version_id: Mapped[str] = mapped_column(ForeignKey("library_version.id"), nullable=False)
    pinned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)