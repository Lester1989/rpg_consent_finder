import logging
from nicegui import ui, app

from components.consent_entry_component import (
    CategoryEntryComponent,
)
from components.consent_display_component import ConsentDisplayComponent
from models.models import (
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
    topics: list[ConsentTemplate] = get_all_consent_topics()
    categories = sorted(list(set(topic.category for topic in topics)))
    grouped_topics = {
        category: [template for template in topics if template.category == category]
        for category in categories
    }
    sheet = get_consent_sheet_by_id(int(sheet_id))
    logging.debug(sheet)
    logging.debug(sheet.public_share_id, share_id)
    if not sheet or sheet.public_share_id != share_id:
        ui.label("No sheet found")
        return
    with ui.grid(columns=3):
        for category in categories:
            templates = grouped_topics[category]
            lookup_consents = {
                template.id: next(
                    (
                        consent_entry
                        for consent_entry in sheet.consent_entries
                        if consent_entry.consent_template_id == template.id
                    ),
                    None,
                )
                for template in templates
            }
            with ui.card().classes(f"row-span-{(len(templates) // 3) + 1} "):
                with ui.row().classes("w-full pt-6"):
                    ui.label(category).classes("text-xl")
                    for topic in templates:
                        ConsentDisplayComponent(lookup_consents[topic.id], [])
