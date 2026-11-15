from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TechnicalProfileDraft(Base):
    __tablename__ = "technical_profile_draft"

    item_id: Mapped[str] = mapped_column(ForeignKey("knowledge_item.id"), primary_key=True)
    profile_type: Mapped[str] = mapped_column(String(32), nullable=False)
    data_json: Mapped[str] = mapped_column(Text, nullable=False)


class TechnicalProfilePayload(Base):
    __tablename__ = "technical_profile_payload"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    revision_id: Mapped[str] = mapped_column(ForeignKey("knowledge_revision.id"), nullable=False, unique=True)
    profile_type: Mapped[str] = mapped_column(String(32), nullable=False)
    data_json: Mapped[str] = mapped_column(Text, nullable=False)