from nicegui import app, ui

from components.consent_legend_component import consent_legend_component
from components.preference_ordered_sheet_display_component import (
    PreferenceOrderedSheetDisplayComponent,
)
from controller.sheet_controller import (
    get_consent_sheet_by_id,
)
from controller.user_controller import get_user_by_id_name
from localization.language_manager import make_localisable
from models.db_models import User


def content(share_id: str, sheet_id: str, lang: str = "en", **kwargs):
    if not share_id:
        make_localisable(ui.label(), key="no_share_id", language=lang)
        return
    sheet = get_consent_sheet_by_id(app.storage.user.get("user_id"), int(sheet_id))
    if not sheet or sheet.public_share_id != share_id:
        make_localisable(ui.label(), key="no_sheet", language=lang)
        return
    PreferenceOrderedSheetDisplayComponent(sheet, lang=lang, redact_name=True)
    ui.separator().mark("public_sheet_separator")
    consent_legend_component(lang)
    try:
        user: User = get_user_by_id_name(app.storage.user.get("user_id"))
    except Exception:
        user = None
    if not user:
        ui.link("Sign Up/in", f"/welcome?lang={lang}").classes(
            "text-lg lg:text-xl text-white hover:text-gray-300 no-underline bg-green-600 p-1 lg:p-2 rounded"
        )
