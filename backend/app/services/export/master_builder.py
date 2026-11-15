from __future__ import annotations

from app.services.export.context import ExportBuildContext
from app.services.export.fascicle_builder import _project_code, build_fascicle_package
from app.services.export.knowledge_mapper import export_knowledge_item
import hashlib


def build_master_package(
    ctx: ExportBuildContext,
    *,
    profile: str,
    export_id: str,
    fascicle_hashes: dict[str, str],
    warnings: list[dict],
    errors: list[dict],
) -> dict:
    document_structure = []
    fascicle_manifest = []
    for index, fascicle in enumerate(ctx.fascicle_roots(), start=1):
        code = ctx.frozen_code(fascicle.id)
        document_structure.append(
            {
                "id": fascicle.id,
                "node_type": fascicle.node_type,
                "display_code": code,
                "title": fascicle.title,
                "position": index,
            }
        )
        filename = f"{code}_{profile}.json"
        fascicle_manifest.append(
            {
                "fascicle_id": fascicle.id,
                "display_code": code,
                "title": fascicle.title,
                "revision": ctx.baseline.revision,
                "filename": filename,
                "content_hash": fascicle_hashes.get(fascicle.id),
            }
        )

    knowledge_index = []
    global_open_questions = []
    for item in ctx.project_knowledge_items():
        mapped = export_knowledge_item(
            ctx.session,
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
                "revision": mapped["revision"],
            }
        )
        if mapped["knowledge_type"] == "open_question":
            global_open_questions.append(
                {"id": item.id, "title": mapped["title"], "revision": mapped["revision"]}
            )

    system_catalog = []
    for row in ctx.technical_instances():
        if row.export_code:
            system_catalog.append({"code": row.export_code, "title": row.name})

    status = "valid"
    if warnings:
        status = "valid_with_warnings"
    if errors:
        status = "invalid"

    return {
        "schema_name": "get_project_master",
        "schema_version": "1.0.0",
        "application_version": "0.1.0",
        "package_type": "master",
        "export_profile": profile,
        "export_id": export_id,
        "created_at": ctx.baseline.created_at.isoformat(),
        "project": {
            "id": ctx.project_id,
            "code": _project_code(ctx.project.name),
            "name": ctx.project.name,
            "installation": ctx.project.name,
            "intervention_type": ctx.project.intervention_type,
            "description": ctx.project.name,
        },
        "baseline": {
            "id": ctx.baseline.id,
            "code": ctx.baseline.code,
            "revision": ctx.baseline.revision,
            "created_at": ctx.baseline.created_at.isoformat(),
        },
        "common_context": {
            "control_philosophy": ["Exportação MVP GET — contexto editável na aplicação."],
            "authoring_constraints": [
                "Não inventar parâmetros.",
                "Manter questões pendentes explícitas.",
            ],
        },
        "document_structure": document_structure,
        "system_catalog_summary": system_catalog,
        "knowledge_index": knowledge_index,
        "global_open_questions": global_open_questions,
        "fascicle_manifest": fascicle_manifest,
        "authoring_profile": {
            "language": "pt-PT",
            "role": "Engenheiro eletrotécnico sénior",
            "output": "structured_knowledge_discussion" if profile == "discussion" else "structured_knowledge_redaction",
        },
        "validation": {"status": status, "errors": errors, "warnings": warnings},
    }


def sha256_hex(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def build_fascicle_payloads(
    ctx: ExportBuildContext,
    *,
    profile: str,
    export_id_prefix: str,
    warnings: list[dict],
    errors: list[dict],
) -> dict[str, dict]:
    payloads: dict[str, dict] = {}
    for index, fascicle in enumerate(ctx.fascicle_roots(), start=1):
        fascicle_export_id = f"{export_id_prefix}-F{index:02d}"
        payloads[fascicle.id] = build_fascicle_package(
            ctx,
            fascicle,
            profile=profile,
            export_id=fascicle_export_id,
            warnings=warnings,
            errors=errors,
        )
    return payloads