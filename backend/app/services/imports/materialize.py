from __future__ import annotations

from app.models.document import DocumentNode
from app.services.export.context import ExportBuildContext
from app.services.export.fascicle_builder import build_fascicle_package
from app.services.imports.package_items import knowledge_items_by_id


def materialize_current_package(
    ctx: ExportBuildContext,
    fascicle: DocumentNode,
    profile: str,
    export_id: str,
) -> dict:
    warnings: list[dict] = []
    errors: list[dict] = []
    return build_fascicle_package(
        ctx,
        fascicle,
        profile=profile,
        export_id=export_id,
        warnings=warnings,
        errors=errors,
    )


def current_items_map(pkg: dict) -> dict[str, dict]:
    return knowledge_items_by_id(pkg)