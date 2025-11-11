import logging

from nicegui import ui, events, app

from controller.sheet_controller import update_entry
from localization.language_manager import make_localisable
from models.db_models import ConsentEntry, ConsentStatus, User


class ConsentEntryComponent(ui.row):
    consent_entry: ConsentEntry

    def __init__(
        self,
        consent_entry: ConsentEntry,
        user: User,
    ):
        super().__init__()
        if not consent_entry:
            logging.getLogger("content_consent_finder").error("No consent entry")
            return
        self.consent_entry = consent_entry
        self.user = user
        self.content()

    def update_value(self, value_change: events.ValueChangeEventArguments):
        if value_change.value is None:
            return
        logging.getLogger("content_consent_finder").debug(
            f"ConsentEntryComponent {self.consent_entry.consent_template.id} {value_change}"
        )
        self.consent_entry.preference = value_change.value
        update_entry(self.user, self.consent_entry)

    @ui.refreshable
    def content(self):
        self.clear()
        lang = app.storage.user.get("lang", "en")
        with self.classes("w-full pt-6 lg:pt-1 gap-0 lg:gap-2"):
            self.comment_toggle = ui.checkbox("🗨️")
            self.comment_toggle.mark(
                f"comment_toggle_{self.consent_entry.consent_template.id}"
            )
            ui.label(
                self.consent_entry.consent_template.topic_local.get_text(lang)
            ).classes("text-md").tooltip(
                self.consent_entry.consent_template.explanation_local.get_text(lang)
            )
            ui.space()
            self.toggle = ui.toggle(
                {status: status.as_emoji for status in ConsentStatus}
            ).bind_value(self.consent_entry, "preference")
            self.toggle.on_value_change(self.update_value)
            self.toggle.mark(f"toggle_{self.consent_entry.consent_template.id}")
            self.comment_input = (
                ui.input("Comment")
                .bind_visibility_from(self.comment_toggle, "value")
                .bind_value(self.consent_entry, "comment")
                .on("focusout", lambda _: update_entry(self.user, self.consent_entry))
                .mark(f"comment_input_{self.consent_entry.consent_template.id}")
            )
            make_localisable(self.comment_input, key="comment")


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
            self.toggle.mark(f"category_toggle_{self.category.lower()}")

    def on_change(self):
        logging.getLogger("content_consent_finder").info(
            f"CategoryEntryComponent {self.category} {self.toggle.value} clicked"
        )
        for topic in self.topics:
            if topic.toggle.value == ConsentStatus.unknown:
                topic.consent_entry.preference = self.toggle.value
