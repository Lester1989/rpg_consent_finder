from nicegui import ui, app
from models.db_models import (
    ConsentStatus,
)
from localization.language_manager import make_localisable


def consent_legend_component(lang: str = "en"):
    make_localisable(
        ui.label().classes("text-2xl mx-auto"), key="consent_levels", language=lang
    )
    with ui.grid().classes("lg:grid-cols-5 grid-cols-2 gap-2 lg:w-5/6 w-full mx-auto"):
        for preference in ConsentStatus:
            with ui.column().classes(
                "p-2 rounded-lg shadow-sm shadow-white gap-1 items-center"
            ):
                ui.label(preference.as_emoji + preference.name.capitalize()).classes(
                    "text-xs text-gray-500 text-center"
                )
                ui.markdown(preference.explanation(lang))
