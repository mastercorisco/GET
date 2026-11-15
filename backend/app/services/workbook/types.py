from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


Severity = Literal["error", "warning", "info"]


@dataclass
class MigrationIssue:
    severity: Severity
    sheet: str | None
    row: int | None
    column: str | None
    message: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "sheet": self.sheet,
            "row": self.row,
            "column": self.column,
            "message": self.message,
        }


@dataclass
class FascicleRow:
    source_row: int
    codigo: str
    designacao: str
    natureza: str | None
    objetivo: str | None


@dataclass
class BlockRow:
    source_row: int
    block_code: str
    fasciculo: str
    block_title: str
    natureza: str | None
    extra: dict[str, str | None] = field(default_factory=dict)


@dataclass
class PrincipleRow:
    source_row: int
    human_code: str
    title: str
    content: str


@dataclass
class ArtefactRow:
    source_row: int
    human_code: str
    title: str
    content: str
    scope_type: str


@dataclass
class A01Row:
    source_row: int
    function_id: str
    name: str
    reference_note: str | None
    fields: dict[str, str | None]


@dataclass
class ReferenceRow:
    source_row: int
    title: str
    citation: str | None
    notes: str | None


@dataclass
class WorkbookBundle:
    workbook_path: str
    workbook_sha256: str
    project_name: str
    project_context: dict[str, str]
    fascicles: list[FascicleRow]
    blocks: list[BlockRow]
    principles: list[PrincipleRow]
    artefacts: list[ArtefactRow]
    a01_rows: list[A01Row]
    references: list[ReferenceRow]


@dataclass
class MigrationRunResult:
    run_id: str
    report_path: str
    blocking_errors: int
    warnings: int
    applied: bool
    project_id: str | None = None