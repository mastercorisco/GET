from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


DEFAULT_LISTS_JSON = (
    '{"development_guidance":[],"perspectives":[],"questions_to_answer":[],'
    '"must_include":[],"limits_and_exclusions":[],"examples":[],'
    '"open_questions":[],"acceptance_criteria":[],"knowledge_item_ids":[],"reference_ids":[]}'
)


class Premise(Base):
    __tablename__ = "premise"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    owner_id: Mapped[str] = mapped_column(String(36), nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    importance: Mapped[str] = mapped_column(String(32), nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    confidence: Mapped[str] = mapped_column(String(32), nullable=False)
    reference_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class DevelopmentPoint(Base):
    __tablename__ = "development_point"
    __table_args__ = (UniqueConstraint("block_id", "sort_order", name="uq_development_point_block_order"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    block_id: Mapped[str] = mapped_column(ForeignKey("document_node.id"), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    core_idea: Mapped[str] = mapped_column(Text, nullable=False, default="")
    intended_outcome: Mapped[str] = mapped_column(Text, nullable=False, default="")
    llm_freedom: Mapped[str] = mapped_column(String(32), nullable=False, default="strict")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    template_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    needs_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    lists_json: Mapped[str] = mapped_column(Text, nullable=False, default=DEFAULT_LISTS_JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)