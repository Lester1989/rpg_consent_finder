from nicegui import ui

from models.db_models import ConsentEntry
import logging


class ConsentDisplayComponent(ui.row):
    consents: list[ConsentEntry]

    def __init__(self, consents: list[ConsentEntry]):
        super().__init__()
        if not consents or not consents[0]:
            logging.debug("No consents found")
            return
        self.consents = consents
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
            ui.label(self.consents[0].consent_template.topic).classes(
                "text-md"
            ).tooltip(self.consents[0].consent_template.explanation)
            ui.space()
            ui.label(f"{group_consent.preference.as_emoji}").tooltip(
                group_consent.preference.explanation_de
            )

            ui.label(self.consents[0].comment).classes("text-md")
