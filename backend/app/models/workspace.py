from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class WorkspaceSettings(Base):
    __tablename__ = "workspace_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    root_path: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    local_user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    schema_versions_json: Mapped[str] = mapped_column(Text, default='{"app":"0.1.0"}')
    retention_critical: Mapped[int] = mapped_column(Integer, default=10)
    retention_daily: Mapped[int] = mapped_column(Integer, default=14)
    retention_weekly: Mapped[int] = mapped_column(Integer, default=8)
    help_level: Mapped[str] = mapped_column(String(16), nullable=False, default="normal")