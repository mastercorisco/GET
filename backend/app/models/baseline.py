from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Baseline(Base):
    __tablename__ = "baseline"
    __table_args__ = (UniqueConstraint("project_id", "revision", name="uq_baseline_project_revision"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("project.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    library_version_id: Mapped[str] = mapped_column(ForeignKey("library_version.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class BaselineEntry(Base):
    __tablename__ = "baseline_entry"
    __table_args__ = (UniqueConstraint("baseline_id", "entity_id", name="uq_baseline_entry_entity"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    baseline_id: Mapped[str] = mapped_column(ForeignKey("baseline.id"), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    revision_num: Mapped[int] = mapped_column(Integer, nullable=False)


class BaselineDocumentCode(Base):
    __tablename__ = "baseline_document_code"
    __table_args__ = (
        UniqueConstraint("baseline_id", "document_node_id", name="uq_baseline_document_code"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    baseline_id: Mapped[str] = mapped_column(ForeignKey("baseline.id"), nullable=False)
    document_node_id: Mapped[str] = mapped_column(ForeignKey("document_node.id"), nullable=False)
    display_code: Mapped[str] = mapped_column(String(128), nullable=False)


class ExportRecord(Base):
    __tablename__ = "export_record"
    __table_args__ = (UniqueConstraint("project_id", "export_id", name="uq_export_record_project_export_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("project.id"), nullable=False)
    baseline_id: Mapped[str] = mapped_column(ForeignKey("baseline.id"), nullable=False)
    export_id: Mapped[str] = mapped_column(String(64), nullable=False)
    profile: Mapped[str] = mapped_column(String(32), nullable=False)
    schema_name: Mapped[str] = mapped_column(String(64), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    package_type: Mapped[str] = mapped_column(String(32), nullable=False)
    parent_export_id: Mapped[str | None] = mapped_column(ForeignKey("export_record.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)