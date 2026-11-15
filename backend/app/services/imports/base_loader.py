from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.baseline import ExportRecord


class BaseLoadError(Exception):
    pass


def resolve_export_record(session: Session, project_id: str, export_id: str) -> ExportRecord:
    row = session.scalar(
        select(ExportRecord).where(
            ExportRecord.project_id == project_id,
            ExportRecord.export_id == export_id,
        )
    )
    if row is None:
        raise BaseLoadError(f"Export base não encontrado para {export_id}.")
    return row


def load_base_package(record: ExportRecord) -> dict:
    path = Path(record.file_path)
    if not path.is_file():
        raise BaseLoadError("Ficheiro base de exportação em falta.")
    return json.loads(path.read_text(encoding="utf-8"))