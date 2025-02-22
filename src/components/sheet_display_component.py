import logging
from nicegui import app, ui

from components.consent_display_component import ConsentDisplayComponent

from components.preference_consent_display_component import (
    PreferenceConsentDisplayComponent,
)
from localization.language_manager import get_localization, make_localisable
from models.db_models import ConsentTemplate, ConsentSheet, LocalizedText
from models.controller import (
    duplicate_sheet,
    get_all_consent_topics,
    get_all_localized_texts,
    get_consent_sheet_by_id,
)


class SheetDisplayComponent(ui.column):
    sheet: ConsentSheet = None
    sheets: list[ConsentSheet] = None
    redact_name: bool
    categories: list[int]
    grouped_topics: dict[int, list[ConsentTemplate]]
    lang: str
    text_lookup: dict[int, LocalizedText]

    def __init__(
        self,
        consent_sheet: ConsentSheet = None,
        consent_sheets: list[ConsentSheet] = None,
        redact_name: bool = False,
        lang: str = "en",
    ):
        super().__init__()
        if consent_sheet is None:
            self.sheets = consent_sheets
        else:
            self.sheet = consent_sheet
        self.lang = lang
        self.text_lookup = get_all_localized_texts()
        self.redact_name = redact_name
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

    @property
    def sheet_name(self):
        if self.redact_name:
            return "Consent Sheet"
        return (
            self.sheet.human_name
            if self.sheet
            else get_localization("consent_of", self.lang) + str(len(self.sheets))
        )

    @property
    def sheet_comments(self):
        return (
            self.sheet.comment
            if self.sheet
            else "\n---\n".join(sheet.comment for sheet in self.sheets if sheet.comment)
        )

    def button_duplicate(self, user_id_name: str):
        logging.debug(f"Duplicating {self.sheet}")
        if duplicate := duplicate_sheet(self.sheet, user_id_name):
            ui.navigate.to(f"/home?lang={self.lang}")
            ui.notify(
                duplicate.human_name + get_localization("sheet_duplicated", self.lang)
            )
        else:
            ui.notify(get_localization("sheet_not_duplicated", self.lang))

    def refresh_sheets(self):
        if self.sheet:
            self.sheet = get_consent_sheet_by_id(self.sheet.id)
        if self.sheets:
            self.sheets = [get_consent_sheet_by_id(sheet.id) for sheet in self.sheets]

    @ui.refreshable
    def content(self):
        logging.debug(f"SheetDisplayComponent {self.sheet} {self.sheets}")
        self.refresh_sheets()
        self.clear()
        with self.classes("w-full"):
            self.display_head()
            with ui.grid().classes("w-full lg:grid-cols-5 grid-cols-1"):
                self.content_topic_displays()
            self.display_foot()

    def content_topic_displays(self):
        for category_id in self.categories:
            templates = self.grouped_topics[category_id]
            lookup_consents = {
                template.id: [
                    sheet.consent_entries_dict.get(template.id)
                    for sheet in self.sheets or [self.sheet]
                ]
                for template in templates
            }
            with ui.card().classes(f"row-span-{(len(templates) // 3) + 1} "):
                with ui.row().classes("w-full pt-6"):
                    ui.label(self.text_lookup[category_id].get_text(self.lang)).classes(
                        "text-xl"
                    )
                    for topic in templates:
                        ConsentDisplayComponent(lookup_consents[topic.id], self.lang)

        custom_entries = [
            entry
            for sheet in self.sheets or [self.sheet]
            for entry in sheet.custom_consent_entries
        ]
        with ui.card().classes("row-span-1"):
            with ui.row().classes("w-full pt-6"):
                ui.label("Custom Entries").classes("text-xl")
                for custom_entry in custom_entries:
                    PreferenceConsentDisplayComponent(
                        custom_entry.preference,
                        custom_text=custom_entry.content,
                        lang=self.lang,
                        comments=[custom_entry.comment],
                    )

    def display_foot(self):
        user_id_name = app.storage.user.get("user_id")
        if not user_id_name:
            make_localisable(ui.label(), key="login_to_duplicate", language=self.lang)
            return
        if self.sheet:
            make_localisable(
                ui.button(
                    "Duplicate",
                    on_click=lambda: self.button_duplicate(user_id_name),
                ),
                key="duplicate",
                language=self.lang,
            )

    def display_head(self):
        with ui.row().classes("w-full bg-gray-700 p-2 rounded-lg"):
            ui.label(self.sheet_name)
            ui.label(self.sheet_comments)
            if self.sheet and self.sheet.public_share_id and not self.redact_name:
                with ui.expansion("Share Link") as share_expansion:
                    make_localisable(
                        share_expansion, key="share_link_expansion", language=self.lang
                    )
                    make_localisable(
                        ui.link(
                            "Link to this sheet",
                            f"/consent/{self.sheet.public_share_id}/{self.sheet.id}&lang={self.lang}",
                        ),
                        key="share_link",
                        language=self.lang,
                    )
                    ui.image(
                        f"/api/qr?share_id={self.sheet.public_share_id}&sheet_id={self.sheet.id}&lang={self.lang}"
                    )
