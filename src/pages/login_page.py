import logging

from nicegui import app, ui

from controller.user_controller import (
    create_user_account,
    get_user_by_account_and_password,
    get_user_by_id_name,
)
from localization.language_manager import get_localization, make_localisable


def content(**kwargs):
    logging.getLogger("content_consent_finder").debug("showing login page")
    if user_id := app.storage.user.get("user_id"):
        if get_user_by_id_name(user_id):
            ui.navigate.to("/welcome")
            ui.notify(get_localization("already_logged_in"), type="warning")
            return
    with ui.card().classes("lg:w-1/2 mx-auto"):
        with ui.tabs() as tabs:
            login_tab = ui.tab("Login")
            register_tab = ui.tab("Register")
            sso_tab = ui.tab("SSO")
            make_localisable(login_tab, key="login")
            make_localisable(register_tab, key="register")
            login_tab.mark("login_tab")
            register_tab.mark("register_tab")

        with ui.tab_panels(tabs, value=login_tab).classes("w-full m-2"):
            with ui.tab_panel(login_tab):
                login_form()
            with ui.tab_panel(register_tab):
                register_form()
            with ui.tab_panel(sso_tab):
                ui.button(
                    "Log/Sign in via Google",
                    on_click=lambda: ui.navigate.to("/google/login"),
                )
                ui.button(
                    "Log/Sign in via Discord",
                    on_click=lambda: ui.navigate.to("/discord/login"),
                )


def login_form():
    account_input = ui.input(
        "Account Name", validation={"Too short": lambda value: len(value) >= 5}
    ).classes("w-full")
    password_input = ui.input("PW", password=True, password_toggle_button=True).classes(
        "w-full"
    )
    login_button = ui.button("Login").on_click(
        lambda: login(account_input.value, password_input.value)
    )
    account_input.mark("login_account")
    password_input.mark("login_pw")
    login_button.mark("login_button")
    make_localisable(password_input, key="password")
    make_localisable(
        login_button,
        key="login",
    )


def login(account: str, password: str):
    if user := get_user_by_account_and_password(account, password):
        app.storage.user["user_id"] = user.id_name
        ui.navigate.to("/welcome")
    else:
        logging.getLogger("content_consent_finder").warning(
            f"Failed login attempt for {account} and <redact Passwort {len(password)}>"
        )
        ui.notify(get_localization("login_failed"), type="negative")


def register_form():
    make_localisable(ui.label(), key="register_hint")
    account_input = ui.input(
        "Account Name", validation={"Too short": lambda value: len(value) >= 5}
    ).classes("w-full")
    make_localisable(
        ui.label().classes("text-xs text-gray-500"),
        key="account_name_hint",
    )
    password_input = ui.input(
        "PW",
        password=True,
        validation={get_localization("pw_too_short"): lambda value: len(value) >= 8},
    ).classes("w-full")
    confirm_input = ui.input(
        "PW",
        password=True,
        validation={get_localization("pw_too_short"): lambda value: len(value) >= 8},
    ).classes("w-full")
    account_input.mark("register_account")
    password_input.mark("register_pw")
    confirm_input.mark("register_pw_confirm")
    make_localisable(password_input, key="password")
    make_localisable(confirm_input, key="password_confirm")
    register_button = ui.button("Register").on_click(
        lambda: register(account_input.value, password_input.value, confirm_input.value)
    )
    register_button.mark("register_button")
    make_localisable(
        register_button,
        key="register",
    )


def register(account: str, password: str, confirm: str):
    if password != confirm:
        ui.notify(get_localization("passwords_do_not_match"), type="negative")
        return
    try:
        if create_user_account(account, password):
            ui.navigate.reload()
            ui.notify(get_localization("account_created"), type="positive")
            return
    except ValueError as e:
        logging.getLogger("content_consent_finder").error(e)
        ui.notify(get_localization("account_name_in_use"), type="negative")
    else:
        ui.notify(get_localization("account_not_created"), type="negative")
