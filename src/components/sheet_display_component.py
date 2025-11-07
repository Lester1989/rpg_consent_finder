import logging

from nicegui import app, ui

from components.consent_display_component import ConsentDisplayComponent
from components.preference_consent_display_component import (
    PreferenceConsentDisplayComponent,
)
from controller.sheet_controller import (
    duplicate_sheet,
    get_all_consent_topics,
    get_consent_sheet_by_id,
)
from controller.util_controller import (
    get_all_localized_texts,
)
from localization.language_manager import get_localization, make_localisable
from models.db_models import (
    ConsentSheet,
    ConsentTemplate,
    CustomConsentEntry,
    LocalizedText,
)
from controller.user_controller import get_user_from_storage
from models.db_models import ConsentStatus


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
        logging.getLogger("content_consent_finder").debug(
            f"SheetDisplayComponent {consent_sheet} {consent_sheets}"
        )
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
            else get_localization("consent_of", self.lang)
            + str(len(self.sheets) if self.sheets else 1)
        )

    @property
    def sheet_comments(self):
        return (
            self.sheet.comment
            if self.sheet
            else "\n---\n".join(
                sheet.comment for sheet in self.sheets if sheet and sheet.comment
            )
        )

    def button_duplicate(self, user_id: int):
        logging.getLogger("content_consent_finder").debug(f"Duplicating {self.sheet}")
        if duplicate := duplicate_sheet(self.sheet, user_id):
            ui.navigate.to(f"/home?lang={self.lang}")
            ui.notify(
                duplicate.human_name + get_localization("sheet_duplicated", self.lang)
            )
        else:
            ui.notify(get_localization("sheet_not_duplicated", self.lang))

    def refresh_sheets(self):
        if self.sheet:
            self.sheet = get_consent_sheet_by_id(self.user.id_name, self.sheet.id)
        if self.sheets:
            self.sheets = [
                get_consent_sheet_by_id(self.user.id_name, sheet.id)
                for sheet in self.sheets
            ]

    @ui.refreshable
    def content(self):
        logging.getLogger("content_consent_finder").debug(
            f"SheetDisplayComponent {self.sheet or self.sheets}"
        )
        self.user = get_user_from_storage()
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
            if entry.content
        ]
        grouped_custom_entries: dict[str, list[CustomConsentEntry]] = {}
        for entry in custom_entries:
            key = entry.content.lower()
            if key not in grouped_custom_entries:
                grouped_custom_entries[key] = []
            grouped_custom_entries[key].append(entry)
        with ui.card().classes("row-span-1"):
            with ui.row().classes("w-full pt-6"):
                ui.label("Custom Entries").classes("text-xl")
                for custom_entries in grouped_custom_entries.values():
                    PreferenceConsentDisplayComponent(
                        status=ConsentStatus.get_consent(
                            [entry.preference for entry in custom_entries]
                        ),
                        custom_text=custom_entries[0].content,
                        lang=self.lang,
                        comments=[
                            entry.comment for entry in custom_entries if entry.comment
                        ],
                    )

    def display_foot(self):
        if not self.user:
            make_localisable(ui.label(), key="login_to_duplicate", language=self.lang)
            return
        if self.sheet:
            make_localisable(
                ui.button(
                    "Duplicate",
                    on_click=lambda: self.button_duplicate(self.user.id),
                ),
                key="duplicate",
                language=self.lang,
            )

    def display_head(self):
        with ui.row().classes("w-full bg-gray-700 p-2 rounded-lg"):
            ui.label(self.sheet_name).mark("sheet_name_display")
            ui.label(self.sheet_comments).mark("sheet_comments_display")
            if self.sheet and self.sheet.public_share_id and not self.redact_name:
                with ui.expansion("Share Link") as share_expansion:
                    make_localisable(
                        share_expansion, key="share_link_expansion", language=self.lang
                    )
                    make_localisable(
                        ui.link(
                            "Link to this sheet",
                            f"/consent/{self.sheet.public_share_id}/{self.sheet.id}?lang={self.lang}",
                            new_tab=True,
                        ).mark("share_link"),
                        key="share_link",
                        language=self.lang,
                    )
                    ui.image(
                        f"/api/qr?share_id={self.sheet.public_share_id}&sheet_id={self.sheet.id}&lang={self.lang}"
                    )
