from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="GET_",
        env_file=".env",
        extra="ignore",
    )

    host: str = "127.0.0.1"
    port: int = 4810
    workspace_root: Path | None = Field(
        default=None,
        description="Raiz do workspace (dados). Se definido, sobrepõe workspace_root em app-config.json.",
    )
    app_config_path: Path = Field(
        default_factory=lambda: Path.home() / ".get" / "app-config.json"
    )
    ui_preferences_path: Path = Field(
        default_factory=lambda: Path.home() / ".get" / "ui-preferences.json"
    )


def load_app_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_app_config(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def get_active_workspace_root(settings: AppSettings) -> Path | None:
    if settings.workspace_root is not None:
        root = settings.workspace_root.expanduser().resolve()
        if not root.is_dir():
            raise ValueError(
                f"GET_WORKSPACE_ROOT não é um directório válido: {root}"
            )
        return root
    data = load_app_config(settings.app_config_path)
    root = data.get("workspace_root")
    if not root:
        return None
    return Path(root).resolve()


def set_active_workspace_root(settings: AppSettings, root: Path) -> None:
    data = load_app_config(settings.app_config_path)
    data["workspace_root"] = str(root.resolve())
    save_app_config(settings.app_config_path, data)