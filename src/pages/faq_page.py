import logging
from nicegui import ui, app

from components.faq_element_component import FAQElementComponent
from guided_tour import NiceGuidedTour
from localization.language_manager import make_localisable, get_localization
from models.controller import get_all_faq, store_faq_question


def store_user_faq(user_faq: str, lang: str = "en"):
    logging.debug(user_faq)
    result = store_faq_question(user_faq)
    if result.id:
        ui.notify(get_localization("question_stored", lang), type="positive")
    else:
        ui.notify(get_localization("question_not_stored", lang), type="negative")


def start_tour(tour_name: str, lang: str = "en"):
    logging.info(f"Starting tour {tour_name}")
    if tour_name == "create_sheet":
        for key in app.storage.user.keys():
            if isinstance(key, str) and key.startswith("tour_create_sheet_progress"):
                app.storage.user[key] = 0
        ui.navigate.to(f"/home?lang={lang}")
        return
    elif tour_name == "share_sheet":
        for key in app.storage.user.keys():
            if isinstance(key, str) and key.startswith("tour_share_sheet_progress"):
                app.storage.user[key] = 0
        ui.navigate.to(f"/home?lang={lang}")
        return
    ui.notify("Tour not found", type="negative")


def make_tour_card(lang: str, tour: str):
    with ui.card():
        make_localisable(
            ui.label().classes("text-xl font-bold"),
            key=f"howto_header_{tour}",
            language=lang,
        )
        ui.markdown(
            get_localization(f"howto_text_{tour}", language=lang),
        )
        make_localisable(
            ui.button().on_click(lambda tour=tour: start_tour(tour, lang)),
            key=f"howto_button_{tour}",
            language=lang,
        )


@ui.refreshable
def content(lang: str = "en", **kwargs):
    tours = ["create_sheet", "share_sheet", "create_group", "join_group"]
    with ui.grid().classes("gap-4 mx-auto lg:grid-cols-4 grid-cols-1 2xl:w-2/3"):
        for tour in tours:
            make_tour_card(lang, tour)
    ui.separator()
    faq_items = get_all_faq()
    with ui.grid().classes("gap-4 mx-auto lg:grid-cols-2 grid-cols-1 2xl:w-2/3"):
        for faq_item in faq_items:
            FAQElementComponent(
                faq_item.question_local.get_text(lang),
                faq_item.answer_local.get_text(lang),
            )
    with ui.card().classes("w-5/6 mx-auto 2xl:w-2/3"):
        user_faq = ui.textarea("Neue Frage").classes("w-full")
        make_localisable(
            user_faq,
            key="faq_question",
            language=lang,
        )
        make_localisable(
            ui.button("Abschicken").on_click(
                lambda: store_user_faq(user_faq.value, lang)
            ),
            key="submit",
            language=lang,
        )
