import logging

from nicegui import ui

from controller.sheet_controller import update_entry
from localization.language_manager import make_localisable
from models.db_models import ConsentEntry, ConsentStatus


class ConsentEntryComponent(ui.row):
    consent_entry: ConsentEntry
    lang: str

    def __init__(self, consent_entry: ConsentEntry, lang: str = "en"):
        super().__init__()
        if not consent_entry:
            logging.error("No consent entry")
            return
        self.lang = lang
        self.consent_entry = consent_entry
        self.content()

    @ui.refreshable
    def content(self):
        self.clear()
        with self.classes("w-full pt-6 lg:pt-1 gap-0 lg:gap-2"):
            self.comment_toggle = ui.checkbox("🗨️")
            ui.label(
                self.consent_entry.consent_template.topic_local.get_text(self.lang)
            ).classes("text-md").tooltip(
                self.consent_entry.consent_template.explanation_local.get_text(
                    self.lang
                )
            )
            ui.space()
            self.toggle = ui.toggle(
                {status: status.as_emoji for status in ConsentStatus}
            ).bind_value(self.consent_entry, "preference")
            self.toggle.on_value_change(lambda _: update_entry(self.consent_entry))
            self.comment_input = (
                ui.input("Comment")
                .bind_visibility_from(self.comment_toggle, "value")
                .bind_value(self.consent_entry, "comment")
            ).on("focusout", lambda _: update_entry(self.consent_entry))
            make_localisable(self.comment_input, key="comment", language=self.lang)


class CategoryEntryComponent(ui.row):
    category: str
    topics: list[ConsentEntryComponent]

    def __init__(self, category: str):
        super().__init__()
        self.category = category
        with self.classes("w-full pt-6"):
            ui.label(self.category).classes("text-xl")
            ui.space()
            self.toggle = ui.toggle(
                {status: status.as_emoji for status in ConsentStatus},
                on_change=self.on_change,
            )

    def on_change(self):
        for topic in self.topics:
            if topic.toggle.value == ConsentStatus.unknown:
                topic.consent_entry.preference = self.toggle.value
