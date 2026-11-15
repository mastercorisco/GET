from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.config import AppSettings
from app.schemas.ui_preferences import (
    DEFAULT_UI_PREFERENCES,
    UiPreferencesPatch,
    UiPreferencesResponse,
)


def _prefs_path(settings: AppSettings) -> Path:
    return settings.ui_preferences_path


def _read_raw(path: Path) -> dict[str, Any]:
    if not path.exists():
        return dict(DEFAULT_UI_PREFERENCES)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return dict(DEFAULT_UI_PREFERENCES)
    merged = dict(DEFAULT_UI_PREFERENCES)
    merged.update({k: v for k, v in data.items() if k in DEFAULT_UI_PREFERENCES})
    return merged


def _write_raw(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def get_ui_preferences(settings: AppSettings) -> UiPreferencesResponse:
    raw = _read_raw(_prefs_path(settings))
    return UiPreferencesResponse.model_validate(raw)


def patch_ui_preferences(settings: AppSettings, body: UiPreferencesPatch) -> UiPreferencesResponse:
    path = _prefs_path(settings)
    if body.reset_defaults:
        raw = dict(DEFAULT_UI_PREFERENCES)
    else:
        raw = _read_raw(path)
        patch = body.model_dump(exclude_none=True, exclude={"reset_defaults"})
        raw.update(patch)
    _write_raw(path, raw)
    return UiPreferencesResponse.model_validate(raw)