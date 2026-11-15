from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.deps import get_settings
from app.main import app


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    cfg = tmp_path / "app-config.json"
    monkeypatch.setenv("GET_APP_CONFIG_PATH", str(cfg))
    get_settings.cache_clear()
    return TestClient(app)


def _workspace(client: TestClient, tmp_path: Path) -> None:
    assert client.post(
        "/api/workspace/create",
        json={"root_path": str(tmp_path / "workspace"), "local_user_name": "tester"},
    ).status_code == 200


def test_reference_and_standard_profile(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    client.post(
        "/api/knowledge",
        json={"title": "s", "content": "c", "origin_context": "t"},
    )
    ref = client.post(
        "/api/references",
        json={"scope_type": "library", "title": "IEC 61000", "citation": "IEC"},
    )
    assert ref.status_code == 200
    ref_id = ref.json()["id"]

    std = client.put(
        f"/api/references/{ref_id}/standard-profile",
        json={"contractual_role": "design_basis", "code": "IEC 61000"},
    )
    assert std.status_code == 200
    assert std.json()["standard_profile"]["contractual_role"] == "design_basis"

    bad = client.put(
        f"/api/references/{ref_id}/standard-profile",
        json={"contractual_role": "invalid_role"},
    )
    assert bad.status_code in (400, 422)