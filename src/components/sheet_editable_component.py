import logging
from nicegui import ui

from components.consent_entry_component import (
    CategoryEntryComponent,
    ConsentEntryComponent,
)
from models.db_models import (
    ConsentStatus,
    ConsentTemplate,
    ConsentEntry,
    ConsentSheet,
)
from models.controller import (
    create_share_id,
    get_all_consent_topics,
    update_consent_sheet,
    update_entry,
)


class SheetEditableComponent(ui.grid):
    sheet: ConsentSheet
    topics: list[ConsentTemplate]
    categories: list[str]
    grouped_topics: dict[str, list[ConsentTemplate]]

    def __init__(self, consent_sheet: ConsentSheet):
        super().__init__(columns=3)
        self.sheet = consent_sheet
        logging.debug(self.sheet)
        self.topics: list[ConsentTemplate] = get_all_consent_topics()
        self.categories = sorted(list(set(topic.category for topic in self.topics)))
        self.grouped_topics = {
            category: [
                template for template in self.topics if template.category == category
            ]
            for category in self.categories
        }
        self.content()

    def unshare(self):
        self.sheet.public_share_id = None
        update_consent_sheet(self.sheet)
        ui.navigate.to(f"/consentsheet/{self.sheet.id}?show=edit")

    def share(self):
        self.sheet.public_share_id = create_share_id()
        update_consent_sheet(self.sheet)
        ui.navigate.to(f"/consentsheet/{self.sheet.id}?show=edit")

    @ui.refreshable
    def content(self):
        self.clear()
        with self:
            ui.input("Sheet Name").bind_value(self.sheet, "human_name").on(
                "focusout", lambda _: update_consent_sheet(self.sheet)
            )
            ui.input("Comment").bind_value(self.sheet, "comment").on(
                "focusout", lambda _: update_consent_sheet(self.sheet)
            )
            if self.sheet.public_share_id:
                ui.button("Unshare").on_click(self.unshare)
            else:
                ui.button("Share").on_click(self.share)
            for category in self.categories:
                templates = self.grouped_topics[category]
                with ui.card().classes(f"row-span-{(len(templates) // 2) + 1} "):
                    with ui.row().classes("w-full pt-0"):
                        category_component = CategoryEntryComponent(
                            category=category,
                        )
                        category_component.topics = [
                            ConsentEntryComponent(
                                self.sheet.get_entry(topic.id),
                            )
                            for topic in templates
                        ]
