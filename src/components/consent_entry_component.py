from nicegui import ui

from models.models import ConsentStatus, ConsentTemplate, ConsentEntry
from models.controller import update_entry
import logging


class ConsentEntryComponent(ui.row):
    consent_entry: ConsentEntry

    def __init__(self, consent_entry: ConsentEntry):
        super().__init__()
        if not consent_entry:
            logging.error("No consent entry")
            return
        self.consent_entry = consent_entry
        self.content()

    @ui.refreshable
    def content(self):
        self.clear()
        with self.classes("w-full"):
            self.comment_toggle = ui.checkbox("🗨️")
            ui.label(self.consent_entry.consent_template.topic).classes(
                "text-md"
            ).tooltip(self.consent_entry.consent_template.explanation)
            ui.space()
            self.toggle = ui.toggle(
                {status: status.as_emoji for status in ConsentStatus}
            ).bind_value(self.consent_entry, "preference")
            self.toggle.on_value_change(lambda _: update_entry(self.consent_entry))
            self.comment_input = (
                ui.input("Comment")
                .bind_visibility_from(self.comment_toggle, "value")
                .bind_value(self.consent_entry, "comment")
            )


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
