from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ScopeKind = Literal["fascicle", "block"]
ExportProfile = Literal["discussion", "redaction"]


class PackageExportRequest(BaseModel):
    scope_kind: ScopeKind
    node_id: str = Field(min_length=1)
    profile: ExportProfile | None = "discussion"


class PackageExportResponse(BaseModel):
    export_id: str
    file_path: str
    scope_kind: str
    sha256: str
    filename: str
    body: str


class PackageImportResponse(BaseModel):
    import_id: str
    scope_kind: str
    export_id: str | None
    status: str