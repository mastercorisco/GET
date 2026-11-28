"""Compatibilidade CTBJ v3 sobre sincronização genérica de catálogo."""

from __future__ import annotations

from app.config import AppSettings
from app.services.structure_seed.catalog_types import StructureCatalog
from app.services.structure_seed.ctbj_catalog import load_ctbj_catalog
from app.services.structure_seed.generic_sync import (
    StructureSyncResult,
    SyncMode,
    apply_structure_catalog,
)

EXPECTED_FASCICLES = 20
EXPECTED_BLOCKS = 179
EXPECTED_POINTS = 869

CtbjSyncResult = StructureSyncResult


def apply_ctbj_v3_structure(
    app_settings: AppSettings,
    project_id: str,
    *,
    mode: SyncMode = "migrate",
    dry_run: bool = True,
    catalog: StructureCatalog | None = None,
    backup_id: str | None = None,
    preserve_rich_content: bool = True,
) -> StructureSyncResult:
    resolved = catalog or load_ctbj_catalog()
    return apply_structure_catalog(
        app_settings,
        project_id,
        mode=mode,
        dry_run=dry_run,
        catalog=resolved,
        backup_id=backup_id,
        preserve_rich_content=preserve_rich_content,
        exclusive_lock="ctbj_v3_sync",
        report_prefix="ctbj_v3",
    )