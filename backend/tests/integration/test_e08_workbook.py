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
from app.services.workbook.mapping import mapping_document
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


def test_workbook_migrate_api_new_project(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)

    data = _minimal_workbook_bytes()
    dry = client.post(
        "/api/workbook/migrate",
        data={"dry_run": "true"},
        files={"file": ("test.xlsx", data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert dry.status_code == 200
    body = dry.json()
    assert body["status"] == "ready"
    assert body["run_id"]
    assert body["counts"]["fascicles"] == 1

    report = client.get(f"/api/workbook/migration-reports/{body['run_id']}")
    assert report.status_code == 200
    assert report.json()["run_id"] == body["run_id"]

    bad_apply = client.post(
        "/api/workbook/migrate/apply",
        json={
            "run_id": body["run_id"],
            "confirm": "WRONG",
            "target": "new_project",
        },
    )
    assert bad_apply.status_code == 400

    applied = client.post(
        "/api/workbook/migrate/apply",
        json={
            "run_id": body["run_id"],
            "confirm": "I_UNDERSTAND",
            "target": "new_project",
        },
    )
    assert applied.status_code == 200
    project_id = applied.json()["project_id"]
    assert project_id

    projects = client.get("/api/projects")
    assert any(p["id"] == project_id for p in projects.json())


def test_workbook_migrate_api_existing_project(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    data = _minimal_workbook_bytes()

    first_dry = client.post(
        "/api/workbook/migrate",
        data={"dry_run": "true"},
        files={"file": ("test.xlsx", data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert first_dry.status_code == 200
    first_apply = client.post(
        "/api/workbook/migrate/apply",
        json={
            "run_id": first_dry.json()["run_id"],
            "confirm": "I_UNDERSTAND",
            "target": "new_project",
        },
    )
    assert first_apply.status_code == 200
    project_id = first_apply.json()["project_id"]
    assert project_id

    nodes_before = client.get(f"/api/projects/{project_id}/document-nodes").json()["nodes"]
    fascicle_count = sum(1 for n in nodes_before if n["node_type"] == "fascicle")

    dry = client.post(
        "/api/workbook/migrate",
        data={"dry_run": "true"},
        files={"file": ("test2.xlsx", data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert dry.status_code == 200
    run_id = dry.json()["run_id"]

    applied = client.post(
        "/api/workbook/migrate/apply",
        json={
            "run_id": run_id,
            "confirm": "I_UNDERSTAND",
            "target": "existing_project",
            "project_id": project_id,
        },
    )
    assert applied.status_code == 200
    summary = applied.json().get("summary") or {}
    assert summary.get("fascicles_added", 0) == 0
    assert summary.get("blocks_added", 0) == 0

    nodes_after = client.get(f"/api/projects/{project_id}/document-nodes").json()["nodes"]
    assert sum(1 for n in nodes_after if n["node_type"] == "fascicle") == fascicle_count


def test_workbook_export_project_validates(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    data = _minimal_workbook_bytes()
    dry = client.post(
        "/api/workbook/migrate",
        data={"dry_run": "true"},
        files={"file": ("test.xlsx", data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    applied = client.post(
        "/api/workbook/migrate/apply",
        json={
            "run_id": dry.json()["run_id"],
            "confirm": "I_UNDERSTAND",
            "target": "new_project",
        },
    )
    project_id = applied.json()["project_id"]

    export = client.get(f"/api/workbook/export/project/{project_id}")
    assert export.status_code == 200
    xlsx = export.content
    validation = validate_workbook_bytes(xlsx)
    assert validation["valid"] is True

    from openpyxl import load_workbook

    loaded = load_workbook(BytesIO(xlsx))
    assert SHEET_FASCICULOS in loaded.sheetnames
    assert SHEET_BLOCOS in loaded.sheetnames
    for spec in mapping_document()["sheets"]:
        if spec["name"] in DATA_SHEETS:
            assert spec["name"] in loaded.sheetnames


def test_workbook_export_roundtrip_add_fascicle(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    data = _minimal_workbook_bytes()
    dry = client.post(
        "/api/workbook/migrate",
        data={"dry_run": "true"},
        files={"file": ("seed.xlsx", data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    project_id = client.post(
        "/api/workbook/migrate/apply",
        json={
            "run_id": dry.json()["run_id"],
            "confirm": "I_UNDERSTAND",
            "target": "new_project",
        },
    ).json()["project_id"]

    from openpyxl import load_workbook

    xlsx = client.get(f"/api/workbook/export/project/{project_id}").content
    wb = load_workbook(BytesIO(xlsx))
    sheet = wb[SHEET_FASCICULOS]
    row = 5
    while sheet.cell(row=row, column=1).value:
        row += 1
    sheet.cell(row=row, column=1, value="F99")
    sheet.cell(row=row, column=2, value="Fascículo exportado")
    sheet.cell(row=row, column=3, value="Projeto")
    buffer = BytesIO()
    wb.save(buffer)
    edited = buffer.getvalue()

    dry2 = client.post(
        "/api/workbook/migrate",
        data={"dry_run": "true", "project_id": project_id},
        files={"file": ("edited.xlsx", edited, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert dry2.status_code == 200
    assert dry2.json()["status"] == "ready"
    run_id = dry2.json()["run_id"]

    result = client.post(
        "/api/workbook/migrate/apply",
        json={
            "run_id": run_id,
            "confirm": "I_UNDERSTAND",
            "target": "existing_project",
            "project_id": project_id,
        },
    )
    assert result.status_code == 200
    assert result.json()["summary"]["fascicles_added"] == 1


def test_workbook_export_append_only_warning_on_edit(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    data = _minimal_workbook_bytes()
    dry = client.post(
        "/api/workbook/migrate",
        data={"dry_run": "true"},
        files={"file": ("seed.xlsx", data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    project_id = client.post(
        "/api/workbook/migrate/apply",
        json={
            "run_id": dry.json()["run_id"],
            "confirm": "I_UNDERSTAND",
            "target": "new_project",
        },
    ).json()["project_id"]

    from openpyxl import load_workbook

    xlsx = client.get(f"/api/workbook/export/project/{project_id}").content
    wb = load_workbook(BytesIO(xlsx))
    sheet = wb[SHEET_FASCICULOS]
    sheet.cell(row=5, column=2, value="Título alterado no Excel")
    buffer = BytesIO()
    wb.save(buffer)

    dry2 = client.post(
        "/api/workbook/migrate",
        data={"dry_run": "true", "project_id": project_id},
        files={
            "file": (
                "edited.xlsx",
                buffer.getvalue(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    issues = dry2.json().get("issues") or []
    msgs = " ".join(i.get("message", "") for i in issues)
    assert "append-only" in msgs.lower() or "não actualiza" in msgs.lower()


def test_workbook_export_library(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    client.post(
        "/api/references",
        json={"scope_type": "library", "title": "Norma teste E08", "citation": "uso geral"},
    )
    export = client.get("/api/workbook/export/library")
    assert export.status_code == 200
    assert validate_workbook_bytes(export.content)["valid"] is True