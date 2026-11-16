from typing import Literal

from pydantic import BaseModel, Field

ExportProfile = Literal["discussion", "redaction"]


class MasterExportRequest(BaseModel):
    profile: ExportProfile = "discussion"
    write_zip: bool = False


class FascicleExportRequest(BaseModel):
    profile: ExportProfile = "discussion"
    master_export_id: str | None = None
    write_zip: bool = False


class ExportRecordResponse(BaseModel):
    id: str
    project_id: str
    baseline_id: str
    export_id: str
    profile: str
    schema_name: str
    sha256: str
    file_path: str
    package_type: str
    parent_export_id: str | None
    created_at: str
    zip_path: str | None = None


class LlmGenerationExportRequest(BaseModel):
    profile: ExportProfile = "discussion"
    include_draft: bool = False
    fascicle_node_id: str | None = Field(default=None, description="Se definido, exporta só este fascículo.")


class LlmGenerationExportResponse(BaseModel):
    export_id: str
    file_path: str
    zip_path: str
    sha256: str
    manifest: dict