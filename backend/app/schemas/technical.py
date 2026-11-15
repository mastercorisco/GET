from typing import Literal

from pydantic import BaseModel, Field

TechnicalKind = Literal["system", "equipment", "function"]


class TechnicalClassCreateRequest(BaseModel):
    kind: TechnicalKind
    code: str = Field(min_length=1)
    label: str = Field(min_length=1)


class TechnicalClassResponse(BaseModel):
    id: str
    kind: str
    code: str
    label: str


class TechnicalInstanceCreateRequest(BaseModel):
    kind: TechnicalKind
    name: str = Field(min_length=1)
    parent_id: str | None = None
    class_id: str | None = None
    export_code: str | None = None
    location_note: str | None = None
    reference_note: str | None = None


class TechnicalInstanceResponse(BaseModel):
    id: str
    project_id: str
    parent_id: str | None
    class_id: str | None
    kind: str
    name: str
    export_code: str | None
    location_note: str | None
    reference_note: str | None
    depth: int