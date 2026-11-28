"""Seed e sincronização da estrutura documental CTBJ."""

from app.services.structure_seed.ctbj_v3_sync import CtbjSyncResult, apply_ctbj_v3_structure
from app.services.structure_seed.generic_sync import StructureSyncResult, apply_structure_catalog

__all__ = ["CtbjSyncResult", "apply_ctbj_v3_structure"]