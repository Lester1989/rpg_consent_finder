import logging
from nicegui import ui, app

from components.faq_element_component import FAQElementComponent
from localization.language_manager import make_localisable, get_localization
from models.controller import get_all_faq, store_faq_question


def store_user_faq(user_faq: str, lang: str = "en"):
    logging.debug(user_faq)
    result = store_faq_question(user_faq)
    if result.id:
        ui.notify(get_localization("question_stored", lang), type="positive")
    else:
        ui.notify(get_localization("question_not_stored", lang), type="negative")


@ui.refreshable
def content(lang: str = "en", **kwargs):
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
