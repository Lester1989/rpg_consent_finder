import logging
from nicegui import ui

from models.db_models import ConsentStatus
from models.controller import get_all_consent_topics, store_content_question


def store_user_question(question: str):
    logging.debug(question)
    result = store_content_question(question)
    if result.id:
        ui.notify("Frage wurde gespeichert", type="positive")
    else:
        ui.notify(
            "Frage konnte nicht gespeichert werden, Kontaktiere mich auf Discord",
            type="negative",
        )


@ui.refreshable
def content(**kwargs):
    topics = get_all_consent_topics()
    ui.label("Consent Levels").classes("text-2xl mx-auto")
    with ui.grid(rows=1, columns=5).classes("gap-2 w-5/6 mx-auto"):
        for preference in ConsentStatus:
            with ui.column().classes(
                "p-2 rounded-lg shadow-sm shadow-white gap-1 items-center"
            ):
                ui.label(preference.as_emoji + preference.name.capitalize()).classes(
                    "text-xs text-gray-500 text-center"
                )
                ui.markdown(preference.explanation_de)
    ui.separator()
    ui.label("Consent Topics").classes("text-2xl mx-auto")
    with ui.grid(columns=2).classes("gap-4 w-5/6 mx-auto"):
        for topic in topics:
            with ui.column().classes(
                "w-full gap-0 p-2 rounded-lg shadow-sm shadow-white"
            ):
                ui.label(topic.topic).classes("text-lg")
                ui.label(topic.category).classes("text-xs text-gray-500")
                ui.space()
                ui.markdown(topic.explanation or "coming \n\n soon")
    with ui.card().classes("w-5/6 mx-auto"):
        user_question = ui.textarea("Frage oder Anmerkung").classes("w-full")
        ui.button("Abschicken").on_click(
            lambda: store_user_question(user_question.value)
        )
