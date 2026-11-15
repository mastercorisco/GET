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