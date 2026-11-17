from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeItem
from app.models.technical import TechnicalInstance
from app.services.export.knowledge_mapper import export_knowledge_item
from app.domain.document_lexicon import annotate_node_role, merge_generation_rules_with_lexicon
from app.services.llm_export.catalogs import load_llm_generation_catalog
from app.services.llm_export.live_context import LlmLiveContext
from app.services.llm_export.project_payload import build_project_payload
from app.services.llm_export.validator import validate_llm_export


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_master_llm(
    session: Session,
    ctx: LlmLiveContext,
    *,
    profile: str,
    export_id: str | None = None,
    generated_at: str | None = None,
    fascicle_manifest: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    warnings: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []

    document_structure = []
    for fascicle in ctx.fascicle_roots():
        document_structure.append(
            annotate_node_role(
                {
                    "id": fascicle.id,
                    "display_code": ctx.display_code(fascicle.id),
                    "title": fascicle.title,
                    "node_type": "fascicle",
                },
                "fascicle",
            )
        )

    knowledge_index = []
    global_open_questions = []
    items = list(
        session.scalars(
            select(KnowledgeItem).where(
                KnowledgeItem.scope_type == "project",
                KnowledgeItem.scope_id == ctx.project_id,
            )
        )
    )
    for item in items:
        mapped = export_knowledge_item(
            session,
            item,
            profile=profile,
            created_by=ctx.created_by,
            use_draft_if_no_revision=profile == "discussion",
            warnings=warnings,
        )
        if mapped is None:
            continue
        knowledge_index.append(
            {
                "id": item.id,
                "code": item.human_code,
                "title": mapped["title"],
                "knowledge_type": mapped["knowledge_type"],
                "revision": mapped["revision"],
            }
        )
        if mapped["knowledge_type"] == "open_question":
            global_open_questions.append({"id": item.id, "title": mapped["title"]})

    system_catalog = []
    for row in session.scalars(select(TechnicalInstance).where(TechnicalInstance.project_id == ctx.project_id)):
        if row.export_code:
            system_catalog.append({"code": row.export_code, "title": row.name})

    catalog = load_llm_generation_catalog()

    package: dict[str, Any] = {
        "get_export": {
            "schema": "GET-LLM",
            "schema_version": "1.0",
            "export_type": "project_master",
            "generated_at": generated_at or _utcnow_iso(),
            "language": "pt-PT",
        },
        "export_id": export_id or str(uuid.uuid4()),
        "project": build_project_payload(ctx.project),
        "generation_request": {
            "target": "project",
            "target_id": ctx.project_id,
            "purpose": "generate_technical_specification",
            "output_language": "pt-PT",
            "writing_style": "technical_procurement_specification",
            "detail_level": "detailed",
            "preserve_source_structure": True,
            "export_profile": profile,
        },
        "common_context": {
            "note": (
                "Enquadramento global; detalhe por capítulo e ponto "
                "(chaves JSON fascicle/block) nos ficheiros referenciados no manifesto."
            ),
        },
        "document_structure": document_structure,
        "knowledge_index": knowledge_index,
        "global_open_questions": global_open_questions,
        "system_catalog_summary": system_catalog,
        "fascicle_manifest": [
            annotate_node_role(entry, "fascicle") if "text_production_label_pt" not in entry else entry
            for entry in (fascicle_manifest or [])
        ],
        "generation_rules": merge_generation_rules_with_lexicon(catalog),
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