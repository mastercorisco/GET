from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from openpyxl import Workbook

from sqlalchemy import select

from app.config import AppSettings
from app.models.document import DocumentNode
from app.services.document_service import compute_display_codes
from app.services.knowledge_service import list_items
from app.services.project_service import ProjectError, get_project
from app.services.reference_service import list_references
from app.services.technical_service import list_instances
from app.services.workbook.constants import (
    DATA_SHEETS,
    SHEET_A01,
    SHEET_ARTEFACTOS,
    SHEET_BLOCOS,
    SHEET_FASCICULOS,
    SHEET_FILOSOFIA,
    SHEET_LEITURA,
    SHEET_MAPA,
    WORKBOOK_IMPORT_VERSION,
)
from app.services.workbook.xlsx_writer import (
    write_data_rows,
    write_leitura_sheet,
    write_sheet_headers,
    write_sheet_notes,
    workbook_to_bytes,
)
from app.services.workspace_service import WorkspaceError, workspace_session

_APPLICATION_RE = re.compile(r"\n\n\*\*Aplicação:\*\*\s*", re.IGNORECASE)
_ARTEFACT_LINE_RE = re.compile(r"^(purpose|related_fasciculos|contract_state):\s*(.+)$", re.MULTILINE)


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _split_principle_content(content: str) -> tuple[str, str | None]:
    if not content:
        return "", None
    match = _APPLICATION_RE.search(content)
    if match:
        definition = content[: match.start()].strip()
        application = content[match.end() :].strip()
        return definition, application or None
    return content.strip(), None


def _artefact_columns(content: str, *, scope_type: str) -> dict[str, str | None]:
    row: dict[str, str | None] = {
        "purpose": None,
        "related_fasciculos": None,
        "contract_state": "Reutilizável" if scope_type == "library" else None,
    }
    if not content:
        return row
    parsed_any = False
    for match in _ARTEFACT_LINE_RE.finditer(content):
        parsed_any = True
        key = match.group(1)
        val = match.group(2).strip()
        if key in row:
            row[key] = val
    if not parsed_any and content.strip():
        row["purpose"] = content.strip()[:500]
    return row


def _a01_row_from_instance(instance) -> dict[str, str | None]:
    row: dict[str, str | None] = {
        "function_id": instance.export_code or instance.id[:8],
        "function": instance.name,
        "process_system": None,
    }
    if instance.reference_note:
        try:
            payload = json.loads(instance.reference_note)
            if isinstance(payload, dict):
                for key, val in payload.items():
                    if val is not None:
                        row[key] = str(val)
        except json.JSONDecodeError:
            row["communication_dependency"] = instance.reference_note[:500]
    return row


def _map_reference_row(ref) -> dict[str, str | None]:
    citation = ref.citation or ""
    parts = [p.strip() for p in citation.split("·")] if citation else []
    application = parts[0] if parts else None
    fasciculos = parts[1] if len(parts) > 1 else None
    priority = parts[2] if len(parts) > 2 else None
    return {
        "title": ref.title,
        "application": application,
        "fasciculos": fasciculos,
        "priority": priority,
        "note": ref.notes,
    }


def _build_workbook(
    *,
    leitura_title: str,
    leitura_subtitle: str,
    context_rows: list[tuple[str, str]],
    sheet_data: dict[str, list[dict[str, str | None]]],
) -> bytes:
    wb = Workbook()
    default = wb.active
    wb.remove(default)

    ws_leitura = wb.create_sheet(SHEET_LEITURA)
    write_leitura_sheet(ws_leitura, title=leitura_title, subtitle=leitura_subtitle, context_rows=context_rows)

    for sheet_name in DATA_SHEETS:
        ws = wb.create_sheet(sheet_name)
        write_sheet_notes(ws, sheet_name, f"Export GET — {WORKBOOK_IMPORT_VERSION}")
        write_sheet_headers(ws, sheet_name)
        rows = sheet_data.get(sheet_name) or []
        if rows:
            write_data_rows(ws, sheet_name, rows)

    return workbook_to_bytes(wb)


