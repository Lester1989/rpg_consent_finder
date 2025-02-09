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
    SheetDisplayComponent(sheet)
