from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.deps import get_settings
from app.main import app
from app.services.project_service import ensure_template_version
from app.services.workspace_service import workspace_session


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    cfg = tmp_path / "app-config.json"
    monkeypatch.setenv("GET_APP_CONFIG_PATH", str(cfg))
    get_settings.cache_clear()
    return TestClient(app)


def _workspace(client: TestClient, tmp_path: Path) -> None:
    response = client.post(
        "/api/workspace/create",
        json={"root_path": str(tmp_path / "workspace"), "local_user_name": "tester"},
    )
    assert response.status_code == 200


def _ensure_library(client: TestClient) -> None:
    client.post(
        "/api/knowledge",
        json={
            "title": "Semente biblioteca",
            "content": "conteúdo",
            "origin_context": "teste",
        },
    )


def _template_v1(client: TestClient) -> str:
    templates = client.get("/api/projects/templates")
    assert templates.status_code == 200
    return templates.json()[0]["versions"][0]["id"]


def test_create_project_without_prior_knowledge_unit(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    v1_id = _template_v1(client)
    created = client.post(
        "/api/projects",
        json={
            "template_version_id": v1_id,
            "name": "Projeto sem unidade prévia",
            "intervention_type": "brownfield",
        },
    )
    assert created.status_code == 200
    assert created.json()["library_version"] == 1


def test_project_pins_library_and_keeps_template_version(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    _ensure_library(client)
    v1_id = _template_v1(client)
    created = client.post(
        "/api/projects",
        json={
            "template_version_id": v1_id,
            "name": "Projeto A",
            "intervention_type": "brownfield",
        },
    )
    assert created.status_code == 200
    body = created.json()
    assert body["template_version_id"] == v1_id
    assert body["template_version"] == 1
    assert body["library_version"] == 1

    with workspace_session(get_settings()) as (session, _paths):
        ensure_template_version(session, 2)

    later = client.get(f"/api/projects/{body['id']}")
    assert later.status_code == 200
    assert later.json()["template_version_id"] == v1_id
    assert later.json()["template_version"] == 1


def test_instance_parent_must_belong_to_same_project(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    _ensure_library(client)
    v1 = _template_v1(client)
    p1 = client.post(
        "/api/projects",
        json={"template_version_id": v1, "name": "P1", "intervention_type": "brownfield"},
    ).json()
    p2 = client.post(
        "/api/projects",
        json={"template_version_id": v1, "name": "P2", "intervention_type": "brownfield"},
    ).json()
    root = client.post(
        f"/api/projects/{p1['id']}/instances",
        json={"kind": "system", "name": "Sistema 1"},
    ).json()
    other_root = client.post(
        f"/api/projects/{p2['id']}/instances",
        json={"kind": "system", "name": "Sistema 2"},
    ).json()
    denied = client.post(
        f"/api/projects/{p1['id']}/instances",
        json={"kind": "equipment", "name": "Filho inválido", "parent_id": other_root["id"]},
    )
    assert denied.status_code == 400
    allowed = client.post(
        f"/api/projects/{p1['id']}/instances",
        json={"kind": "equipment", "name": "Filho válido", "parent_id": root["id"]},
    )
    assert allowed.status_code == 200
    assert allowed.json()["parent_id"] == root["id"]
    assert allowed.json()["depth"] == 1


def test_project_knowledge_isolated_from_library(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    _ensure_library(client)
    v1 = _template_v1(client)
    project = client.post(
        "/api/projects",
        json={"template_version_id": v1, "name": "P-K", "intervention_type": "brownfield"},
    ).json()
    client.post(
        "/api/knowledge",
        json={
            "title": "Biblioteca isolada",
            "content": "só biblioteca",
            "origin_context": "teste",
        },
    )
    client.post(
        "/api/knowledge",
        json={
            "title": "Unidade de projeto",
            "content": "só projeto",
            "origin_context": "teste",
            "scope_type": "project",
            "scope_id": project["id"],
        },
    )
    library = client.get("/api/knowledge", params={"scope_type": "library"})
    project_items = client.get(
        "/api/knowledge",
        params={"scope_type": "project", "scope_id": project["id"]},
    )
    assert library.status_code == 200
    assert project_items.status_code == 200
    library_titles = {item["title"] for item in library.json()}
    project_titles = {item["title"] for item in project_items.json()}
    assert "Unidade de projeto" in project_titles
    assert "Unidade de projeto" not in library_titles
    assert project_items.json()[0]["scope_type"] == "project"


def test_project_summary_read_only(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    _ensure_library(client)
    v1_id = _template_v1(client)
    project = client.post(
        "/api/projects",
        json={
            "template_version_id": v1_id,
            "name": "Resumo",
            "intervention_type": "brownfield",
        },
    ).json()
    summary = client.get("/api/projects/" + project["id"] + "/summary")
    assert summary.status_code == 200
    body = summary.json()
    assert body["project_id"] == project["id"]
    assert isinstance(body["point_status_counts"], dict)
    assert body["imports_staged"] == 0
    assert body["merge_sessions_open"] == 0


def test_f0_preflight_script_reports_missing_fascicle(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    _ensure_library(client)
    v1_id = _template_v1(client)
    project = client.post(
        "/api/projects",
        json={
            "template_version_id": v1_id,
            "name": "Preflight",
            "intervention_type": "brownfield",
        },
    ).json()
    cfg = tmp_path / "app-config.json"
    env = {**os.environ, "GET_APP_CONFIG_PATH": str(cfg)}
    backend = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        [
            sys.executable,
            str(backend / "scripts" / "f0_pilot_preflight.py"),
            "--project-id",
            project["id"],
            "--fascicle",
            "F99",
        ],
        cwd=backend,
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert "F99" in proc.stderr or "F99" in proc.stdout


def test_f1_block_preflight_reports_missing_block(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    _ensure_library(client)
    v1_id = _template_v1(client)
    project = client.post(
        "/api/projects",
        json={
            "template_version_id": v1_id,
            "name": "F1 preflight",
            "intervention_type": "brownfield",
        },
    ).json()
    cfg = tmp_path / "app-config.json"
    env = {**os.environ, "GET_APP_CONFIG_PATH": str(cfg)}
    backend = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        [
            sys.executable,
            str(backend / "scripts" / "f1_block_preflight.py"),
            "--project-id",
            project["id"],
            "--block",
            "F99_B99",
        ],
        cwd=backend,
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert "F99_B99" in proc.stderr or "F99_B99" in proc.stdout


def test_f1_patch_block_point_missing_title(client: TestClient, tmp_path: Path) -> None:
    from tests.integration.test_get_package import _setup_block

    pid, block_id, _ = _setup_block(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "block", "node_id": block_id},
    )
    assert export.status_code == 200
    pkg_path = Path(export.json()["file_path"])
    cfg = tmp_path / "app-config.json"
    env = {**os.environ, "GET_APP_CONFIG_PATH": str(cfg)}
    backend = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        [
            sys.executable,
            str(backend / "scripts" / "f1_patch_block_point.py"),
            str(pkg_path),
            "--project-id",
            pid,
            "--title-contains",
            "inexistente_xyz",
            "--append-guidance",
            "x",
        ],
        cwd=backend,
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0


def test_f1_ready_check_runs_on_block(client: TestClient, tmp_path: Path) -> None:
    from tests.integration.test_get_package import _setup_block

    pid, block_id, _ = _setup_block(client, tmp_path)
    cfg = tmp_path / "app-config.json"
    env = {**os.environ, "GET_APP_CONFIG_PATH": str(cfg)}
    backend = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        [
            sys.executable,
            str(backend / "scripts" / "f1_ready_check.py"),
            "--project-id",
            pid,
            "--block",
            "F01_B01",
            "--json",
        ],
        cwd=backend,
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert "point_count" in proc.stdout


def test_f1_patch_block_point_patches_file(client: TestClient, tmp_path: Path) -> None:
    import json

    from tests.integration.test_get_package import _setup_block

    pid, block_id, _ = _setup_block(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "block", "node_id": block_id},
    )
    assert export.status_code == 200
    pkg_path = Path(export.json()["file_path"])
    patches = [
        {
            "title_contains": "Ponto",
            "append_guidance": "Linha de orientação de teste.",
        }
    ]
    patch_file = tmp_path / "patches.json"
    patch_file.write_text(json.dumps(patches), encoding="utf-8")
    out = tmp_path / "patched.json"
    cfg = tmp_path / "app-config.json"
    env = {**os.environ, "GET_APP_CONFIG_PATH": str(cfg)}
    backend = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        [
            sys.executable,
            str(backend / "scripts" / "f1_patch_block_point.py"),
            str(pkg_path),
            "--project-id",
            pid,
            "--patches",
            str(patch_file),
            "--out",
            str(out),
        ],
        cwd=backend,
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    assert out.is_file()


def test_f2_m2_preflight_reports_block(client: TestClient, tmp_path: Path) -> None:
    from tests.integration.test_get_package import _setup_block

    pid, block_id, _ = _setup_block(client, tmp_path)
    cfg = tmp_path / "app-config.json"
    env = {**os.environ, "GET_APP_CONFIG_PATH": str(cfg)}
    backend = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        [
            sys.executable,
            str(backend / "scripts" / "f2_m2_preflight.py"),
            "--project-id",
            pid,
            "--block",
            "F01_B01",
            "--json",
        ],
        cwd=backend,
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert "exportable_points" in proc.stdout