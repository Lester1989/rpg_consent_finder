from nicegui import ui

from models.controller import get_consent_template_by_id
from models.db_models import ConsentEntry, ConsentTemplate
import logging


class ConsentDisplayComponent(ui.row):
    consents: list[ConsentEntry]
    consent_template: ConsentTemplate

    def __init__(self, consents: list[ConsentEntry]):
        super().__init__()
        if not consents or not consents[0]:
            logging.debug("No consents found")
            return
        self.consents = consents
        self.consent_template = get_consent_template_by_id(
            self.consents[0].consent_template_id
        )
        self.content()

    @ui.refreshable
    def content(self):
        self.clear()
        group_consent = (
            sorted(self.consents, key=lambda x: x.preference.order)[-1]
            if self.consents
            else None
        )
        with self.classes("w-full"):
            ui.label(self.consent_template.topic).classes("text-md").tooltip(
                self.consent_template.explanation
            )
            ui.space()
            ui.label(f"{group_consent.preference.as_emoji}").tooltip(
                group_consent.preference.explanation_de
            )

            ui.label(self.consents[0].comment).classes("text-md")
