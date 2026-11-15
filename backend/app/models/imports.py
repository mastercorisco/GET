from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ImportRecord(Base):
    __tablename__ = "import_record"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("project.id"), nullable=False)
    source_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    raw_path: Mapped[str] = mapped_column(Text, nullable=False)
    package_type: Mapped[str] = mapped_column(String(32), nullable=False)
    schema_name: Mapped[str] = mapped_column(String(64), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(32), nullable=False)
    linked_export_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    export_record_id: Mapped[str | None] = mapped_column(ForeignKey("export_record.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ImportStagingItem(Base):
    __tablename__ = "import_staging_item"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    import_id: Mapped[str] = mapped_column(ForeignKey("import_record.id"), nullable=False)
    entity_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_key: Mapped[str] = mapped_column(String(128), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)


class ImportQuarantineItem(Base):
    __tablename__ = "import_quarantine_item"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    import_id: Mapped[str] = mapped_column(ForeignKey("import_record.id"), nullable=False)
    path: Mapped[str] = mapped_column(String(256), nullable=False)
    error_code: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)


class MergeSession(Base):
    __tablename__ = "merge_session"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    import_id: Mapped[str] = mapped_column(ForeignKey("import_record.id"), nullable=False)
    project_id: Mapped[str] = mapped_column(ForeignKey("project.id"), nullable=False)
    base_export_id: Mapped[str] = mapped_column(String(64), nullable=False)
    baseline_id: Mapped[str] = mapped_column(ForeignKey("baseline.id"), nullable=False)
    fascicle_node_id: Mapped[str] = mapped_column(ForeignKey("document_node.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    summary_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ChangeProposal(Base):
    __tablename__ = "change_proposal"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    merge_session_id: Mapped[str] = mapped_column(ForeignKey("merge_session.id"), nullable=False)
    proposal_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    target_item_id: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    field_changes_json: Mapped[str] = mapped_column(Text, nullable=False)
    conflict: Mapped[bool] = mapped_column(Boolean, nullable=False)
    protected_touch: Mapped[bool] = mapped_column(Boolean, nullable=False)


class ChangeDecision(Base):
    __tablename__ = "change_decision"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_id: Mapped[str] = mapped_column(ForeignKey("change_proposal.id"), nullable=False, unique=True)
    decision: Mapped[str | None] = mapped_column(String(32), nullable=True)
    destination: Mapped[str | None] = mapped_column(String(32), nullable=True)
    confirmed_protected: Mapped[bool] = mapped_column(Boolean, default=False)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)