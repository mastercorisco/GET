from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.services.workbook.constants import (
    DATA_SHEETS,
    SHEET_A01,
    SHEET_ARTEFACTOS,
    SHEET_BLOCOS,
    SHEET_FASCICULOS,
    SHEET_FILOSOFIA,
    SHEET_LEITURA,
    SHEET_MAPA,
)
from app.services.workbook.mapping import SHEET_SPECS
from app.services.workbook.reader import WorkbookReader, normalize_cell
from app.services.workbook.scope import resolve_scope
from app.services.workbook.types import (
    A01Row,
    ArtefactRow,
    BlockRow,
    FascicleRow,
    MigrationIssue,
    PrincipleRow,
    ReferenceRow,
    WorkbookBundle,
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _header_index_map(headers: list[str | None], sheet_name: str) -> dict[str, int]:
    spec = SHEET_SPECS[sheet_name]
    index: dict[str, int] = {}
    normalized = [h.strip() if h else None for h in headers]
    for col in spec.columns:
        try:
            idx = normalized.index(col.header)
        except ValueError:
            continue
        index[col.key] = idx
    return index


def _validate_headers(sheet_name: str, headers: list[str | None], issues: list[MigrationIssue]) -> dict[str, int] | None:
    spec = SHEET_SPECS[sheet_name]
    index = _header_index_map(headers, sheet_name)
    missing = [col.header for col in spec.columns if col.required and col.key not in index]
    if missing:
        issues.append(
            MigrationIssue(
                severity="error",
                sheet=sheet_name,
                row=4,
                column=None,
                message=f"Cabeçalhos obrigatórios em falta: {', '.join(missing)}",
            )
        )
        return None
    return index


def _project_name(reader: WorkbookReader) -> str:
    subtitle = reader.cell_text(SHEET_LEITURA, 2, 1)
    if subtitle and "|" in subtitle:
        return subtitle.split("|", 1)[0].strip()
    if subtitle:
        return subtitle.strip()
    return "Projeto GET (workbook)"


def _project_context(reader: WorkbookReader) -> dict[str, str]:
    context: dict[str, str] = {}
    for row_num, row in reader.iter_data_rows(SHEET_LEITURA):
        key = normalize_cell(row[0]) if row else None
        value = normalize_cell(row[1]) if len(row) > 1 else None
        if key and value:
            context[key] = value
    return context


def extract_workbook(path: Path) -> tuple[WorkbookBundle | None, list[MigrationIssue]]:
    issues: list[MigrationIssue] = []
    reader = WorkbookReader(path)
    try:
        for sheet_name in DATA_SHEETS:
            if sheet_name not in reader.sheet_names():
                issues.append(
                    MigrationIssue(
                        severity="error",
                        sheet=sheet_name,
                        row=None,
                        column=None,
                        message="Folha obrigatória em falta.",
                    )
                )

        if any(i.severity == "error" for i in issues):
            return None, issues

        fascicles: list[FascicleRow] = []
        blocks: list[BlockRow] = []
        principles: list[PrincipleRow] = []
        artefacts: list[ArtefactRow] = []
        a01_rows: list[A01Row] = []
        references: list[ReferenceRow] = []

        def get_col(row: tuple, index_map: dict[str, int], key: str) -> str | None:
            idx = index_map.get(key)
            if idx is None or idx >= len(row):
                return None
            return normalize_cell(row[idx])

        # Fascículos
        f_headers = reader.header_row(SHEET_FASCICULOS)
        f_map = _validate_headers(SHEET_FASCICULOS, f_headers, issues)
        if f_map:
            for row_num, row in reader.iter_data_rows(SHEET_FASCICULOS):
                codigo = get_col(row, f_map, "codigo")
                designacao = get_col(row, f_map, "designacao")
                if not codigo or not designacao:
                    issues.append(
                        MigrationIssue("error", SHEET_FASCICULOS, row_num, "Código/Designação", "Linha incompleta.")
                    )
                    continue
                fascicles.append(
                    FascicleRow(
                        source_row=row_num,
                        codigo=codigo,
                        designacao=designacao,
                        natureza=get_col(row, f_map, "natureza"),
                        objetivo=get_col(row, f_map, "objetivo"),
                    )
                )

        # Blocos
        b_headers = reader.header_row(SHEET_BLOCOS)
        b_map = _validate_headers(SHEET_BLOCOS, b_headers, issues)
        fascicle_codes = {f.codigo for f in fascicles}
        if b_map:
            for row_num, row in reader.iter_data_rows(SHEET_BLOCOS):
                block_code = get_col(row, b_map, "block_code")
                fasciculo = get_col(row, b_map, "fasciculo")
                title = get_col(row, b_map, "block_title")
                if not block_code or not fasciculo or not title:
                    issues.append(
                        MigrationIssue("error", SHEET_BLOCOS, row_num, None, "Bloco incompleto (código/fascículo/título).")
                    )
                    continue
                if fascicle_codes and fasciculo not in fascicle_codes:
                    issues.append(
                        MigrationIssue(
                            "warning",
                            SHEET_BLOCOS,
                            row_num,
                            "Fascículo",
                            f"Fascículo {fasciculo} não listado em 01_Fasciculos.",
                        )
                    )
                extra = {
                    "natureza": get_col(row, b_map, "natureza"),
                    "estado": get_col(row, b_map, "estado"),
                    "prioridade": get_col(row, b_map, "prioridade"),
                    "observacoes": get_col(row, b_map, "observacoes"),
                }
                blocks.append(
                    BlockRow(
                        source_row=row_num,
                        block_code=block_code,
                        fasciculo=fasciculo,
                        block_title=title,
                        natureza=extra["natureza"],
                        extra=extra,
                    )
                )

        # Filosofia
        p_headers = reader.header_row(SHEET_FILOSOFIA)
        p_map = _validate_headers(SHEET_FILOSOFIA, p_headers, issues)
        if p_map:
            for row_num, row in reader.iter_data_rows(SHEET_FILOSOFIA):
                human_code = get_col(row, p_map, "human_code")
                title = get_col(row, p_map, "title")
                definition = get_col(row, p_map, "definition")
                application = get_col(row, p_map, "application")
                if not human_code or not title or not definition:
                    issues.append(
                        MigrationIssue("error", SHEET_FILOSOFIA, row_num, None, "Princípio incompleto (ID/título/definição).")
                    )
                    continue
                content = definition
                if application:
                    content = f"{definition}\n\n**Aplicação:** {application}"
                principles.append(
                    PrincipleRow(source_row=row_num, human_code=human_code, title=title, content=content)
                )

        # Artefactos
        a_headers = reader.header_row(SHEET_ARTEFACTOS)
        a_map = _validate_headers(SHEET_ARTEFACTOS, a_headers, issues)
        if a_map:
            for row_num, row in reader.iter_data_rows(SHEET_ARTEFACTOS):
                human_code = get_col(row, a_map, "human_code")
                title = get_col(row, a_map, "title")
                if not human_code or not title:
                    issues.append(MigrationIssue("error", SHEET_ARTEFACTOS, row_num, None, "Artefacto incompleto."))
                    continue
                parts = []
                for key in ("purpose", "related_fasciculos", "contract_state"):
                    val = get_col(row, a_map, key)
                    if val:
                        parts.append(f"{key}: {val}")
                natureza = get_col(row, a_map, "contract_state")
                artefacts.append(
                    ArtefactRow(
                        source_row=row_num,
                        human_code=human_code,
                        title=title,
                        content="\n".join(parts) if parts else title,
                        scope_type=resolve_scope(natureza),
                    )
                )

        # A01
        a01_headers = reader.header_row(SHEET_A01)
        a01_map = _validate_headers(SHEET_A01, a01_headers, issues)
        if a01_map:
            all_keys = list(a01_map.keys())
            for row_num, row in reader.iter_data_rows(SHEET_A01):
                function_id = get_col(row, a01_map, "function_id")
                if not function_id:
                    issues.append(MigrationIssue("error", SHEET_A01, row_num, "function_id", "function_id em falta."))
                    continue
                fields = {key: get_col(row, a01_map, key) for key in all_keys}
                fn_name = fields.get("function") or fields.get("process_system") or function_id
                note_payload = {k: v for k, v in fields.items() if k not in ("function_id", "function", "process_system") and v}
                reference_note = json.dumps(note_payload, ensure_ascii=False) if note_payload else None
                a01_rows.append(
                    A01Row(
                        source_row=row_num,
                        function_id=function_id,
                        name=fn_name,
                        reference_note=reference_note,
                        fields=fields,
                    )
                )

        # Mapa normativo
        r_headers = reader.header_row(SHEET_MAPA)
        r_map = _validate_headers(SHEET_MAPA, r_headers, issues)
        if r_map:
            for row_num, row in reader.iter_data_rows(SHEET_MAPA):
                title = get_col(row, r_map, "title")
                if not title:
                    issues.append(MigrationIssue("error", SHEET_MAPA, row_num, "Norma/Regulamento", "Título em falta."))
                    continue
                app = get_col(row, r_map, "application")
                fasc = get_col(row, r_map, "fasciculos")
                priority = get_col(row, r_map, "priority")
                note = get_col(row, r_map, "note")
                citation_parts = [p for p in (app, fasc, priority) if p]
                citation = " · ".join(citation_parts) if citation_parts else None
                references.append(
                    ReferenceRow(
                        source_row=row_num,
                        title=title,
                        citation=citation,
                        notes=note,
                    )
                )

        bundle = WorkbookBundle(
            workbook_path=str(path),
            workbook_sha256=_sha256(path),
            project_name=_project_name(reader),
            project_context=_project_context(reader),
            fascicles=fascicles,
            blocks=blocks,
            principles=principles,
            artefacts=artefacts,
            a01_rows=a01_rows,
            references=references,
        )
        return bundle, issues
    finally:
        reader.close()