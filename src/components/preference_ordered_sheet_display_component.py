import logging

from nicegui import ui

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
from services.session_service import get_current_user_id, session_storage


class PreferenceOrderedSheetDisplayComponent(ui.column):
    sheet: ConsentSheet = None
    sheets: list[ConsentSheet] = None
    redact_name: bool
    text_lookup: dict[int, LocalizedText]
    share_expansion: ui.expansion
    share_image: ui.image

    def __init__(
        self,
        consent_sheet: ConsentSheet = None,
        consent_sheets: list[ConsentSheet] = None,
        redact_name: bool = False,
    ):
        super().__init__()
        if consent_sheet is None:
            self.sheets = consent_sheets
        else:
            self.sheet = consent_sheet
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
            else get_localization("consent_of") + str(len(self.sheets))
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
            ui.navigate.to("/home")
            ui.notify(duplicate.human_name + get_localization("sheet_duplicated"))
        else:
            ui.notify(get_localization("sheet_not_duplicated"))

    def refresh_sheets(self):
        user_id = get_current_user_id()
        if self.sheet:
            self.sheet = (
                get_consent_sheet_by_id(user_id, self.sheet.id) if user_id else None
            )
        if self.sheets:
            self.sheets = [
                get_consent_sheet_by_id(user_id, sheet.id) if user_id else None
                for sheet in self.sheets
            ]
            self.sheets = [sheet for sheet in self.sheets if sheet is not None]

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
        lang = session_storage.get("lang", "en")
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
        grouped_custom_entries: dict[str, list[CustomConsentEntry]] = {}
        for sheet in self.sheets or [self.sheet]:
            for custom_entry in sheet.custom_consent_entries:
                if custom_entry.content == "":
                    continue
                grouped_custom_entries.setdefault(
                    custom_entry.content.lower(), []
                ).append(custom_entry)

        for content, entries in grouped_custom_entries.items():
            status = ConsentStatus.get_consent([entry.preference for entry in entries])
            prefence_entries.setdefault(status, []).append(
                CustomConsentEntry(
                    content=content,
                    preference=status,
                    comment="; ".join(
                        entry.comment for entry in entries if entry.comment
                    ),
                )
            )

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
                    ui.markdown(status.explanation(lang))
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
                        )
                    elif isinstance(template_or_custom, CustomConsentEntry):
                        logging.getLogger("content_consent_finder").debug(
                            f"Displaying {template_or_custom}"
                        )
                        PreferenceConsentDisplayComponent(
                            status,
                            custom_text=template_or_custom.content,
                        )

    def display_foot(self):
        user = get_user_from_storage()
        if not user:
            make_localisable(ui.label(), key="login_to_duplicate")
            return
        if self.sheet:
            make_localisable(
                ui.button(
                    "Duplicate",
                    on_click=lambda: self.button_duplicate(user.id),
                ),
                key="duplicate",
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
                    )
                    make_localisable(
                        ui.link(
                            "Link to this sheet",
                            f"/consent/{self.sheet.public_share_id}/{self.sheet.id}",
                        ),
                        key="share_link",
                    )
                    self.share_image = ui.image(
                        f"/api/qr?share_id={self.sheet.public_share_id}&sheet_id={self.sheet.id}"
                    )
            else:
                self.share_image = None
                self.share_expansion = None
