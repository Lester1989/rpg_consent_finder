from nicegui import ui

from models.models import ConsentStatus
from models.controller import get_all_consent_topics


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
