import logging
from nicegui import ui, app


from models.controller import (
    get_user_by_id_name,
    get_user_by_account_and_password,
    create_user_account,
)
from localization.language_manager import get_localization, make_localisable


def reload_after(func, *args, **kwargs):
    func(*args, **kwargs)
    content.refresh()


@ui.refreshable
def content(lang: str = "en", **kwargs):
    if user_id := app.storage.user.get("user_id"):
        if get_user_by_id_name(user_id):
            ui.navigate.to(f"/welcome?lang={lang}")
            ui.notify(get_localization("already_logged_in", lang), type="warning")
            return
    with ui.card().classes("lg:w-1/2 mx-auto"):
        with ui.tabs() as tabs:
            login_tab = ui.tab("Login")
            register_tab = ui.tab("Register")
            sso_tab = ui.tab("SSO")
            make_localisable(login_tab, key="login", language=lang)
            make_localisable(register_tab, key="register", language=lang)
        with ui.tab_panels(tabs, value=login_tab).classes("w-full m-2"):
            with ui.tab_panel(login_tab):
                login_form(lang)
            with ui.tab_panel(register_tab):
                register_form(lang)
            with ui.tab_panel(sso_tab):
                ui.button(
                    "Log/Sign in via Google",
                    on_click=lambda: ui.navigate.to("/google/login"),
                )
                ui.button(
                    "Log/Sign in via Discord",
                    on_click=lambda: ui.navigate.to("/discord/login"),
                )


def login_form(lang: str):
    account_input = ui.input(
        "Account Name", validation={"Too short": lambda value: len(value) >= 5}
    ).classes("w-full")
    password_input = ui.input("PW", password=True, password_toggle_button=True).classes(
        "w-full"
    )
    make_localisable(password_input, key="password", language=lang)
    make_localisable(
        ui.button("Login").on_click(
            lambda: login(account_input.value, password_input.value, lang)
        ),
        key="login",
        language=lang,
    )


def login(account: str, password: str, lang: str):
    if user := get_user_by_account_and_password(account, password):
        app.storage.user["user_id"] = user.id_name
        ui.navigate.to("/welcome")
    else:
        ui.notify(get_localization("login_failed", lang), type="negative")


def register_form(lang: str):
    account_input = ui.input(
        "Account Name", validation={"Too short": lambda value: len(value) >= 5}
    ).classes("w-full")
    make_localisable(
        ui.label().classes("text-xs text-gray-500"),
        key="account_name_hint",
        language=lang,
    )
    password_input = ui.input(
        "PW",
        password=True,
        validation={
            get_localization("pw_too_short", language=lang): lambda value: len(value)
            >= 8
        },
    ).classes("w-full")
    confirm_input = ui.input(
        "PW",
        password=True,
        validation={
            get_localization("pw_too_short", language=lang): lambda value: len(value)
            >= 8
        },
    ).classes("w-full")
    make_localisable(password_input, key="password", language=lang)
    make_localisable(confirm_input, key="password_confirm", language=lang)
    make_localisable(
        ui.button("Register").on_click(
            lambda: register(
                account_input.value, password_input.value, confirm_input.value, lang
            )
        ),
        key="register",
        language=lang,
    )


def register(account: str, password: str, confirm: str, lang: str):
    if password != confirm:
        ui.notify(get_localization("passwords_do_not_match", lang), type="negative")
        return
    try:
        if create_user_account(account, password):
            content.refresh()
            ui.notify(get_localization("account_created", lang), type="positive")
            return
    except ValueError as e:
        logging.error(e)
        ui.notify(get_localization("account_name_in_use"), type="negative")
    else:
        ui.notify(get_localization("account_not_created", lang), type="negative")
