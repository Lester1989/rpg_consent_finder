from nicegui import ui

from models.controller import get_consent_template_by_id
from models.db_models import ConsentEntry, ConsentTemplate, ConsentStatus
import logging


class ConsentDisplayComponent(ui.row):
    consents: list[ConsentEntry]
    consent_template: ConsentTemplate
    lang: str

    def __init__(self, consents: list[ConsentEntry], lang: str = "en"):
        super().__init__()
        if not consents or not consents[0]:
            logging.debug("No consents found")
            return
        self.lang = lang
        self.consents = consents
        self.consent_template = get_consent_template_by_id(
            self.consents[0].consent_template_id
        )
        self.content()

    @ui.refreshable
    def content(self):
        self.clear()
        group_consent = ConsentStatus.get_consent(
            [consent.preference for consent in self.consents]
        )
        with self.classes("w-full"):
            ui.label(self.consent_template.topic_local.get_text(self.lang)).classes(
                "text-md"
            ).tooltip(self.consent_template.explanation_local.get_text(self.lang))
            ui.space()
            ui.label(f"{group_consent.as_emoji}").tooltip(
                group_consent.explanation(self.lang)
            )

            ui.label(self.consents[0].comment).classes("text-md")
