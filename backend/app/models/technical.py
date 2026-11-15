from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TechnicalClass(Base):
    __tablename__ = "technical_class"
    __table_args__ = (UniqueConstraint("kind", "code", name="uq_technical_class_kind_code"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)


class TechnicalInstance(Base):
    __tablename__ = "technical_instance"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("project.id"), nullable=False)
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("technical_instance.id"), nullable=True)
    class_id: Mapped[str | None] = mapped_column(ForeignKey("technical_class.id"), nullable=True)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    export_code: Mapped[str | None] = mapped_column(String(128), nullable=True)
    location_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reference_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)