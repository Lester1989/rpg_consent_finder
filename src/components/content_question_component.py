import logging

from nicegui import ui

from controller.admin_controller import (
    remove_content_question,
    store_content_answer,
)
from controller.sheet_controller import get_all_consent_topics
from models.db_models import UserContentQuestion
from services.session_service import session_storage


class ContentQuestionComponent(ui.expansion):
    content_question: UserContentQuestion

    def __init__(self, content: UserContentQuestion, refresh_func):
        super().__init__(f"{content.created_at:%Y-%m-%d %H:%M} | {content.question}")
        self.content_question = content
        self.refresh_func = refresh_func
        ui.add_css("""
        .nicegui-markdown h3 {
            font-size: 1.5em;
        }
        .nicegui-markdown h4 {
            font-size: 1.25em;
        }
        """)
        self.content()

    def reload_after(self, func, *args, **kwargs):
        logging.getLogger("content_consent_finder").debug(
            f"Reloading after {func.__name__}"
        )
        func(*args, **kwargs)
        self.refresh_func()

    @ui.refreshable
    def content(self):
        lang = session_storage.get("lang", "en")
        templates = get_all_consent_topics()
        categories = {
            template.category_id: template.category_local.get_text(lang)
            for template in templates
        }
        with self.classes("w-full border border-gray-200 rounded p-4 text-lg"):
            category_select = ui.select(label="Category", options=categories).classes(
                "w-full"
            )
            topic_input = ui.input("topic").classes("w-full")
            explanation_input = ui.textarea("explanation").classes("w-full")
            ui.button(
                "add to Content",
                on_click=lambda category_select=category_select,
                topic_input=topic_input,
                explanation_input=explanation_input,
                content=self.content: self.reload_after(
                    store_content_answer,
                    category_select.value,
                    topic_input.value,
                    explanation_input.value,
                    content,
                ),
            )
            ui.button("delete", color="red").on_click(
                lambda content=self.content: self.reload_after(
                    remove_content_question, content
                )
            )
