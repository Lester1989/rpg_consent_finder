from nicegui import ui, app
from models.db_models import (
    ConsentStatus,
)
from localization.language_manager import make_localisable


def consent_legend_component():
    lang = app.storage.user.get("lang", "en")
    make_localisable(ui.label().classes("text-2xl mx-auto"), key="consent_levels")
    with ui.grid().classes(
        "lg:grid-cols-5 grid-cols-2 gap-2 lg:w-5/6 w-full mx-auto"
    ) as grid:
        for preference in ConsentStatus:
            with ui.column().classes(
                "p-2 rounded-lg shadow-sm shadow-white gap-1 items-center rounded-lg shadow-sm dark:shadow-white bg-zinc-100 dark:bg-zinc-800 text-stone-900 dark:text-orange-50"
            ):
                ui.label(preference.as_emoji + preference.name.capitalize()).classes(
                    "text-xs dark:text-amber-100 text-zinc-800 font-bold"
                )
                ui.markdown(preference.explanation(lang))
    return grid
