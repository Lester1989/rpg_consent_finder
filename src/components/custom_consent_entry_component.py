import logging

from nicegui import ui

from controller.sheet_controller import update_custom_entry
from localization.language_manager import get_localization, make_localisable
from models.db_models import ConsentStatus, CustomConsentEntry
from src.controller.user_controller import get_user_from_storage


class CustomConsentEntryComponent(ui.row):
    consent_entry: CustomConsentEntry
    lang: str

    def __init__(self, consent_entry: CustomConsentEntry, lang: str = "en"):
        super().__init__()
        if not consent_entry:
            logging.getLogger("content_consent_finder").error("No consent entry")
            return
        self.lang = lang
        self.consent_entry = consent_entry
        self.user = get_user_from_storage()
        self.content()

    @ui.refreshable
    def content(self):
        self.clear()
        with self.classes("w-full pt-6 lg:pt-1 gap-0 lg:gap-2"):
            self.comment_toggle = ui.checkbox("🗨️")
            content_input = (
                ui.input(
                    "Content",
                    validation={
                        get_localization(
                            "empty_will_be_removed", self.lang
                        ): lambda x: x
                    },
                )
                .classes("text-md")
                .bind_value(self.consent_entry, "content")
                .on(
                    "focusout",
                    lambda _: update_custom_entry(self.user, self.consent_entry),
                )
            )
            self.comment_toggle.mark("custom_consent_entry_comment_toggle")
            content_input.mark("custom_consent_entry_content")
            make_localisable(content_input, key="content", language=self.lang)
            ui.space()
            self.toggle = ui.toggle(
                {status: status.as_emoji for status in ConsentStatus}
            ).bind_value(self.consent_entry, "preference")
            self.toggle.mark("custom_consent_entry_toggle")
            self.toggle.on_value_change(
                lambda _: update_custom_entry(self.user, self.consent_entry)
            )
            self.comment_input = (
                ui.input("Comment")
                .bind_visibility_from(self.comment_toggle, "value")
                .bind_value(self.consent_entry, "comment")
                .on(
                    "focusout",
                    lambda _: update_custom_entry(self.user, self.consent_entry),
                )
            )
            self.comment_input.mark("custom_consent_entry_comment")
            make_localisable(self.comment_input, key="comment", language=self.lang)
