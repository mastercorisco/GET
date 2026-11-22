from datetime import datetime

from pydantic import BaseModel, Field


class BackupCreateRequest(BaseModel):
    tier: str = Field(pattern="^(critical|daily|weekly)$")
    user_note: str | None = Field(default=None, max_length=500)


class BackupRecordResponse(BaseModel):
    id: str
    tier: str
    file_path: str
    sha256: str
    created_at: datetime
    preview_meta_json: dict
    user_note: str | None = None


class BackupRestorePreviewResponse(BaseModel):
    backup_id: str
    workspace_settings_rows: int
    backup_record_rows: int
    file_path: str