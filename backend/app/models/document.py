from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AssociationRole(Base):
    __tablename__ = "association_role"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)


class DocumentNode(Base):
    __tablename__ = "document_node"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("project.id"), nullable=False)
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("document_node.id"), nullable=True)
    node_type: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_key: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class DocumentAssociation(Base):
    __tablename__ = "document_association"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_node_id: Mapped[str] = mapped_column(ForeignKey("document_node.id"), nullable=False)
    knowledge_item_id: Mapped[str] = mapped_column(ForeignKey("knowledge_item.id"), nullable=False)
    role_id: Mapped[str] = mapped_column(ForeignKey("association_role.id"), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    usage_instruction: Mapped[str | None] = mapped_column(Text, nullable=True)
    pinned_revision_num: Mapped[int | None] = mapped_column(Integer, nullable=True)