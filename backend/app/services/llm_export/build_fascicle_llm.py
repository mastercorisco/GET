from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.document import DocumentNode
from app.services.llm_export.block_eligibility import count_exportable_points
from app.services.llm_export.catalogs import load_llm_generation_catalog
from app.services.llm_export.knowledge_view import build_knowledge_units
from app.services.llm_export.live_context import LlmLiveContext
from app.services.llm_export.project_payload import build_project_payload, parse_llm_context
from app.services.llm_export.validator import validate_llm_export


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_fascicle_llm_index(
    session: Session,
    ctx: LlmLiveContext,
    fascicle: DocumentNode,
    *,
    profile: str,
    include_draft: bool,
    export_id: str | None = None,
    generated_at: str | None = None,
    block_manifest: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    llm_ctx = parse_llm_context(ctx.project.llm_context_json)
    fascicle_code = ctx.display_code(fascicle.id)
    warnings: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []

    structure = []
    block_summaries = []
    blocks = ctx.blocks_in_fascicle(fascicle.id)
    for node in blocks:
        code = ctx.display_code(node.id)
        point_count = count_exportable_points(session, node.id, include_draft=include_draft)
        block_summaries.append(
            {
                "id": node.id,
                "display_code": code,
                "title": node.title,
                "purpose": node.objective or "",
                "exportable_point_count": point_count,
                "included_in_package": point_count > 0,
            }
        )
    for node in ctx.subtree_nodes(fascicle.id):
        structure.append(
            {
                "id": node.id,
                "node_type": node.node_type,
                "display_code": ctx.display_code(node.id),
                "title": node.title,
            }
        )

    knowledge_units = build_knowledge_units(
        session,
        block=fascicle,
        fascicle_id=fascicle.id,
        preparation_item_ids=set(),
        profile=profile,
        created_by=ctx.created_by,
        warnings=warnings,
    )

    catalog = load_llm_generation_catalog()

    package: dict[str, Any] = {
        "get_export": {
            "schema": "GET-LLM",
            "schema_version": "1.0",
            "export_type": "fascicle",
            "generated_at": generated_at or _utcnow_iso(),
            "language": "pt-PT",
        },
        "export_id": export_id or str(uuid.uuid4()),
        "project": build_project_payload(ctx.project),
        "generation_request": {
            "target": "fascicle",
            "target_id": fascicle_code,
            "purpose": "generate_technical_specification",
            "output_language": "pt-PT",
            "writing_style": "technical_procurement_specification",
            "detail_level": "detailed",
            "preserve_source_structure": True,
            "export_profile": profile,
        },
        "fascicle": {
            "id": fascicle.id,
            "display_code": fascicle_code,
            "title": fascicle.title,
            "purpose": llm_ctx.fascicle_overrides.get(fascicle.id, ""),
        },
        "document_structure": structure,
        "block_summaries": block_summaries,
        "block_manifest": block_manifest or [],
        "knowledge_units": knowledge_units,
        "standards": [],
        "open_points": [],
        "generation_rules": catalog.get("generation_rules", {}),
        "traceability": catalog.get("traceability", {}),
        "validation": {
            "status": "valid_with_warnings" if warnings else "valid",
            "warnings": warnings,
            "errors": errors,
        },
    }

    schema_errors = validate_llm_export(package)
    if schema_errors:
        errors.extend({"code": "SCHEMA", "message": msg} for msg in schema_errors[:5])
        package["validation"]["status"] = "invalid"
        package["validation"]["errors"] = errors
    return package