import logging
from nicegui import ui

from components.consent_display_component import ConsentDisplayComponent
from components.consent_entry_component import (
    CategoryEntryComponent,
    ConsentEntryComponent,
)
from models.models import (
    ConsentStatus,
    ConsentTemplate,
    ConsentEntry,
    ConsentSheet,
)
from models.controller import get_all_consent_topics, update_entry, update_consent_sheet


class SheetDisplayComponent(ui.grid):
    sheet: ConsentSheet = None
    sheets: list[ConsentSheet] = None

    def __init__(
        self,
        consent_sheet: ConsentSheet = None,
        consent_sheets: list[ConsentSheet] = None,
    ):
        super().__init__(columns=3)
        if consent_sheet is None:
            self.sheets = consent_sheets
        else:
            self.sheet = consent_sheet

        self.topics: list[ConsentTemplate] = get_all_consent_topics()
        self.categories = sorted(list(set(topic.category for topic in self.topics)))
        self.grouped_topics = {
            category: [
                template for template in self.topics if template.category == category
            ]
            for category in self.categories
        }
        self.content()

    @property
    def sheet_name(self):
        return (
            self.sheet.human_name
            if self.sheet
            else f"Consent of {len(self.sheets)} players"
        )

    @property
    def sheet_comments(self):
        return (
            self.sheet.comment
            if self.sheet
            else "\n---\n".join(sheet.comment for sheet in self.sheets if sheet.comment)
        )

    @ui.refreshable
    def content(self):
        logging.debug(f"SheetDisplayComponent {self.sheet} {self.sheets}")
        self.clear()
        with self:
            ui.label(self.sheet_name)
            ui.label(self.sheet_comments)
            if self.sheet and self.sheet.public_share_id:
                ui.link(
                    "Link to this sheet",
                    f"/consent/{self.sheet.public_share_id}/{self.sheet.id}",
                )
            else:
                ui.label("")

            for category in self.categories:
                templates = self.grouped_topics[category]
                lookup_consents = {
                    template.id: [
                        sheet.consent_entries_dict.get(template.id)
                        for sheet in self.sheets or [self.sheet]
                    ]
                    for template in templates
                }
                with ui.card().classes(f"row-span-{(len(templates) // 3) + 1} "):
                    with ui.row().classes("w-full pt-6"):
                        ui.label(category).classes("text-xl")
                        for topic in templates:
                            ConsentDisplayComponent(lookup_consents[topic.id])
