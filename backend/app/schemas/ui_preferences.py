from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator

UiTheme = Literal["light", "dark", "system"]
UiAccent = Literal["blue", "teal", "slate", "high_contrast", "purple", "amber", "rose", "custom"]
UiFont = Literal["system", "segoe", "atkinson", "source_sans", "georgia", "monospace", "custom"]
UiDensity = Literal["compact", "normal", "comfortable", "custom"]
UiContentWidth = Literal["narrow", "normal", "wide", "xlarge", "custom"]

_HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")

DEFAULT_UI_PREFERENCES: dict[str, str | int | float] = {
    "schema_version": "1.1",
    "theme": "light",
    "accent": "blue",
    "accent_color": "#1d4ed8",
    "font": "system",
    "font_family_custom": "",
    "density": "normal",
    "control_font_size_rem": 1.0,
    "control_padding_block_rem": 0.55,
    "control_padding_inline_rem": 0.65,
    "textarea_min_height_rem": 5.0,
    "content_width": "normal",
    "content_max_px": 1200,
    "ui_scale_percent": 100,
}


class UiPreferencesResponse(BaseModel):
    schema_version: str = "1.1"
    theme: UiTheme = "light"
    accent: UiAccent = "blue"
    accent_color: str = "#1d4ed8"
    font: UiFont = "system"
    font_family_custom: str = ""
    density: UiDensity = "normal"
    control_font_size_rem: float = Field(default=1.0, ge=0.65, le=1.5)
    control_padding_block_rem: float = Field(default=0.55, ge=0.2, le=1.2)
    control_padding_inline_rem: float = Field(default=0.65, ge=0.2, le=1.5)
    textarea_min_height_rem: float = Field(default=5.0, ge=2.0, le=14.0)
    content_width: UiContentWidth = "normal"
    content_max_px: int = Field(default=1200, ge=640, le=2000)
    ui_scale_percent: int = Field(default=100, ge=80, le=130)

    @field_validator("accent_color")
    @classmethod
    def validate_hex(cls, v: str) -> str:
        if not _HEX.match(v):
            raise ValueError("accent_color deve ser #RRGGBB")
        return v.lower()


class UiPreferencesPatch(BaseModel):
    theme: UiTheme | None = None
    accent: UiAccent | None = None
    accent_color: str | None = None
    font: UiFont | None = None
    font_family_custom: str | None = None
    density: UiDensity | None = None
    control_font_size_rem: float | None = Field(default=None, ge=0.65, le=1.5)
    control_padding_block_rem: float | None = Field(default=None, ge=0.2, le=1.2)
    control_padding_inline_rem: float | None = Field(default=None, ge=0.2, le=1.5)
    textarea_min_height_rem: float | None = Field(default=None, ge=2.0, le=14.0)
    content_width: UiContentWidth | None = None
    content_max_px: int | None = Field(default=None, ge=640, le=2000)
    ui_scale_percent: int | None = Field(default=None, ge=80, le=130)
    reset_defaults: bool = Field(default=False, description="Restaura valores de fábrica")

    @field_validator("accent_color")
    @classmethod
    def validate_hex_patch(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not _HEX.match(v):
            raise ValueError("accent_color deve ser #RRGGBB")
        return v.lower()