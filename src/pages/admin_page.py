import os
from nicegui import ui, app

from models.db_models import (
    User,
)
from models.controller import (
    get_all_consent_topics,
    get_all_content_questions,
    get_all_faq_questions,
    get_status,
    get_user_by_id_name,
    remove_content_question,
    remove_faq_question,
    store_content_answer,
    store_faq_answer,
)
from models.seeder import seed_consent_questioneer

ADMINS = os.getenv("ADMINS", "").split(",")


def reload_after(func, *args, **kwargs):
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
        ui.label("Not an admin")
        ui.link("Home", "/home")
        return
    ui.button("Seed ", on_click=lambda: reload_after(seed_consent_questioneer))

    for table, table_count_and_clear_func in get_status().items():
        with ui.row():
            ui.label(f"{table} {table_count_and_clear_func[0]}")
            ui.button("clear", color="red").on_click(
                lambda clear_func=table_count_and_clear_func[1]: reload_after(
                    clear_func
                )
            )
    templates = get_all_consent_topics()
    categories = {
        template.category_id: template.category_local.get_text("de")
        for template in templates
    }
    ui.separator()
    ui.label("Open FAQ")
    with ui.grid().classes("lg:grid-cols-2 grid-cols-1 gap-4"):
        for faq in get_all_faq_questions():
            with ui.expansion(f"{faq.created_at:%Y-%m-%d %H:%M} || {faq.question}"):
                question_input = ui.input("question").classes("w-full")
                answer_input = ui.textarea("answer").classes("w-full")
                ui.button(
                    "add to FAQ",
                    on_click=lambda faq=faq,
                    question_input=question_input,
                    answer_input=answer_input: reload_after(
                        store_faq_answer, question_input.value, answer_input.value, faq
                    ),
                )
                ui.button("delete", color="red").on_click(
                    lambda faq=faq: reload_after(remove_faq_question, faq)
                )
    ui.separator()
    ui.label("Open Content")
    with ui.grid().classes("lg:grid-cols-2 grid-cols-1 gap-4"):
        for content in get_all_content_questions():
            # ui.label(content.created_at)
            # ui.label(content.question)
            with ui.expansion(
                f"{content.created_at:%Y-%m-%d %H:%M} || {content.question}"
            ):
                category_select = ui.select(
                    label="Category", options=categories
                ).classes("w-full")
                topic_input = ui.input("topic").classes("w-full")
                explanation_input = ui.textarea("explanation").classes("w-full")
                ui.button(
                    "add to Content",
                    on_click=lambda category_select=category_select,
                    topic_input=topic_input,
                    explanation_input=explanation_input,
                    content=content: reload_after(
                        store_content_answer,
                        category_select.value,
                        topic_input.value,
                        explanation_input.value,
                        content,
                    ),
                )
                ui.button("delete", color="red").on_click(
                    lambda content=content: reload_after(
                        remove_content_question, content
                    )
                )
