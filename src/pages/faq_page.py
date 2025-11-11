import logging

from nicegui import app, ui

from components.faq_element_component import FAQElementComponent
from controller.user_controller import get_user_from_storage
from controller.util_controller import get_all_faq, store_faq_question
from localization.language_manager import get_localization, make_localisable


def store_user_faq(user_faq: str):
    logging.getLogger("content_consent_finder").debug(user_faq)
    result = store_faq_question(user_faq)
    if result.id:
        ui.notify(get_localization("question_stored"), type="positive")
    else:
        ui.notify(get_localization("question_not_stored"), type="negative")


def start_tour(tour_name: str):
    logging.getLogger("content_consent_finder").info(f"Starting tour {tour_name}")
    app.storage.user["active_tour"] = tour_name
    for key in app.storage.user.keys():
        if isinstance(key, str) and key.startswith(f"tour_{tour_name}_progress"):
            app.storage.user[key] = 0
    ui.navigate.to("/home")


def make_tour_card(tour: str):
    with ui.card():
        make_localisable(
            ui.label().classes("text-xl font-bold"),
            key=f"howto_header_{tour}",
        )
        ui.markdown(get_localization(f"howto_text_{tour}"))
        start_button = (
            ui.button()
            .on_click(lambda tour=tour: start_tour(tour))
            .mark(f"start_tour_{tour}")
        )
        if not get_user_from_storage():
            start_button.set_enabled(False)
            start_button.tooltip(get_localization("login_required_for_tour"))
        make_localisable(
            start_button,
            key=f"howto_button_{tour}",
        )


def content(**kwargs):
    lang = app.storage.user.get("lang", "en")
    tours = ["create_sheet", "share_sheet", "create_group", "join_group"]
    with ui.grid().classes("gap-4 mx-auto lg:grid-cols-4 grid-cols-1 2xl:w-2/3"):
        for tour in tours:
            make_tour_card(tour)
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
        )
        make_localisable(
            ui.button("Abschicken").on_click(lambda: store_user_faq(user_faq.value)),
            key="submit",
        )
