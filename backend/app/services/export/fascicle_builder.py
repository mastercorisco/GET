from __future__ import annotations

from app.models.document import AssociationRole, DocumentNode
from app.models.knowledge import KnowledgeItem
from app.services.export.context import ExportBuildContext
from app.services.export.knowledge_mapper import (
    _EDIT_POLICY_DISCUSSION,
    _EDIT_POLICY_EDITABLE,
    export_knowledge_item,
)
from sqlalchemy import select


_WORKING_INSTRUCTIONS = {
    "preserve_existing_ids": True,
    "invent_missing_values": False,
    "treat_omissions_as_deletions": False,
    "return_complete_package": True,
    "notes": [
        "Novos objetos devem usar IDs temporários new_001, new_002, etc.",
        "Não alterar aprovação ou ciclo de vida.",
    ],
}


def _project_code(project_name: str) -> str:
    slug = "".join(ch for ch in project_name.upper() if ch.isalnum())[:12]
    return f"PRJ-{slug or 'PROJECT'}"


def build_fascicle_package(
    ctx: ExportBuildContext,
    fascicle: DocumentNode,
    *,
    profile: str,
    export_id: str,
    warnings: list[dict],
    errors: list[dict],
) -> dict:
    display_code = ctx.frozen_code(fascicle.id)
    structure = []
    for index, node in enumerate(ctx.subtree_nodes(fascicle.id), start=1):
        structure.append(
            {
                "node_id": node.id,
                "node_type": node.node_type,
                "display_code": ctx.frozen_code(node.id),
                "title": node.title,
                "position": index,
            }
        )

    protected_items: list[dict] = []
    editable_items: list[dict] = []
    seen: set[str] = set()

    for node in [fascicle] + ctx.subtree_nodes(fascicle.id):
        for assoc in ctx.associations_for(node.id):
            if assoc.knowledge_item_id in seen:
                continue
            item = ctx.session.get(KnowledgeItem, assoc.knowledge_item_id)
            if item is None:
                continue
            role = ctx.session.scalar(
                select(AssociationRole).where(AssociationRole.id == assoc.role_id)
            )
            role_code = role.code if role else ""
            mapped = export_knowledge_item(
                ctx.session,
                item,
                profile=profile,
                created_by=ctx.created_by,
                use_draft_if_no_revision=profile == "discussion",
                edit_policy=_EDIT_POLICY_EDITABLE if role_code != "mandatory_content" else _EDIT_POLICY_DISCUSSION,
                warnings=warnings,
            )
            if mapped is None:
                continue
            seen.add(item.id)
            if role_code == "mandatory_content":
                protected_items.append(mapped)
            else:
                editable_items.append(mapped)

    decisions = [i for i in editable_items if i["knowledge_type"] == "decision"]
    open_questions = [i for i in editable_items if i["knowledge_type"] == "open_question"]
    other_items = [i for i in editable_items if i["knowledge_type"] not in ("decision", "open_question")]

    technical = []
    for row in ctx.technical_instances():
        technical.append(
            {
                "instance_id": row.export_code or row.id,
                "class_code": row.kind,
                "title": row.name,
                "notes": row.reference_note or row.location_note,
            }
        )

    status = "valid"
    if warnings:
        status = "valid_with_warnings"
    if errors:
        status = "invalid"

    return {
        "schema_name": "get_fascicle_roundtrip",
        "schema_version": "1.0.0",
        "application_version": "0.1.0",
        "package_type": "fascicle_roundtrip",
        "export_profile": profile,
        "export_id": export_id,
        "created_at": ctx.baseline.created_at.isoformat(),
        "base_revision": ctx.baseline.revision,
        "project": {
            "id": ctx.project_id,
            "code": _project_code(ctx.project.name),
            "name": ctx.project.name,
        },
        "fascicle": {
            "id": fascicle.id,
            "display_code": display_code,
            "title": fascicle.title,
            "revision": ctx.baseline.revision,
            "scope": fascicle.title,
            "structure": structure,
        },
        "protected_context": {
            "purpose": "Contexto de leitura; alterações exigem proposta explícita.",
            "knowledge_items": protected_items,
        },
        "editable_knowledge": {
            "knowledge_items": other_items,
            "decisions": decisions,
            "open_questions": open_questions,
        },
        "technical_instances": technical,
        "authoring_profile": {
            "language": "pt-PT",
            "mode": profile,
            "instructions": [
                "Não inventar parâmetros.",
                "Preservar decisões confirmadas.",
            ],
        },
        "working_instructions": _WORKING_INSTRUCTIONS,
        "proposed_removals": [],
        "change_summary": [],
        "validation": {"status": status, "errors": errors, "warnings": warnings},
    }