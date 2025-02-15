import logging
from nicegui import ui

from components.consent_legend_component import consent_legend_component
from components.sheet_display_component import SheetDisplayComponent
from models.controller import (
    get_consent_sheet_by_id,
)
from localization.language_manager import make_localisable


@ui.refreshable
def content(share_id: str, sheet_id: str, lang: str = "en", **kwargs):
    if not share_id:
        make_localisable(ui.label(), key="no_share_id", language=lang)
        return
    sheet = get_consent_sheet_by_id(int(sheet_id))
    if not sheet or sheet.public_share_id != share_id:
        make_localisable(ui.label(), key="no_sheet", language=lang)
        return
    logging.debug(sheet)
    logging.debug(sheet.public_share_id, share_id)
    consent_legend_component(lang)
    ui.separator()
    SheetDisplayComponent(sheet)

    ui.link("Sign Up/in", f"/welcome?lang={lang}").classes(
        "text-lg lg:text-xl text-white hover:text-gray-300 no-underline bg-green-600 p-1 lg:p-2 rounded"
    )
