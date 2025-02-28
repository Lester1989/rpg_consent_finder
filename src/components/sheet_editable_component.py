import logging

from nicegui import app, ui

from components.consent_entry_component import (
    CategoryEntryComponent,
    ConsentEntryComponent,
)
from components.custom_consent_entry_component import CustomConsentEntryComponent
from controller.sheet_controller import (
    create_share_id,
    get_all_consent_topics,
    get_consent_sheet_by_id,
    update_consent_sheet,
    update_custom_entry,
)
from controller.user_controller import get_user_from_storage
from controller.util_controller import (
    get_all_localized_texts,
)
from localization.language_manager import make_localisable
from models.db_models import (
    ConsentSheet,
    ConsentStatus,
    ConsentTemplate,
    CustomConsentEntry,
)


class SheetEditableComponent(ui.grid):
    sheet: ConsentSheet
    topics: list[ConsentTemplate]
    categories: list[str]
    grouped_topics: dict[str, list[ConsentTemplate]]
    lang: str
    share_button: ui.button

    def __init__(self, consent_sheet: ConsentSheet, lang: str = "en"):
        super().__init__()
        self.sheet = consent_sheet

        self.sheet.custom_consent_entries = [
            cce for cce in self.sheet.custom_consent_entries if cce.content != ""
        ]
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
        self.user = get_user_from_storage()
        self.content()

    def unshare(self):
        self.sheet.public_share_id = None
        update_consent_sheet(self.user, self.sheet)
        ui.navigate.to(f"/consentsheet/{self.sheet.id}?show=edit&lang={self.lang}")

    def share(self):
        self.sheet.public_share_id = create_share_id()
        update_consent_sheet(self.user, self.sheet)
        ui.navigate.to(f"/consentsheet/{self.sheet.id}?show=edit&lang={self.lang}")

    @ui.refreshable
    def content(self):
        self.clear()
        with self.classes("lg:grid-cols-3 grid-cols-1"):
            make_localisable(
                ui.input("Sheet Name")
                .bind_value(self.sheet, "human_name")
                .on("focusout", lambda _: update_consent_sheet(self.user, self.sheet)),
                key="sheet_name",
                language=self.lang,
            )
            make_localisable(
                ui.input("Comment")
                .bind_value(self.sheet, "comment")
                .on("focusout", lambda _: update_consent_sheet(self.user, self.sheet)),
                key="sheet_comment",
                language=self.lang,
            )
            if self.sheet.public_share_id:
                self.share_button = ui.button("Unshare").on_click(self.unshare)
                make_localisable(
                    self.share_button,
                    key="unshare",
                    language=self.lang,
                )
            else:
                self.share_button = ui.button("Share").on_click(self.share)
                make_localisable(
                    self.share_button,
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
            with ui.card().classes(
                f"row-span-{(len(self.sheet.custom_consent_entries) // 2) + 1}"
            ):
                empty_entries = 0
                for custom_entry in self.sheet.custom_consent_entries:
                    if custom_entry.content == "":
                        empty_entries += 1
                        if empty_entries > 1:
                            continue
                    CustomConsentEntryComponent(custom_entry, lang=self.lang)
                add_button = ui.button("Add Entry", on_click=self.add_custom_entry)
                add_button.bind_enabled_from(
                    self.sheet,
                    "custom_consent_entries",
                    backward=lambda custom_consent_entries: len(
                        [
                            entry
                            for entry in custom_consent_entries
                            if entry.content == ""
                        ]
                    )
                    < 2,
                )
                make_localisable(
                    add_button,
                    key="add_entry",
                    language=self.lang,
                )
                make_localisable(
                    ui.label("empty_custom_entries_will_be_deleted").classes(
                        "text-sm text-gray-500"
                    ),
                    key="empty_custom_entries_will_be_deleted",
                    language=self.lang,
                )

    def add_custom_entry(self):
        new_entry = CustomConsentEntry(
            consent_sheet_id=self.sheet.id,
            consent_sheet=self.sheet,
            content="",
            preference=ConsentStatus.unknown,
            comment="",
        )
        update_custom_entry(new_entry)
        self.sheet = get_consent_sheet_by_id(
            app.storage.user.get("user_id"), self.sheet.id
        )
        self.content.refresh()
