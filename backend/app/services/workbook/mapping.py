from __future__ import annotations

from dataclasses import dataclass

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


@dataclass(frozen=True)
class SheetColumnSpec:
    key: str
    header: str
    required: bool = True


@dataclass(frozen=True)
class SheetSpec:
    name: str
    columns: tuple[SheetColumnSpec, ...]
    data_sheet: bool = True


SHEET_SPECS: dict[str, SheetSpec] = {
    SHEET_LEITURA: SheetSpec(
        name=SHEET_LEITURA,
        columns=(),
        data_sheet=False,
    ),
    SHEET_FASCICULOS: SheetSpec(
        name=SHEET_FASCICULOS,
        columns=(
            SheetColumnSpec("codigo", "Código"),
            SheetColumnSpec("designacao", "Designação"),
            SheetColumnSpec("natureza", "Natureza", required=False),
            SheetColumnSpec("objetivo", "Objetivo", required=False),
        ),
    ),
    SHEET_BLOCOS: SheetSpec(
        name=SHEET_BLOCOS,
        columns=(
            SheetColumnSpec("block_code", "Código do bloco"),
            SheetColumnSpec("fasciculo", "Fascículo"),
            SheetColumnSpec("fasciculo_designacao", "Designação do fascículo", required=False),
            SheetColumnSpec("block_title", "Designação do bloco"),
            SheetColumnSpec("natureza", "Natureza", required=False),
            SheetColumnSpec("estado", "Estado", required=False),
            SheetColumnSpec("prioridade", "Prioridade", required=False),
            SheetColumnSpec("observacoes", "Observações", required=False),
        ),
    ),
    SHEET_FILOSOFIA: SheetSpec(
        name=SHEET_FILOSOFIA,
        columns=(
            SheetColumnSpec("human_code", "ID"),
            SheetColumnSpec("title", "Princípio"),
            SheetColumnSpec("definition", "Definição"),
            SheetColumnSpec("application", "Aplicação", required=False),
        ),
    ),
    SHEET_ARTEFACTOS: SheetSpec(
        name=SHEET_ARTEFACTOS,
        columns=(
            SheetColumnSpec("human_code", "Código"),
            SheetColumnSpec("title", "Artefacto"),
            SheetColumnSpec("purpose", "Finalidade", required=False),
            SheetColumnSpec("related_fasciculos", "Fascículos relacionados", required=False),
            SheetColumnSpec("contract_state", "Estado contratual", required=False),
        ),
    ),
    SHEET_A01: SheetSpec(
        name=SHEET_A01,
        columns=(
            SheetColumnSpec("function_id", "function_id"),
            SheetColumnSpec("process_system", "process_system", required=False),
            SheetColumnSpec("function", "function", required=False),
            SheetColumnSpec("criticality", "criticality", required=False),
            SheetColumnSpec("normal_execution_level", "normal_execution_level", required=False),
            SheetColumnSpec("control_authority", "control_authority", required=False),
            SheetColumnSpec("local_control", "local_control", required=False),
            SheetColumnSpec("automatic_control", "automatic_control", required=False),
            SheetColumnSpec("distributed_control", "distributed_control", required=False),
            SheetColumnSpec("remote_reference_source", "remote_reference_source", required=False),
            SheetColumnSpec("remote_reference_required", "remote_reference_required", required=False),
            SheetColumnSpec(
                "reference_validity_criteria",
                "reference_validity_criteria",
                required=False,
            ),
            SheetColumnSpec("communication_dependency", "communication_dependency", required=False),
            SheetColumnSpec(
                "hardwired_critical_interface",
                "hardwired_critical_interface",
                required=False,
            ),
            SheetColumnSpec("local_autonomy", "local_autonomy", required=False),
            SheetColumnSpec(
                "loss_of_reference_behaviour",
                "loss_of_reference_behaviour",
                required=False,
            ),
            SheetColumnSpec("fallback_reference", "fallback_reference", required=False),
            SheetColumnSpec("fallback_strategy", "fallback_strategy", required=False),
            SheetColumnSpec("continuity_safe_state", "continuity_safe_state", required=False),
            SheetColumnSpec("final_safe_state", "final_safe_state", required=False),
            SheetColumnSpec("return_strategy", "return_strategy", required=False),
            SheetColumnSpec("safety_related", "safety_related", required=False),
            SheetColumnSpec("machinery_related", "machinery_related", required=False),
            SheetColumnSpec("responsible_system", "responsible_system", required=False),
            SheetColumnSpec("verification_method", "verification_method", required=False),
            SheetColumnSpec("acceptance_criterion", "acceptance_criterion", required=False),
        ),
    ),
    SHEET_MAPA: SheetSpec(
        name=SHEET_MAPA,
        columns=(
            SheetColumnSpec("title", "Norma/Regulamento"),
            SheetColumnSpec("application", "Aplicação", required=False),
            SheetColumnSpec("fasciculos", "Fascículos", required=False),
            SheetColumnSpec("priority", "Prioridade", required=False),
            SheetColumnSpec("note", "Nota", required=False),
        ),
    ),
}


def required_headers(sheet_name: str) -> list[str]:
    spec = SHEET_SPECS.get(sheet_name)
    if spec is None:
        return []
    return [col.header for col in spec.columns if col.required]


def mapping_document() -> dict:
    return {
        "schema": WORKBOOK_IMPORT_VERSION,
        "header_row": 4,
        "data_start_row": 5,
        "sheets": [
            {
                "name": spec.name,
                "data_sheet": spec.data_sheet,
                "columns": [
                    {"key": col.key, "header": col.header, "required": col.required}
                    for col in spec.columns
                ],
            }
            for spec in SHEET_SPECS.values()
            if spec.name in DATA_SHEETS or spec.name == SHEET_LEITURA
        ],
    }