from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Reference(Base):
    __tablename__ = "reference"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scope_type: Mapped[str] = mapped_column(String(32), nullable=False)
    scope_id: Mapped[str] = mapped_column(String(36), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    citation: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class StandardProfile(Base):
    __tablename__ = "standard_profile"

    reference_id: Mapped[str] = mapped_column(ForeignKey("reference.id"), primary_key=True)
    code: Mapped[str | None] = mapped_column(String(128), nullable=True)
    issuing_body: Mapped[str | None] = mapped_column(String(255), nullable=True)
    edition: Mapped[str | None] = mapped_column(String(64), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lifecycle_state: Mapped[str | None] = mapped_column(String(64), nullable=True)
    contractual_role: Mapped[str | None] = mapped_column(String(64), nullable=True)
    applicability_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    clauses_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    eda_interpretation: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_required: Mapped[str | None] = mapped_column(Text, nullable=True)
    verification_state: Mapped[str | None] = mapped_column(String(64), nullable=True)
    internal_location: Mapped[str | None] = mapped_column(String(255), nullable=True)