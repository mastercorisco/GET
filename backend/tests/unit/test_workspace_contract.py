from __future__ import annotations

from pathlib import Path

import pytest

from app.config import AppSettings, get_active_workspace_root
from app.deps import get_settings
from app.services.workspace_exclusivity import WorkspaceExclusiveError, workspace_exclusive


def test_get_workspace_root_env_overrides_app_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_root = tmp_path / "from-env"
    env_root.mkdir()
    other = tmp_path / "from-config"
    other.mkdir()
    cfg = tmp_path / "app-config.json"
    cfg.write_text(f'{{"workspace_root": "{other.as_posix()}"}}', encoding="utf-8")
    monkeypatch.setenv("GET_APP_CONFIG_PATH", str(cfg))
    monkeypatch.setenv("GET_WORKSPACE_ROOT", str(env_root))
    get_settings.cache_clear()
    settings = get_settings()
    assert get_active_workspace_root(settings) == env_root.resolve()


def test_workspace_exclusive_rejects_nested() -> None:
    with workspace_exclusive("outer"):
        with pytest.raises(WorkspaceExclusiveError):
            with workspace_exclusive("inner"):
                pass


def test_invalid_workspace_root_env_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = tmp_path / "app-config.json"
    cfg.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("GET_APP_CONFIG_PATH", str(cfg))
    monkeypatch.setenv("GET_WORKSPACE_ROOT", str(tmp_path / "missing-dir"))
    get_settings.cache_clear()
    settings = AppSettings()
    with pytest.raises(ValueError, match="GET_WORKSPACE_ROOT"):
        get_active_workspace_root(settings)