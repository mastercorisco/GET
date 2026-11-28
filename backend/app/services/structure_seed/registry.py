"""Registo de catálogos de estrutura documental."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from app.services.structure_seed.catalog_loader import load_structure_catalog_file
from app.services.structure_seed.catalog_types import StructureCatalog
from app.services.structure_seed.ctbj_catalog import DEFAULT_CATALOG as CTBJ_CATALOG_PATH, load_ctbj_catalog

REPO_ROOT = Path(__file__).resolve().parents[4]
GENERIC_EXAMPLE_PATH = REPO_ROOT / "catalogs" / "structure_catalog_generic_example.pt-PT.json"


@dataclass(frozen=True)
class CatalogRegistryEntry:
    id: str
    path: Path
    display_name: str
    project_template_code: str | None
    loader: Callable[[], StructureCatalog]


def _load_ctbj() -> StructureCatalog:
    return load_ctbj_catalog()


def _load_generic_example() -> StructureCatalog:
    return load_structure_catalog_file(GENERIC_EXAMPLE_PATH)


_REGISTRY: dict[str, CatalogRegistryEntry] = {
    "ctbj_v3": CatalogRegistryEntry(
        id="ctbj_v3",
        path=CTBJ_CATALOG_PATH,
        display_name="CTBJ v3 — brownfield CSC",
        project_template_code="brownfield-cee-csc",
        loader=_load_ctbj,
    ),
    "generic_example_v1": CatalogRegistryEntry(
        id="generic_example_v1",
        path=GENERIC_EXAMPLE_PATH,
        display_name="Estrutura documental genérica (exemplo)",
        project_template_code="generic-structure-v1",
        loader=_load_generic_example,
    ),
}


def registered_catalog_ids() -> list[str]:
    return list(_REGISTRY.keys())


def get_registry_entry(catalog_id: str) -> CatalogRegistryEntry:
    entry = _REGISTRY.get(catalog_id)
    if entry is None:
        raise KeyError(f"Catálogo desconhecido: {catalog_id}")
    return entry


def load_catalog(catalog_id: str) -> StructureCatalog:
    return get_registry_entry(catalog_id).loader()


def list_catalog_summaries() -> list[dict]:
    out: list[dict] = []
    for entry in _REGISTRY.values():
        catalog = entry.loader()
        out.append(
            {
                "id": catalog.id,
                "version": catalog.version,
                "display_name": catalog.display_name or entry.display_name,
                "checksum": catalog.checksum,
                "totals": {
                    "fascicles": catalog.fascicle_count,
                    "blocks": catalog.block_count,
                    "development_points": catalog.point_count,
                },
                "project_template_code": entry.project_template_code,
            }
        )
    return out