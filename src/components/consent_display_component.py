import logging

from nicegui import ui

from controller.sheet_controller import get_consent_template_by_id
from models.db_models import ConsentEntry, ConsentStatus, ConsentTemplate
from services.session_service import session_storage


class ConsentDisplayComponent(ui.row):
    consents: list[ConsentEntry]
    consent_template: ConsentTemplate

    def __init__(self, consents: list[ConsentEntry]):
        super().__init__()
        if not consents or not consents[0]:
            logging.getLogger("content_consent_finder").debug("No consents found")
            return
        self.consents = consents
        self.consent_template = get_consent_template_by_id(
            self.consents[0].consent_template_id
        )
        self.content()

    @ui.refreshable
    def content(self):
        self.clear()
        lang = session_storage.get("lang", "en")
        group_consent = ConsentStatus.get_consent(
            [consent.preference for consent in self.consents]
        )
        with self.classes("w-full"):
            ui.label(self.consent_template.topic_local.get_text(lang)).classes(
                "text-md"
            ).tooltip(self.consent_template.explanation_local.get_text(lang))
            ui.space()
            ui.label(f"{group_consent.as_emoji}").tooltip(
                group_consent.explanation(lang)
            )

            ui.label(self.consents[0].comment).classes("text-md")
