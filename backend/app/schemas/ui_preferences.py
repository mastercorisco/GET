from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

UiTheme = Literal["light", "dark", "system"]
UiAccent = Literal["blue", "teal", "slate", "high_contrast"]
UiFont = Literal["system", "segoe", "atkinson", "source_sans"]
UiDensity = Literal["compact", "normal", "comfortable"]
UiContentWidth = Literal["narrow", "normal", "wide"]

DEFAULT_UI_PREFERENCES: dict[str, str] = {
    "schema_version": "1.0",
    "theme": "light",
    "accent": "blue",
    "font": "system",
    "density": "normal",
    "content_width": "normal",
}


class UiPreferencesResponse(BaseModel):
    schema_version: str = "1.0"
    theme: UiTheme = "light"
    accent: UiAccent = "blue"
    font: UiFont = "system"
    density: UiDensity = "normal"
    content_width: UiContentWidth = "normal"


class UiPreferencesPatch(BaseModel):
    theme: UiTheme | None = None
    accent: UiAccent | None = None
    font: UiFont | None = None
    density: UiDensity | None = None
    content_width: UiContentWidth | None = None
    reset_defaults: bool = Field(default=False, description="Restaura valores de fábrica")