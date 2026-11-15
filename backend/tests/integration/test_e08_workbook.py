from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook

from app.config import set_active_workspace_root
from app.deps import get_settings
from app.main import app
from app.services.workbook.constants import DATA_SHEETS, HEADER_ROW, SHEET_A01, SHEET_BLOCOS, SHEET_FASCICULOS
from app.services.workbook.mapping import SHEET_SPECS
from app.services.workbook.migrate import run_workbook_migration
from app.services.workbook.template_builder import build_workbook_template
from app.services.workbook.extract import extract_workbook
from app.services.workbook.validate import validate_workbook_bytes

from tests.integration.test_e06_export import _workspace


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    cfg = tmp_path / "app-config.json"
    monkeypatch.setenv("GET_APP_CONFIG_PATH", str(cfg))
    get_settings.cache_clear()
    return TestClient(app)


def _write_headers(ws, sheet_name: str) -> None:
    for col_idx, col in enumerate(SHEET_SPECS[sheet_name].columns, start=1):
        ws.cell(row=HEADER_ROW, column=col_idx, value=col.header)


def _minimal_workbook_bytes() -> bytes:
    wb = Workbook()
    default = wb.active
    wb.remove(default)
    for sheet_name in ["00_Leitura", *DATA_SHEETS]:
        ws = wb.create_sheet(sheet_name)
        if sheet_name == "00_Leitura":
            ws.cell(row=2, column=1, value="Projecto teste E08 | v1")
            ws.cell(row=HEADER_ROW, column=1, value="Finalidade")
            ws.cell(row=HEADER_ROW, column=2, value="Teste")
            ws.cell(row=5, column=1, value="Nota")
            ws.cell(row=5, column=2, value="Contexto teste")
        else:
            _write_headers(ws, sheet_name)

    f = wb[SHEET_FASCICULOS]
    f.cell(row=5, column=1, value="F01")
    f.cell(row=5, column=2, value="Fascículo teste")
    f.cell(row=5, column=3, value="Projeto")
    f.cell(row=5, column=4, value="Objectivo")

    b = wb[SHEET_BLOCOS]
    b.cell(row=5, column=1, value="F01_B01")
    b.cell(row=5, column=2, value="F01")
    b.cell(row=5, column=4, value="Bloco teste")

    a01 = wb[SHEET_A01]
    a01.cell(row=5, column=1, value="FN-TEST-1")
    a01.cell(row=5, column=2, value="Sistema A")
    a01.cell(row=5, column=3, value="Função A")
    a01.cell(row=5, column=4, value="high")

    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def test_workbook_validate_and_template(client: TestClient, tmp_path: Path) -> None:
    data = _minimal_workbook_bytes()
    validation = validate_workbook_bytes(data)
    assert validation["valid"] is True
    assert validation["blocking_errors"] == 0
    xlsx_path = tmp_path / "minimal_probe.xlsx"
    xlsx_path.write_bytes(data)
    bundle, issues = extract_workbook(xlsx_path)
    assert bundle is not None
    assert not [i for i in issues if i.severity == "error"]
    assert bundle.a01_rows[0].fields.get("criticality") == "high"
    assert bundle.a01_rows[0].reference_note is not None

    tpl = client.get("/api/workbook/templates/project_import_v1")
    assert tpl.status_code == 200
    assert "spreadsheetml" in tpl.headers.get("content-type", "")
    built = build_workbook_template("library_import_v1")
    assert len(built) > 1000

    missing_col = validate_workbook_bytes(built)
    assert missing_col["valid"] is True

    bad = BytesIO()
    bad_wb = Workbook()
    ws = bad_wb.active
    ws.title = "01_Fasciculos"
    ws.cell(row=HEADER_ROW, column=1, value="Wrong")
    bad_wb.save(bad)
    bad_validation = validate_workbook_bytes(bad.getvalue())
    assert bad_validation["valid"] is False


def test_workbook_migrate_dry_run_and_apply(client: TestClient, tmp_path: Path) -> None:
    ws_root = tmp_path / "workspace"
    _workspace(client, tmp_path)

    xlsx_path = tmp_path / "minimal.xlsx"
    xlsx_path.write_bytes(_minimal_workbook_bytes())

    settings = get_settings()
    set_active_workspace_root(settings, ws_root)

    dry = run_workbook_migration(settings, xlsx_path, dry_run=True)
    assert dry.blocking_errors == 0
    report = json.loads(Path(dry.report_path).read_text(encoding="utf-8"))
    assert report["status"] == "ready"
    assert report["counts"]["fascicles"] == 1
    assert report["counts"]["blocks"] == 1
    assert report["counts"]["a01_rows"] == 1

    applied = run_workbook_migration(
        settings,
        xlsx_path,
        dry_run=False,
        confirm="I_UNDERSTAND",
    )
    assert applied.applied is True
    assert applied.project_id

    projects = client.get("/api/projects")
    assert projects.status_code == 200
    assert any(p["id"] == applied.project_id for p in projects.json())

    nodes = client.get(f"/api/projects/{applied.project_id}/document-nodes")
    assert nodes.status_code == 200
    types = {n["node_type"] for n in nodes.json()["nodes"]}
    assert "fascicle" in types and "block" in types

    tech = client.get(f"/api/projects/{applied.project_id}/instances")
    assert tech.status_code == 200
    assert len(tech.json()) >= 1


def test_workbook_validate_api(client: TestClient) -> None:
    data = _minimal_workbook_bytes()
    response = client.post(
        "/api/workbook/validate",
        files={"file": ("test.xlsx", data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 200
    assert response.json()["valid"] is True