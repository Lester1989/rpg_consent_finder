import logging
import os

from nicegui import app, ui

from components.content_question_component import ContentQuestionComponent
from controller.admin_controller import (
    get_all_content_questions,
    get_all_faq_questions,
    get_status,
    remove_faq_question,
    store_content_answer,
    store_faq_answer,
    update_localized_text,
)
from controller.sheet_controller import (
    get_all_consent_topics,
    get_all_custom_entries,
)
from controller.user_controller import get_user_by_id_name
from controller.util_controller import (
    get_all_localized_texts,
)
from models.db_models import (
    User,
)
from models.seeder import seed_consent_questioneer

ADMINS = os.getenv("ADMINS", "").split(",")


SHOW_TAB_STORAGE_KEY = "admin_show_tab"


def reload_after(func, *args, **kwargs):
    logging.getLogger("content_consent_finder").debug(
        f"Reloading after {func.__name__}"
    )
    func(*args, **kwargs)
    content.refresh()


@ui.refreshable
def content(**kwargs):
    user: User = get_user_by_id_name(app.storage.user.get("user_id"))
    if not user:
        ui.label("No user found")
        return
    user_id = app.storage.user.get("user_id")
    if user_id not in ADMINS:
        logging.getLogger("content_consent_finder").debug(
            f"User {user_id} is not an admin"
        )
        ui.label("Not an admin")
        ui.link("Home", "/home")
        return
    with ui.tabs().classes("w-full") as tabs:
        db_tab = ui.tab("DB").classes("w-full")
        faq_tab = ui.tab("FAQ").classes("w-full")
        trigger_tab = ui.tab("Contents").classes("w-full")
        local_text_tab = ui.tab("Localized Texts").classes("w-full")

    named_tabs = {
        "DB": db_tab,
        "FAQ": faq_tab,
        "Contents": trigger_tab,
        "Localized Texts": local_text_tab,
    }
    show_tab = app.storage.user.get(SHOW_TAB_STORAGE_KEY, "DB")
    with ui.tab_panels(tabs, value=named_tabs.get(show_tab, db_tab)).classes(
        "w-full"
    ) as panels:
        with ui.tab_panel(db_tab).classes("w-full"):
            db_content()
        with ui.tab_panel(faq_tab).classes("w-full"):
            faq_content()
        with ui.tab_panel(trigger_tab).classes("w-full"):
            trigger_content()
        with ui.tab_panel(local_text_tab).classes("w-full"):
            local_text_content()

    panels.on_value_change(lambda x: storage_show_tab_and_refresh(x.value))


def storage_show_tab_and_refresh(tab: str):
    # tab = tab.lower()
    app.storage.user[SHOW_TAB_STORAGE_KEY] = tab
    logging.getLogger("content_consent_finder").debug(
        f"storage_show_tab_and_refresh {tab}"
    )


def local_text_content():
    ui.label("Localized Texts")
    with ui.grid(columns="auto 1fr 1fr auto").classes("w-full"):
        ui.label("ID").classes("lg:text-xl text-lg w-1/6")
        ui.label("DE").classes("lg:text-xl text-lg w-2/3")
        ui.label("EN").classes("lg:text-xl text-lg w-2/3")
        ui.label("Action").classes("lg:text-xl text-lg w-1/6")
        for value in sorted(
            get_all_localized_texts().values(), key=lambda x: x.text_de
        ):
            ui.label(value.id)
            ui.textarea().classes("w-full").bind_value(value, "text_de")
            ui.textarea().classes("w-full").bind_value(value, "text_en")
            ui.button(
                "save",
                on_click=lambda text=value: reload_after(update_localized_text, text),
            )


def db_content():
    ui.label("DB Administation")
    ui.button("Seed ", on_click=lambda: reload_after(seed_consent_questioneer))
    with ui.grid().classes("lg:grid-cols-4 grid-cols-2 gap-4 w-full lg:p-4"):
        for table, table_count_and_clear_func in get_status().items():
            with ui.card(), ui.row():
                double_check = ui.checkbox("")
                clear_button = ui.button("clear", color="red").on_click(
                    lambda clear_func=table_count_and_clear_func[1]: reload_after(
                        clear_func
                    )
                )
                clear_button.set_enabled(False)
                double_check.bind_value(clear_button, "enabled")
                ui.label(f"{table} {table_count_and_clear_func[0]}")


def trigger_content():
    templates = get_all_consent_topics()
    categories = {
        template.category_id: template.category_local.get_text("de")
        for template in templates
    }
    open_questions = get_all_content_questions()
    ui.label(f"Open Content Questions: {len(open_questions)}")
    if open_questions:
        with ui.grid().classes("lg:grid-cols-2 grid-cols-1 gap-4 w-full lg:p-4"):
            for content_question in open_questions:
                ContentQuestionComponent(content_question, content.refresh)
        ui.separator()
    custom_entries = get_all_custom_entries()
    ui.label(f"Custom Entries: {len(custom_entries)}")
    with ui.grid().classes("lg:grid-cols-4 grid-cols-2 gap-4 w-full lg:p-4"):
        for custom_entry in sorted(custom_entries, key=lambda x: x.content.lower()):
            with ui.card():
                ui.label(custom_entry.content)
    ui.label("New Content")
    new_category_select = ui.select(label="Category", options=categories).classes(
        "w-full"
    )
    new_topic_input = ui.input("topic").classes("w-full")
    new_explanation_input = ui.textarea("explanation").classes("w-full")
    ui.button(
        "add to Content",
        on_click=lambda category_select=new_category_select,
        topic_input=new_topic_input,
        explanation_input=new_explanation_input: reload_after(
            store_content_answer,
            category_select.value,
            topic_input.value,
            explanation_input.value,
        ),
    )


def faq_content():
    ui.label("Open FAQ")
    with ui.grid().classes("lg:grid-cols-2 grid-cols-1 gap-4 w-full lg:p-4"):
        for faq in get_all_faq_questions():
            with ui.expansion(f"{faq.created_at:%Y-%m-%d %H:%M} || {faq.question}"):
                question_input_de = ui.input("question_de").classes("w-full")
                question_input_en = ui.input("question_en").classes("w-full")
                answer_input_de = ui.textarea("answer_de").classes("w-full")
                answer_input_en = ui.textarea("answer_en").classes("w-full")
                ui.button(
                    "add to FAQ",
                    on_click=lambda faq=faq,
                    question_input_de=question_input_de,
                    question_input_en=question_input_en,
                    answer_input_de=answer_input_de,
                    answer_input_en=answer_input_en: reload_after(
                        store_faq_answer,
                        question_input_de.value,
                        question_input_en.value,
                        answer_input_de.value,
                        answer_input_en.value,
                        faq,
                    ),
                )
                ui.button("delete", color="red").on_click(
                    lambda faq=faq: reload_after(remove_faq_question, faq)
                )
    ui.separator()
    ui.label("New FAQ")
    new_question_input_de = ui.input("question_de").classes("w-full")
    new_question_input_en = ui.input("question_en").classes("w-full")
    new_answer_input_de = ui.textarea("answer_de").classes("w-full")
    new_answer_input_en = ui.textarea("answer_en").classes("w-full")
    ui.button(
        "add to FAQ",
        on_click=lambda question_input_de=new_question_input_de,
        question_input_en=new_question_input_en,
        answer_input_de=new_answer_input_de,
        answer_input_en=new_answer_input_en: reload_after(
            store_faq_answer,
            question_input_de.value,
            question_input_en.value,
            answer_input_de.value,
            answer_input_en.value,
        ),
    )
