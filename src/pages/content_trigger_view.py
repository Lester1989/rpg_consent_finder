import logging

from nicegui import ui

from components.consent_legend_component import consent_legend_component
from controller.sheet_controller import get_all_consent_topics
from controller.util_controller import store_content_question
from localization.language_manager import get_localization, make_localisable


def store_user_question(question: str, lang: str = "en"):
    logging.getLogger("content_consent_finder").debug(question)
    result = store_content_question(question)
    if result.id:
        ui.notify(get_localization("question_stored", lang), type="positive")
    else:
        ui.notify(get_localization("question_not_stored", lang), type="negative")


@ui.refreshable
def content(lang: str = "en", **kwargs):
    topics = get_all_consent_topics()

    consent_legend_component(lang)
    ui.separator()
    make_localisable(
        ui.label("Consent Topics").classes("text-2xl mx-auto"),
        key="consent_topics",
        language=lang,
    )
    with ui.grid().classes(
        "lg:grid-cols-2 gap-4 lg:w-5/6 w-full grid-cols-1 mx-auto 2xl:w-2/3"
    ):
        for topic in topics:
            with ui.column().classes(
                "w-full gap-0 p-2 rounded-lg shadow-sm shadow-white"
            ):
                ui.label(topic.topic_local.get_text(lang)).classes("text-lg")
                ui.label(topic.category_local.get_text(lang)).classes(
                    "text-xs text-gray-500"
                )
                ui.space()
                ui.markdown(
                    topic.explanation_local.get_text(lang) or "coming \n\n soon"
                )
    with ui.card().classes("w-5/6 mx-auto"):
        user_question = ui.textarea("Frage oder Anmerkung").classes("w-full")
        make_localisable(
            ui.button("Abschicken").on_click(
                lambda: store_user_question(user_question.value)
            ),
            key="submit",
            language=lang,
        )
