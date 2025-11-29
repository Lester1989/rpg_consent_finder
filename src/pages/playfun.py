from nicegui import ui

from components.playfun_plot_component import PlayfunPlot
from controller.playfun_controller import (
    get_playfun_questions,
    store_playfun_result,
    get_playfun_answers_for_user,
    get_playfun_result_by_id,
    update_playfun_answer,
)
from controller.user_controller import (
    get_user_from_storage,
)
from localization.language_manager import get_localization, make_localisable
from models.db_models import (
    PlayFunAnswer,
    PlayFunResult,
    User,
)
from services.session_service import session_storage

SHOW_TAB_STORAGE_KEY = "playfun_tab"


def reload_after(func, *args, **kwargs):
    func(*args, **kwargs)
    ui.navigate.reload()


def content(**kwargs):
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

    with ui.tabs().classes("w-5/6 mx-auto") as tabs:
        question_tab = ui.tab("questions").mark("playfun_questions_tab")
        plot_tab = (
            ui.tab("plot").mark("playfun_plot_tab").on("click", plot_content.refresh)
        )
        make_localisable(question_tab, key="play_fun_statements")
        make_localisable(plot_tab, key="play_fun_plot")

    named_tabs = {"questions": question_tab, "plot": plot_tab}
    show_tab = session_storage.get(SHOW_TAB_STORAGE_KEY, "questions")

    with ui.tab_panels(tabs, value=named_tabs.get(show_tab, question_tab)).classes(
        "w-5/6 mx-auto"
    ) as panels:
        with ui.tab_panel(question_tab):
            question_content(user)
        with ui.tab_panel(plot_tab):
            plot_content(user)
    panels.on_value_change(lambda x: storage_show_tab_and_refresh(x.value))

    if user:
        make_localisable(
            ui.button("Save")
            .on_click(lambda: store_playfun_result(user, construct_ratings(user)))
            .mark("save_button"),
            key="save",
        )


def question_content(user: User):
    statements = get_playfun_questions()
    if user is None:
        ui.markdown(get_localization("please_log_in_to_store_playfun"))
        return

    playfun_result = get_playfun_result_by_id(user)
    answers_by_question_id = {
        answer.question_id: answer for answer in get_playfun_answers_for_user(user)
    }
    ui.markdown(get_localization("playfun_questions_introduction")).classes(
        "lg:w-1/2 mx-auto"
    )
    lang = session_storage.get("lang", "en")
    with ui.grid().classes("w-full lg:grid-cols-2 gap-4"):
        for playfun_question in statements:
            with ui.card():
                with ui.row():
                    ui.label(playfun_question.question_local.get_text(lang))
                    # ui.label(
                    #     f"{playfun_question.play_style} {playfun_question.id}"
                    # ).classes("text-xs text-gray-500")
                with ui.row().classes("w-full"):
                    ui.label("❤️").classes("text-lg")
                    ui.space()
                    ui.slider(
                        min=-2,
                        max=2,
                        step=0.25,
                        value=answers_by_question_id.get(
                            playfun_question.id, PlayFunAnswer(rating=0)
                        ).rating,
                    ).on_value_change(
                        lambda e, q=playfun_question: update_playfun_answer(
                            q, e.value, playfun_result
                        )
                    ).props(
                        'selection-color="transparent"',
                    ).props("label").props("reverse").classes("w-3/4").mark(
                        f"slider-{playfun_question.id}"
                    )

                    ui.space()
                    ui.label("🤮").classes("text-lg")


@ui.refreshable
def plot_content(user: User):
    with ui.row().classes("w-full"):
        playfun_result = get_playfun_result_by_id(user) if user else None
        if not playfun_result:
            ui.label(get_localization("no_data"))
            return
        PlayfunPlot({"me": playfun_result})
        ui.markdown(get_localization("playfun_plot_explanation")).classes(
            "xl:w-2/5 w-full text-sm"
        )
        ui.label(f"Top 3: {', '.join(playfun_result.get_top_style(3))}").classes(
            "w-8"
        ).mark("top_styles")


def construct_ratings(user: User) -> PlayFunResult:
    answers: dict[str, dict[int, int]] = session_storage.get("answers", {})
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
    session_storage[SHOW_TAB_STORAGE_KEY] = tab
    plot_content.refresh()
