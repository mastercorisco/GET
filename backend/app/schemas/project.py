from typing import Any

from pydantic import BaseModel, Field


class TemplateVersionResponse(BaseModel):
    id: str
    template_id: str
    template_code: str
    template_name: str
    version: int
    metadata_json: str


class TemplateResponse(BaseModel):
    id: str
    code: str
    name: str
    description: str
    versions: list[TemplateVersionResponse] = Field(default_factory=list)


class ProjectCreateRequest(BaseModel):
    template_version_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    intervention_type: str = Field(min_length=1, default="brownfield")


class ProjectResponse(BaseModel):
    id: str
    name: str
    template_version_id: str
    template_code: str
    template_version: int
    intervention_type: str
    library_version_id: str
    library_version: int


class ProjectLocationContext(BaseModel):
    site: str | None = None
    address: str | None = None
    locality: str | None = None
    island: str | None = None
    region: str | None = None
    country: str | None = None


class StructureCatalogStamp(BaseModel):
    id: str
    checksum: str
    applied_at: str | None = None


class ProjectLlmContext(BaseModel):
    code: str | None = None
    owner: str | None = None
    location: ProjectLocationContext | None = None
    project_type: str | None = None
    document_type: str | None = None
    fascicle_overrides: dict[str, str] = Field(default_factory=dict)
    structure_catalog: StructureCatalogStamp | None = None


class ProjectLlmContextResponse(BaseModel):
    project_id: str
    context: ProjectLlmContext


class ProjectLlmContextPatch(BaseModel):
    context: ProjectLlmContext

