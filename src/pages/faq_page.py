import logging
from nicegui import ui, app

from components.faq_element_component import FAQElementComponent
from models.controller import get_all_faq, store_faq_question


def store_user_faq(user_faq: str):
    logging.debug(user_faq)
    result = store_faq_question(user_faq)
    if result.id:
        ui.notify("Frage wurde gespeichert", type="positive")
    else:
        ui.notify(
            "Frage konnte nicht gespeichert werden, Kontaktiere mich auf Discord",
            type="negative",
        )


@ui.refreshable
def content(**kwargs):
    faq_items = get_all_faq()
    with ui.grid(columns=2).classes("gap-4 mx-auto"):
        for faq_item in faq_items:
            FAQElementComponent(faq_item.question, faq_item.answer)
    with ui.card().classes("w-5/6 mx-auto"):
        user_faq = ui.textarea("Neue Frage")
        ui.button("Abschicken").on_click(lambda: store_user_faq(user_faq.value))
