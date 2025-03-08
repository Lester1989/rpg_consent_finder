import logging

from nicegui import app, ui

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
    ConsentStatus,
    ConsentTemplate,
    CustomConsentEntry,
    LocalizedText,
)
from controller.user_controller import get_user_from_storage


class PreferenceOrderedSheetDisplayComponent(ui.column):
    sheet: ConsentSheet = None
    sheets: list[ConsentSheet] = None
    redact_name: bool
    lang: str
    text_lookup: dict[int, LocalizedText]
    share_expansion: ui.expansion
    share_image: ui.image

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
        self.templates: list[ConsentTemplate] = get_all_consent_topics()
        self.content()

    @property
    def sheet_name(self):
        if self.redact_name:
            return "Consent Sheet"
        return (
            self.sheet.display_name
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

    def button_duplicate(self, user_id: str):
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
            self.sheet = get_consent_sheet_by_id(
                app.storage.user.get("user_id"), self.sheet.id
            )
        if self.sheets:
            self.sheets = [
                get_consent_sheet_by_id(app.storage.user.get("user_id"), sheet.id)
                for sheet in self.sheets
            ]

    @ui.refreshable
    def content(self):
        logging.getLogger("content_consent_finder").warning(
            f"SheetDisplayComponent {self.sheet} {self.sheets}"
        )
        self.refresh_sheets()
        self.clear()
        with self.classes("w-full"):
            self.display_head()
            with ui.grid().classes("w-full lg:grid-cols-5 grid-cols-1"):
                self.content_topic_displays()
            self.display_foot()

    def content_topic_displays(self):
        lookup_consents = {
            template.id: ConsentStatus.get_consent(
                [
                    sheet.consent_entries_dict.get(template.id).preference
                    for sheet in self.sheets or [self.sheet]
                ]
            )
            for template in self.templates
        }
        prefence_entries: dict[
            ConsentStatus, list[ConsentTemplate | CustomConsentEntry]
        ] = {
            status: [
                template
                for template in self.templates
                if lookup_consents[template.id] == status
            ]
            for status in ConsentStatus
        }
        for sheet in self.sheets or [self.sheet]:
            for custom_entry in sheet.custom_consent_entries:
                if custom_entry.content == "":
                    continue
                prefence_entries[custom_entry.preference].append(custom_entry)

        for status in ConsentStatus.ordered():
            if not prefence_entries.get(status):
                continue
            with ui.card().classes(
                f"row-span-{(len(prefence_entries.get(status)) // 3) + 1} "
            ):
                with ui.expansion(
                    text=status.as_emoji + status.name.capitalize()
                ).classes(
                    "mx-auto text-center border-2 rounded-lg"
                ) as status_expansion:
                    ui.markdown(status.explanation(self.lang))
                logging.getLogger("content_consent_finder").warning(
                    f"Displaying {status} with {len(prefence_entries[status])} entries"
                )
                status_expansion.mark(f"status_expansion_{status.name}")
                for template_or_custom in prefence_entries[status]:
                    if isinstance(template_or_custom, ConsentTemplate):
                        logging.getLogger("content_consent_finder").debug(
                            f"Displaying {template_or_custom}"
                        )
                        PreferenceConsentDisplayComponent(
                            status,
                            consent_template_id=template_or_custom.id,
                            lang=self.lang,
                        )
                    elif isinstance(template_or_custom, CustomConsentEntry):
                        logging.getLogger("content_consent_finder").debug(
                            f"Displaying {template_or_custom}"
                        )
                        PreferenceConsentDisplayComponent(
                            status,
                            custom_text=template_or_custom.content,
                            lang=self.lang,
                        )

    def display_foot(self):
        user = get_user_from_storage()
        if not user:
            make_localisable(ui.label(), key="login_to_duplicate", language=self.lang)
            return
        if self.sheet:
            make_localisable(
                ui.button(
                    "Duplicate",
                    on_click=lambda: self.button_duplicate(user.id),
                ),
                key="duplicate",
                language=self.lang,
            )

    def display_head(self):
        with ui.row().classes("w-full bg-gray-700 p-2 rounded-lg"):
            ui.label(self.sheet_name)
            ui.label(self.sheet_comments)
            if self.sheet and self.sheet.public_share_id and not self.redact_name:
                with ui.expansion("Share Link") as self.share_expansion:
                    make_localisable(
                        self.share_expansion,
                        key="share_link_expansion",
                        language=self.lang,
                    )
                    make_localisable(
                        ui.link(
                            "Link to this sheet",
                            f"/consent/{self.sheet.public_share_id}/{self.sheet.id}?lang={self.lang}",
                        ),
                        key="share_link",
                        language=self.lang,
                    )
                    self.share_image = ui.image(
                        f"/api/qr?share_id={self.sheet.public_share_id}&sheet_id={self.sheet.id}&lang={self.lang}"
                    )
            else:
                self.share_image = None
                self.share_expansion = None
