import logging

from nicegui import ui

from a_logger_setup import LOGGER_NAME

from components.consent_legend_component import consent_legend_component
from components.preference_ordered_sheet_display_component import (
    PreferenceOrderedSheetDisplayComponent,
)
from controller.sheet_controller import (
    get_consent_sheet_by_id,
    get_consent_sheet_by_share_id,
)
from controller.user_controller import get_user_by_id_name
from localization.language_manager import make_localisable
from models.db_models import User
from services.session_service import get_current_user_id


logger = logging.getLogger(LOGGER_NAME)


def content(share_id: str, sheet_id: str, **kwargs):
    logger.debug("public_sheet content %s %s", share_id, sheet_id)
    if not share_id:
        make_localisable(ui.label(), key="no_share_id")
        return
    user_id = get_current_user_id()
    sheet = (
        get_consent_sheet_by_id(user_id, int(sheet_id))
        if user_id
        else get_consent_sheet_by_share_id(share_id, int(sheet_id))
    )
    if not sheet or sheet.public_share_id != share_id:
        logger.debug("No sheet found or share_id mismatch: %s %s", sheet, share_id)
        make_localisable(ui.label(), key="no_sheet")
        return
    PreferenceOrderedSheetDisplayComponent(sheet, redact_name=True)
    ui.separator().mark("public_sheet_separator")
    consent_legend_component()
    try:
        user: User = get_user_by_id_name(user_id) if user_id else None
    except Exception:
        user = None
    if not user:
        ui.link("Sign Up/in", "/welcome").classes(
            "text-lg lg:text-xl text-white hover:text-gray-300 no-underline bg-green-600 p-1 lg:p-2 rounded"
        )
