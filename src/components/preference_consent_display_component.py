import random

from nicegui import ui

from controller.sheet_controller import get_consent_template_by_id
from models.db_models import ConsentStatus, ConsentTemplate
from services.session_service import session_storage


class PreferenceConsentDisplayComponent(ui.row):
    preference: ConsentStatus
    consent_template: ConsentTemplate | None = None
    comments: list[str]
    custom_text: str

    def __init__(
        self,
        status: ConsentStatus,
        consent_template_id: int = None,
        custom_text: str = None,
        comments: list[str] = None,
    ):
        super().__init__()
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
        lang = session_storage.get("lang", "en")
        content_text = (
            self.consent_template.topic_local.get_text(lang)
            if self.consent_template
            else self.custom_text
        )
        content_tooltip = (
            self.consent_template.explanation_local.get_text(lang)
            if self.consent_template
            else ""
        )
        category_text = (
            self.consent_template.category_local.get_text(lang)
            if self.consent_template
            else "Custom"
        )
        with self.classes("w-full"):
            ui.label(content_text).classes("text-md").tooltip(content_tooltip)
            ui.label(category_text).classes("text-xs text-gray-500")
            ui.space()
            ui.label(f"{self.preference.as_emoji}").tooltip(
                self.preference.explanation(lang)
            )
            if self.comments:
                ui.label(" |#| ".join(self.comments)).classes("text-md")
