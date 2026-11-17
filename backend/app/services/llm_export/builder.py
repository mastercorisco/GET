from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import DocumentNode
from app.models.project import Project
from app.models.reference import Reference, StandardProfile
from app.schemas.project import ProjectLlmContext
from app.services.document_service import compute_display_codes
from app.domain.document_lexicon import annotate_node_role, merge_generation_rules_with_lexicon
from app.services.llm_export.catalogs import load_llm_generation_catalog
from app.services.llm_export.knowledge_view import build_knowledge_units
from app.services.llm_export.preparation import build_block_preparation
from app.services.llm_export.validator import validate_llm_export


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_llm_context(raw: str) -> ProjectLlmContext:
    try:
        data = json.loads(raw or "{}")
    except json.JSONDecodeError:
        data = {}
    if not isinstance(data, dict):
        data = {}
    return ProjectLlmContext.model_validate(data)


def _block_code_suffix(display_code: str) -> str:
    if "_B" in display_code:
        return display_code.rsplit("_B", 1)[-1]
    return display_code


def _build_standards(session: Session, reference_ids: set[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for ref_id in sorted(reference_ids):
        ref = session.get(Reference, ref_id)
        if ref is None:
            continue
        profile = session.get(StandardProfile, ref_id)
        code = profile.code if profile and profile.code else (ref.citation or ref.title)
        application = ""
        mandatory = False
        if profile is not None:
            application = profile.applicability_text or profile.eda_interpretation or ref.notes or ""
            mandatory = (profile.contractual_role or "").lower() == "mandatory"
        rows.append(
            {
                "reference_id": ref_id,
                "standard": code,
                "application": application,
                "mandatory": mandatory,
            }
        )
    return rows


def _open_points_from_bundle(
    preparation_open: list[dict[str, Any]],
    knowledge_units: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []
    seen: set[str] = set()
    for idx, oq in enumerate(preparation_open, start=1):
        question = oq.get("question") or oq.get("text") or oq.get("prompt") or ""
        if not str(question).strip():
            continue
        oid = str(oq.get("id") or f"OP-PREP-{idx}")
        if oid in seen:
            continue
        seen.add(oid)
        points.append({"id": oid, "question": str(question).strip(), "status": oq.get("status", "open")})
    for ku in knowledge_units:
        if ku.get("type") != "open_question":
            continue
        kid = str(ku["id"])
        if kid in seen:
            continue
        seen.add(kid)
        points.append(
            {
                "id": kid,
                "question": ku.get("title") or ku.get("statement") or "",
                "status": "open",
            }
        )
    return points


def build_llm_block_export(
    session: Session,
    block_id: str,
    *,
    include_draft: bool = False,
    profile: str = "discussion",
    export_id: str | None = None,
    generated_at: str | None = None,
    created_by: str = "local_user",
) -> dict[str, Any]:
    block, bundle = build_block_preparation(session, block_id, include_draft=include_draft)
    project = session.get(Project, block.project_id)
    if project is None:
        raise ValueError("Projeto não encontrado.")

    llm_ctx = _parse_llm_context(project.llm_context_json)
    fascicle_id = bundle.fascicle_id
    fascicle: DocumentNode | None = session.get(DocumentNode, fascicle_id) if fascicle_id else None
    nodes = list(session.scalars(select(DocumentNode).where(DocumentNode.project_id == block.project_id)))
    codes = compute_display_codes(nodes)
    fascicle_code = codes.get(fascicle_id, "") if fascicle_id else ""

    warnings: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []

    knowledge_units = build_knowledge_units(
        session,
        block=block,
        fascicle_id=fascicle_id,
        preparation_item_ids=bundle.knowledge_item_ids,
        profile=profile,
        created_by=created_by,
        warnings=warnings,
    )
    for ku in knowledge_units:
        if not ku.get("requirements"):
            warnings.append(
                {
                    "code": "NO_STRUCTURED_REQUIREMENTS",
                    "message": f"Unidade {ku.get('id')} sem requisitos estruturados em technical_profile.",
                }
            )

    catalog = load_llm_generation_catalog()
    target_output = bundle.target_output
    purpose = str(target_output.get("purpose") or "generate_technical_specification")
    detail_level = str(target_output.get("detail_level") or "detailed")
    writing_style = str(target_output.get("writing_style") or "technical_procurement_specification")

    project_payload: dict[str, Any] = {
        "id": project.id,
        "name": project.name,
        "intervention_type": project.intervention_type,
    }
    if llm_ctx.code:
        project_payload["code"] = llm_ctx.code
    if llm_ctx.owner:
        project_payload["owner"] = llm_ctx.owner
    if llm_ctx.location is not None:
        project_payload["location"] = llm_ctx.location.model_dump(exclude_none=True)
    if llm_ctx.project_type:
        project_payload["project_type"] = llm_ctx.project_type
    if llm_ctx.document_type:
        project_payload["document_type"] = llm_ctx.document_type

    fascicle_payload = annotate_node_role(
        {
            "id": fascicle_id or block.id,
            "display_code": fascicle_code,
            "title": fascicle.title if fascicle else "",
            "purpose": (llm_ctx.fascicle_overrides.get(fascicle_id or "", "") if fascicle_id else ""),
        },
        "fascicle",
    )

    preparation = {
        "applicable_premises": bundle.block_premises,
        "development_points": bundle.export_points,
        "supporting_context": {
            "knowledge_items": bundle.supporting_knowledge,
            "references": bundle.supporting_references,
            "examples": bundle.supporting_examples,
        },
        "unresolved_matters": {
            "open_questions": bundle.open_questions,
            "missing_information": bundle.missing_information,
        },
    }

    package: dict[str, Any] = {
        "get_export": {
            "schema": "GET-LLM",
            "schema_version": "1.0",
            "export_type": "block",
            "generated_at": generated_at or _utcnow_iso(),
            "language": "pt-PT",
        },
        "export_id": export_id or str(uuid.uuid4()),
        "project": project_payload,
        "generation_request": {
            "target": "block",
            "target_id": bundle.display_code or block_id,
            "purpose": purpose,
            "output_language": "pt-PT",
            "writing_style": writing_style,
            "detail_level": detail_level,
            "preserve_source_structure": True,
            "export_profile": profile,
        },
        "fascicle": fascicle_payload,
        "block": annotate_node_role(
            {
                "id": block.id,
                "display_code": bundle.display_code,
                "code": _block_code_suffix(bundle.display_code),
                "title": block.title,
                "purpose": block.objective or "",
                "scope": {
                    "narrative": block.scope or "",
                    "includes": bundle.scope_includes,
                    "excludes": bundle.scope_excludes,
                },
            },
            "block",
        ),
        "knowledge_units": knowledge_units,
        "standards": _build_standards(session, bundle.reference_ids),
        "open_points": _open_points_from_bundle(bundle.open_questions, knowledge_units),
        "generation_rules": merge_generation_rules_with_lexicon(catalog),
        "traceability": catalog.get("traceability", {}),
        "preparation": preparation,
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