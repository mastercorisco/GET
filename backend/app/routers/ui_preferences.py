from fastapi import APIRouter

from app.deps import get_settings
from app.schemas.ui_preferences import UiPreferencesPatch, UiPreferencesResponse
from app.services import ui_preferences as ui_prefs_service

router = APIRouter(prefix="/ui-preferences", tags=["ui-preferences"])


@router.get("", response_model=UiPreferencesResponse)
def ui_preferences_get() -> UiPreferencesResponse:
    return ui_prefs_service.get_ui_preferences(get_settings())


@router.patch("", response_model=UiPreferencesResponse)
def ui_preferences_patch(body: UiPreferencesPatch) -> UiPreferencesResponse:
    return ui_prefs_service.patch_ui_preferences(get_settings(), body)