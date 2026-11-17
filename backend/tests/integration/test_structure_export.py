from __future__ import annotations

import zipfile
from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    cfg = tmp_path / "app-config.json"
    monkeypatch.setenv("GET_APP_CONFIG_PATH", str(cfg))
    from app.deps import get_settings

    get_settings.cache_clear()
    return TestClient(app)


def _workspace(client: TestClient, tmp_path: Path) -> None:
    assert client.post(
        "/api/workspace/create",
        json={"root_path": str(tmp_path / "workspace"), "local_user_name": "tester"},
    ).status_code == 200


def _ensure_library(client: TestClient) -> None:
    client.post(
        "/api/knowledge",
        json={"title": "Semente", "content": "c", "origin_context": "t"},
    )


def _project_with_tree(client: TestClient) -> tuple[str, str, str]:
    _ensure_library(client)
    tpl = client.get("/api/projects/templates").json()[0]["versions"][0]["id"]
    project = client.post(
        "/api/projects",
        json={"template_version_id": tpl, "name": "Export structure", "intervention_type": "brownfield"},
    ).json()
    pid = project["id"]
    f1 = client.post(
        f"/api/projects/{pid}/document-nodes",
        json={"node_type": "fascicle", "title": "Fasc A", "parent_id": None},
    ).json()["node"]
    f2 = client.post(
        f"/api/projects/{pid}/document-nodes",
        json={"node_type": "fascicle", "title": "Fasc B", "parent_id": None},
    ).json()["node"]
    block = client.post(
        f"/api/projects/{pid}/document-nodes",
        json={"node_type": "block", "title": "Bloco 1", "parent_id": f1["id"]},
    ).json()["node"]
    client.patch(
        f"/api/blocks/{block['id']}",
        json={"objective": "Obj teste", "scope": "Âmbito teste"},
    )
    client.post(
        f"/api/blocks/{block['id']}/development-points",
        json={"title": "Ponto 1"},
    )
    return pid, f1["id"], block["id"]


def test_structure_export_markdown_full_project(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    pid, _f1, _block = _project_with_tree(client)
    res = client.post(
        f"/api/projects/{pid}/document-structure/export",
        json={
            "format": "markdown",
            "include_block_model": True,
            "point_detail": "summary",
        },
    )
    assert res.status_code == 200
    text = res.text
    assert "Fasc A" in text or "F01" in text
    assert "Obj teste" in text
    assert "Ponto 1" in text
    assert "Não reimportável" in text
    assert "Capítulo" in text
    assert "modelo_do_ponto=" in text


def test_structure_export_subtree_excludes_other_fascicle(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    pid, f1_id, _block = _project_with_tree(client)
    res = client.post(
        f"/api/projects/{pid}/document-structure/export",
        json={"format": "markdown", "root_node_id": f1_id, "point_detail": "none"},
    )
    assert res.status_code == 200
    assert "Fasc B" not in res.text


def test_pdf_point_markup_no_html_escape_or_status() -> None:
    from app.schemas.structure_export import PointSummarySnapshot
    from app.services.structure_export.render_pdf import _point_markup, _xml_escape

    p = PointSummarySnapshot(
        id="x",
        order=1,
        title="Central Termoelétrica",
        status="ready",
        llm_freedom="strict",
        premise_count=0,
        must_include_count=0,
        open_questions_count=0,
        acceptance_criteria_count=0,
    )
    markup = _point_markup(p)
    assert markup == "<b>1. Central Termoelétrica</b>"
    assert "ready" not in markup
    assert "&lt;b&gt;" not in markup
    assert _xml_escape("a<b>c") == "a&lt;b&gt;c"


def test_structure_export_pdf_and_xmind(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    pid, _, _ = _project_with_tree(client)
    pdf = client.post(
        f"/api/projects/{pid}/document-structure/export",
        json={"format": "pdf", "point_detail": "summary"},
    )
    assert pdf.status_code == 200
    assert pdf.content[:4] == b"%PDF"

    xm = client.post(
        f"/api/projects/{pid}/document-structure/export",
        json={"format": "xmind", "point_detail": "none"},
    )
    assert xm.status_code == 200
    zf = zipfile.ZipFile(BytesIO(xm.content))
    assert "content.json" in zf.namelist()