def build_workbook_export_project(app_settings: AppSettings, project_id: str) -> bytes:
    try:
        project = get_project(app_settings, project_id)
    except ProjectError as exc:
        raise ValueError(str(exc)) from exc

    with workspace_session(app_settings) as (session, _paths):
        nodes = list(session.scalars(select(DocumentNode).where(DocumentNode.project_id == project_id)))
        codes = compute_display_codes(nodes)
        by_id = {n.id: n for n in nodes}

        fascicle_rows: list[dict[str, str | None]] = []
        block_rows: list[dict[str, str | None]] = []
        for node in sorted(nodes, key=lambda n: (n.sort_key, n.title)):
            code = codes.get(node.id, "")
            if node.node_type == "fascicle" and not node.parent_id:
                fascicle_rows.append(
                    {
                        "codigo": code,
                        "designacao": node.title,
                        "natureza": None,
                        "objetivo": node.objective or None,
                    }
                )
            elif node.node_type == "block" and node.parent_id:
                parent = by_id.get(node.parent_id)
                parent_code = codes.get(node.parent_id, "") if parent else ""
                parent_title = parent.title if parent else None
                block_rows.append(
                    {
                        "block_code": code,
                        "fasciculo": parent_code,
                        "fasciculo_designacao": parent_title,
                        "block_title": node.title,
                        "estado": node.block_status or None,
                    }
                )

    principle_rows: list[dict[str, str | None]] = []
    artefact_rows: list[dict[str, str | None]] = []
    for item in list_items(app_settings, scope_type="project", scope_id=project_id):
        if not item.human_code:
            continue
        if item.knowledge_type == "principle":
            definition, application = _split_principle_content(item.content or "")
            principle_rows.append(
                {
                    "human_code": item.human_code,
                    "title": item.title,
                    "definition": definition or item.title,
                    "application": application,
                }
            )
        elif item.knowledge_type == "decision":
            extra = _artefact_columns(item.content or "", scope_type="project")
            artefact_rows.append(
                {
                    "human_code": item.human_code,
                    "title": item.title,
                    "purpose": extra.get("purpose"),
                    "related_fasciculos": extra.get("related_fasciculos"),
                    "contract_state": extra.get("contract_state"),
                }
            )

    a01_rows: list[dict[str, str | None]] = []
    for inst in list_instances(app_settings, project_id):
        if inst.kind != "function":
            continue
        a01_rows.append(_a01_row_from_instance(inst))

    ref_rows: list[dict[str, str | None]] = []
    for ref in list_references(app_settings, "library", None):
        ref_rows.append(_map_reference_row(ref))

    context_rows = [
        ("exported_at", _utcnow_iso()),
        ("source", f"project:{project_id}"),
        ("workbook_import_version", WORKBOOK_IMPORT_VERSION),
    ]
    subtitle = f"{project.name} | export {WORKBOOK_IMPORT_VERSION}"
    sheet_data = {
        SHEET_FASCICULOS: fascicle_rows,
        SHEET_BLOCOS: block_rows,
        SHEET_FILOSOFIA: principle_rows,
        SHEET_ARTEFACTOS: artefact_rows,
        SHEET_A01: a01_rows,
        SHEET_MAPA: ref_rows,
    }
    return _build_workbook(
        leitura_title="GET — Exportação workbook v1",
        leitura_subtitle=subtitle,
        context_rows=context_rows,
        sheet_data=sheet_data,
    )


def build_workbook_export_library(app_settings: AppSettings) -> bytes:
    artefact_rows: list[dict[str, str | None]] = []
    for item in list_items(app_settings, scope_type="library"):
        if not item.human_code or item.knowledge_type != "decision":
            continue
        extra = _artefact_columns(item.content or "", scope_type="library")
        artefact_rows.append(
            {
                "human_code": item.human_code,
                "title": item.title,
                "purpose": extra.get("purpose"),
                "related_fasciculos": extra.get("related_fasciculos"),
                "contract_state": extra.get("contract_state") or "Reutilizável",
            }
        )

    ref_rows: list[dict[str, str | None]] = []
    for ref in list_references(app_settings, "library", None):
        ref_rows.append(_map_reference_row(ref))

    context_rows = [
        ("exported_at", _utcnow_iso()),
        ("source", "library"),
        ("workbook_import_version", WORKBOOK_IMPORT_VERSION),
    ]
    sheet_data = {
        SHEET_ARTEFACTOS: artefact_rows,
        SHEET_MAPA: ref_rows,
    }
    return _build_workbook(
        leitura_title="GET — Exportação workbook v1",
        leitura_subtitle=f"Biblioteca EDA | export {WORKBOOK_IMPORT_VERSION}",
        context_rows=context_rows,
        sheet_data=sheet_data,
    )


def persist_workbook_export(
    app_settings: AppSettings,
    data: bytes,
    filename: str,
) -> str:
    try:
        with workspace_session(app_settings) as (_session, paths):
            paths.ensure_layout()
            out_dir = paths.exports_dir / "workbook"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / filename
            out_path.write_bytes(data)
            return str(out_path)
    except WorkspaceError as exc:
        raise ValueError(str(exc)) from exc