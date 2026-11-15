from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Library(Base):
    __tablename__ = "library"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class LibraryVersion(Base):
    __tablename__ = "library_version"
    __table_args__ = (UniqueConstraint("library_id", "version", name="uq_library_version"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    library_id: Mapped[str] = mapped_column(ForeignKey("library.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class KnowledgeItem(Base):
    __tablename__ = "knowledge_item"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scope_type: Mapped[str] = mapped_column(String(32), nullable=False)
    scope_id: Mapped[str] = mapped_column(String(36), nullable=False)
    human_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class KnowledgeItemAlias(Base):
    __tablename__ = "knowledge_item_alias"
    __table_args__ = (UniqueConstraint("item_id", "alias", name="uq_knowledge_item_alias"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id: Mapped[str] = mapped_column(ForeignKey("knowledge_item.id"), nullable=False)
    alias: Mapped[str] = mapped_column(Text, nullable=False)


class KnowledgeDraft(Base):
    __tablename__ = "knowledge_draft"

    item_id: Mapped[str] = mapped_column(ForeignKey("knowledge_item.id"), primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content_md: Mapped[str] = mapped_column(Text, nullable=False)
    origin_context: Mapped[str] = mapped_column(Text, nullable=False)
    knowledge_type: Mapped[str] = mapped_column(String(64), nullable=False)
    maturity: Mapped[str] = mapped_column(String(32), nullable=False)
    approval: Mapped[str] = mapped_column(String(32), nullable=False)
    lifecycle: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class KnowledgeRevision(Base):
    __tablename__ = "knowledge_revision"
    __table_args__ = (UniqueConstraint("item_id", "revision_num", name="uq_knowledge_revision_num"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id: Mapped[str] = mapped_column(ForeignKey("knowledge_item.id"), nullable=False)
    revision_num: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content_md: Mapped[str] = mapped_column(Text, nullable=False)
    origin_context: Mapped[str] = mapped_column(Text, nullable=False)
    knowledge_type: Mapped[str] = mapped_column(String(64), nullable=False)
    maturity: Mapped[str] = mapped_column(String(32), nullable=False)
    approval: Mapped[str] = mapped_column(String(32), nullable=False)
    lifecycle: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class RelationType(Base):
    __tablename__ = "relation_type"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)


class KnowledgeRelation(Base):
    __tablename__ = "knowledge_relation"
    __table_args__ = (
        CheckConstraint("source_item_id != target_item_id", name="ck_knowledge_relation_no_self"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    relation_type_id: Mapped[str] = mapped_column(ForeignKey("relation_type.id"), nullable=False)
    source_item_id: Mapped[str] = mapped_column(ForeignKey("knowledge_item.id"), nullable=False)
    target_item_id: Mapped[str] = mapped_column(ForeignKey("knowledge_item.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
