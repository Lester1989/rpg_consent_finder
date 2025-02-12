import logging
from nicegui import ui

from components.consent_entry_component import (
    CategoryEntryComponent,
    ConsentEntryComponent,
)
from localization.language_manager import make_localisable
from models.db_models import (
    ConsentTemplate,
    ConsentSheet,
)
from models.controller import (
    create_share_id,
    get_all_consent_topics,
    get_all_localized_texts,
    update_consent_sheet,
)


class SheetEditableComponent(ui.grid):
    sheet: ConsentSheet
    topics: list[ConsentTemplate]
    categories: list[str]
    grouped_topics: dict[str, list[ConsentTemplate]]
    lang: str

    def __init__(self, consent_sheet: ConsentSheet, lang: str = "en"):
        super().__init__()
        self.sheet = consent_sheet
        logging.debug(self.sheet)
        self.lang = lang
        self.text_lookup = get_all_localized_texts()
        self.topics: list[ConsentTemplate] = get_all_consent_topics()
        self.categories = sorted(list({topic.category_id for topic in self.topics}))
        self.grouped_topics = {
            category_id: [
                template
                for template in self.topics
                if template.category_id == category_id
            ]
            for category_id in self.categories
        }
        self.content()

    def unshare(self):
        self.sheet.public_share_id = None
        update_consent_sheet(self.sheet)
        ui.navigate.to(f"/consentsheet/{self.sheet.id}?show=edit&lang={self.lang}")

    def share(self):
        self.sheet.public_share_id = create_share_id()
        update_consent_sheet(self.sheet)
        ui.navigate.to(f"/consentsheet/{self.sheet.id}?show=edit&lang={self.lang}")

    @ui.refreshable
    def content(self):
        self.clear()
        with self.classes("lg:grid-cols-3 grid-cols-1"):
            make_localisable(
                ui.input("Sheet Name")
                .bind_value(self.sheet, "human_name")
                .on("focusout", lambda _: update_consent_sheet(self.sheet)),
                key="sheet_name",
                language=self.lang,
            )
            make_localisable(
                ui.input("Comment")
                .bind_value(self.sheet, "comment")
                .on("focusout", lambda _: update_consent_sheet(self.sheet)),
                key="sheet_comment",
                language=self.lang,
            )
            if self.sheet.public_share_id:
                make_localisable(
                    ui.button("Unshare").on_click(self.unshare),
                    key="unshare",
                    language=self.lang,
                )
            else:
                make_localisable(
                    ui.button("Share").on_click(self.share),
                    key="share",
                    language=self.lang,
                )
            for category_id in self.categories:
                templates = self.grouped_topics[category_id]
                with ui.card().classes(f"row-span-{(len(templates) // 2) + 1} "):
                    with ui.row().classes("w-full pt-0"):
                        category_component = CategoryEntryComponent(
                            category=self.text_lookup[category_id].get_text(self.lang),
                        )
                        category_component.topics = [
                            ConsentEntryComponent(
                                self.sheet.get_entry(topic.id),
                                lang=self.lang,
                            )
                            for topic in templates
                        ]
