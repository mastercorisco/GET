from __future__ import annotations

from pydantic import BaseModel, Field


class StructureCatalogTotals(BaseModel):
    fascicles: int
    blocks: int
    development_points: int = 0


class StructureCatalogSummary(BaseModel):
    id: str
    version: int
    display_name: str
    checksum: str = ""
    totals: StructureCatalogTotals
    project_template_code: str | None = None


class StructureCatalogListResponse(BaseModel):
    catalogs: list[StructureCatalogSummary]