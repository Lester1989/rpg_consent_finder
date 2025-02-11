import logging
from nicegui import ui, app

from components.consent_entry_component import (
    CategoryEntryComponent,
)
from components.consent_display_component import ConsentDisplayComponent
from components.sheet_display_component import SheetDisplayComponent
from models.db_models import (
    ConsentEntry,
    ConsentSheet,
    ConsentStatus,
    ConsentTemplate,
    RPGGroup,
)
from models.controller import (
    get_all_consent_topics,
    get_group_by_name_id,
    get_consent_sheet_by_id,
)


@ui.refreshable
def content(share_id: str, sheet_id: str, **kwargs):
    if not share_id:
        ui.label("No share_id provided")
        return
    sheet = get_consent_sheet_by_id(int(sheet_id))
    logging.debug(sheet)
    logging.debug(sheet.public_share_id, share_id)
    if not sheet or sheet.public_share_id != share_id:
        ui.label("No sheet found")
        return
    ui.label("Consent Levels").classes("text-2xl mx-auto")
    with ui.grid().classes("lg:grid-cols-5 grid-cols-2 gap-2 lg:w-5/6 w-full mx-auto"):
        for preference in ConsentStatus:
            with ui.column().classes(
                "p-2 rounded-lg shadow-sm shadow-white gap-1 items-center"
            ):
                ui.label(preference.as_emoji + preference.name.capitalize()).classes(
                    "text-xs text-gray-500 text-center"
                )
                ui.markdown(preference.explanation_de)
    ui.separator()
    SheetDisplayComponent(sheet)

    ui.link("Sign Up/in", "/welcome").classes(
        "text-lg lg:text-xl text-white hover:text-gray-300 no-underline bg-green-600 p-1 lg:p-2 rounded"
    )
