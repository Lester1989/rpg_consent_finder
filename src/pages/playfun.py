from nicegui import app, ui

from components.playfun_plot_component import PlayfunPlot
from controller.playfun_controller import (
    get_playfun_questions,
    store_playfun_result,
)
from controller.user_controller import (
    get_user_from_storage,
)
from localization.language_manager import get_localization, make_localisable
from models.db_models import (
    PlayFunQuestion,
    PlayFunResult,
    User,
)

SHOW_TAB_STORAGE_KEY = "playfun_tab"


def reload_after(func, *args, **kwargs):
    func(*args, **kwargs)
    ui.navigate.reload()


def content(lang: str = "en", **kwargs):
    ui.add_css("""
    .nicegui-markdown h3 {
        font-size: 1.5em;
        font-weight: bold;
    }
    .nicegui-markdown h4 {
        font-size: 1.25em;
    }
    """)

    user: User = get_user_from_storage()
    ensure_answers_in_user_storage()

    with ui.tabs().classes("w-5/6 mx-auto") as tabs:
        question_tab = ui.tab("questions")
        plot_tab = ui.tab("plot")
        make_localisable(question_tab, key="play_fun_statements", language=lang)
        make_localisable(plot_tab, key="play_fun_plot", language=lang)

    named_tabs = {"questions": question_tab, "plot": plot_tab}
    show_tab = app.storage.user.get(SHOW_TAB_STORAGE_KEY, "questions")

    with ui.tab_panels(tabs, value=named_tabs.get(show_tab, question_tab)).classes(
        "w-5/6 mx-auto"
    ) as panels:
        with ui.tab_panel(question_tab):
            question_content(lang)
        with ui.tab_panel(plot_tab):
            plot_content(lang, user)
    panels.on_value_change(lambda x: storage_show_tab_and_refresh(x.value))

    if user:
        make_localisable(
            ui.button("Save").on_click(
                lambda: store_playfun_result(user, construct_ratings(user))
            ),
            key="save",
            language=lang,
        )
    else:
        make_localisable(
            ui.label(),
            key="please_log_in_to_store_playfun",
            language=lang,
        )


def ensure_answers_in_user_storage(statements: list[PlayFunQuestion] = None):
    statements = statements or get_playfun_questions()
    answers: dict[str, dict[str, int]] = app.storage.user.get(
        "answers",
        {statement.play_style: {str(statement.id): 0} for statement in statements},
    )
    for statement in statements:
        if statement.play_style not in answers:
            answers[statement.play_style] = {}
        if str(statement.id) not in answers[statement.play_style]:
            answers[statement.play_style][str(statement.id)] = 0
    app.storage.user["answers"] = answers


def question_content(lang):
    statements = get_playfun_questions()
    ensure_answers_in_user_storage(statements)
    ui.markdown(get_localization("playfun_questions_introduction", lang)).classes(
        "lg:w-1/2 mx-auto"
    )
    with ui.grid().classes("w-full lg:grid-cols-2 gap-4"):
        for playfun_question in statements:
            with ui.card():
                with ui.row():
                    ui.label(playfun_question.question_local.get_text(lang))
                    ui.label(playfun_question.play_style).classes(
                        "text-xs text-gray-500"
                    )
                with ui.row().classes("w-full"):
                    ui.label("❤️").classes("text-lg")
                    ui.space()
                    ui.slider(
                        min=-2,
                        max=2,
                        step=0.25,
                    ).bind_value(
                        app.storage.user.get("answers", {})[
                            playfun_question.play_style
                        ],
                        str(playfun_question.id),
                    ).on_value_change(plot_content.refresh).props(
                        'selection-color="transparent"',
                    ).props("label").props("reverse").classes("w-3/4")
                    ui.space()
                    ui.label("🤮").classes("text-lg")


@ui.refreshable
def plot_content(lang: str, user: User):
    with ui.row().classes("w-full"):
        PlayfunPlot({"me": construct_ratings(user)}, lang=lang)
        ui.markdown(get_localization("playfun_plot_explanation", lang)).classes(
            "xl:w-2/5 w-full text-sm"
        )


def construct_ratings(user: User):
    answers: dict[str, dict[int, int]] = app.storage.user.get("answers", {})
    weights = {
        str(statement.id): statement.weight for statement in get_playfun_questions()
    }
    ratings = {
        play_style: sum(
            val * weights.get(id, 1) or 0
            for id, val in answers.get(play_style, {}).items()
        )
        / len(answers)
        for play_style in answers
    }
    return PlayFunResult(
        user=user or None,
        user_id=user.id if user else None,
        **{f"{play_style}_rating": value for play_style, value in ratings.items()},
    )


def storage_show_tab_and_refresh(tab: str):
    app.storage.user[SHOW_TAB_STORAGE_KEY] = tab
    plot_content.refresh()
