from nicegui import ui

from models.controller import get_consent_template_by_id
from models.db_models import ConsentEntry, ConsentStatus, ConsentTemplate
import logging
import random


class PreferenceConsentDisplayComponent(ui.row):
    preference: ConsentStatus
    consent_template: ConsentTemplate | None = None
    comments: list[str]
    custom_text: str
    lang: str

    def __init__(
        self,
        status: ConsentStatus,
        consent_template_id: int = None,
        custom_text: str = None,
        comments: list[str] = None,
        lang: str = "en",
    ):
        super().__init__()
        self.lang = lang
        self.preference = status
        self.custom_text = custom_text
        if consent_template_id:
            self.consent_template = get_consent_template_by_id(consent_template_id)
        self.comments = comments or []
        if self.comments:
            random.shuffle(self.comments)
        self.content()

    @ui.refreshable
    def content(self):
        self.clear()
        content_text = (
            self.consent_template.topic_local.get_text(self.lang)
            if self.consent_template
            else self.custom_text
        )
        content_tooltip = (
            self.consent_template.explanation_local.get_text(self.lang)
            if self.consent_template
            else ""
        )
        category_text = (
            self.consent_template.category_local.get_text(self.lang)
            if self.consent_template
            else "Custom"
        )
        with self.classes("w-full"):
            ui.label(content_text).classes("text-md").tooltip(content_tooltip)
            ui.label(category_text).classes("text-xs text-gray-500")
            ui.space()
            ui.label(f"{self.preference.as_emoji}").tooltip(
                self.preference.explanation(self.lang)
            )
            if self.comments:
                ui.label(" |#| ".join(self.comments)).classes("text-md")
