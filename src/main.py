import io
import logging
import random
import string
import traceback
from pathlib import Path
from time import perf_counter
from fastapi import Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi_sso.sso.discord import DiscordSSO
from fastapi_sso.sso.google import GoogleSSO
from nicegui import Client, app, ui
from nicegui.page import page

from a_logger_setup import LOGGER_NAME, configure_logging
from controller.user_controller import (
    get_user_by_id_name,
    get_or_create_sso_user,
    update_user,
)
from components.layout import (
    page_frame,
    safe_refresh_header,
)
from localization.language_manager import make_localisable
from models.db_models import User
from models.seeder import seed_consent_questioneer
from pages.admin_page import content as admin_page_content
from pages.content_trigger_view import content as content_trigger_view
from pages.dsgvo import dsgvo_html
from pages.faq_page import content as faq_content
from pages.group_overview import content as group_overview_content
from pages.home import content as home_content
from pages.login_page import content as login_content
from pages.playfun import content as playfun_content
from pages.public_sheet import content as public_sheet_content
from pages.sheet_page import content as sheet_content
from pages.news_page import content as news_content
from public_share_qr import generate_sheet_share_qr_code
from settings import Settings, get_settings
from services.session_service import (
    begin_user_session,
    end_user_session,
    ensure_session_middleware,
    get_current_user_id,
    get_session_stats,
    set_metrics_recorder,
)
from telemetry import setup_metrics

APP_START_TIME = perf_counter()

print("main module imported", __name__)
settings = get_settings()
ensure_session_middleware()
configure_logging(settings.log_level)
LOGGER = logging.getLogger(LOGGER_NAME)

if request_metrics := setup_metrics(settings):
    request_metrics.set_session_stats_provider(get_session_stats)
    set_metrics_recorder(request_metrics)
    app.middleware("http")(request_metrics.middleware())


google_sso = GoogleSSO(
    settings.google_client_id,
    settings.google_client_secret,
    redirect_uri=f"{settings.base_url}/google/callback",
)


discord_sso = DiscordSSO(
    settings.discord_client_id,
    settings.discord_client_secret,
    redirect_uri=f"{settings.base_url}/discord/callback",
    allow_insecure_http=settings.discord_allow_insecure_http,
)


def update_user_and_go_home(new_user: User):
    update_user(new_user)
    ui.navigate.to("/home")


@app.get("/healthcheck_and_heartbeat")
def healthcheck_and_heartbeat(request: Request):
    LOGGER.debug("healthcheck_and_heartbeat")
    return JSONResponse({"status": "ok"})


@app.get("/dsgvo")
def dsgvo():
    return HTMLResponse(content=dsgvo_html, media_type="text/html")


@app.exception_handler(500)
async def exception_handler_500(request: Request, exception: Exception) -> Response:
    stack_trace = traceback.format_exc()
    msg_to_user = f"**{exception}**\n\nStack trace: \n<pre>{stack_trace}"
    with Client(page(""), request=request) as client:
        page_frame("error")
        with ui.card().classes("p-4 mx-auto border-red-800 rounded-lg"):
            ui.label("Internal Application Error").classes("text-2xl").mark(
                "error_label"
            )
            ui.markdown(msg_to_user)

    return client.build_response(request, 500)


def root():
    page_frame(ui.context.client.request.url.path[1:])
    ui.sub_pages(
        {
            "/": empty_uri_redirect,
            "/impressum": impressum_page,
            "/login": login_content,
            "/news": news_content,
            "/faq": faq_content,
            "/content_trigger": content_trigger_view,
            "/home": home_content,
            "/welcome": welcome_page,
            "/admin": admin_page_content,
            "/logout": logout_page,
            "/playstyle": playfun_content,
            "/consent/{share_id}/{sheet_id}": public_sheet_content,
            "/consentsheet/{questioneer_id}": sheet_content,
            "/consentsheet": sheet_content,
            "/groupconsent": group_overview_content,
            "/groupconsent/{group_name_id}": group_overview_content,
            "/google/login": google_login_redirect,
            "/google/callback": google_callback_redirect,
            "/discord/login": discord_login_redirect,
            "/discord/callback": discord_callback_redirect,
        }
    ).classes("m-0 p-0 w-full")


def impressum_page():
    ui.html(
        """
    <h1>Impressum</h1>
    <p>Lukas Jaspaert
            <br />
    J&uuml;rgingsm&uuml;hle 9
            <br />
    33739 Bielefeld</p>

    <h2>Kontakt</h2>
    <p>Telefon: 015150236860
            <br />
    E-Mail: l.ester@gmx.de
            </p>""",
        sanitize=False,
    )


def empty_uri_redirect():
    return ui.navigate.to("/welcome")


async def welcome_page():
    if user_id := get_current_user_id():
        user: User = get_user_by_id_name(user_id)
        LOGGER.debug("welcoming %s", user)
        if not user or not user.nickname:
            ui.label("Welcome, yet unknown user").classes("text-2xl")
            new_user = user or User(
                id_name=user_id,
                nickname="",
            )
            nick_input = ui.input("Your name").bind_value(new_user, "nickname")
            save_nick_button = ui.button(
                "Save", on_click=lambda: update_user_and_go_home(new_user)
            )
            nick_input.mark("welcome_nickname")
            save_nick_button.mark("welcome_save")
        else:
            ui.navigate.to("/home")
            await safe_refresh_header(current_page="home")
    else:
        LOGGER.debug("no user_id")
        with ui.card().classes("p-4 mx-auto"):
            make_localisable(
                ui.label("Welcome, please sign in").classes("text-2xl"),
                key="welcome_signin",
            )
            ui.button(
                "Log/Sign in via Google",
                on_click=lambda: ui.navigate.to("/google/login"),
            )
            ui.button(
                "Log/Sign in via Discord",
                on_click=lambda: ui.navigate.to("/discord/login"),
            )
            local_sign_in_button = ui.button(
                "Log/Sign in via Account and Password",
                on_click=lambda: ui.navigate.to("/login"),
            )
            local_sign_in_button.mark("local_sign_in_button")


def logout_page():
    LOGGER.debug("logout")
    end_user_session()
    return ui.navigate.to("/home")


async def google_login_redirect():
    async with google_sso:
        redirect_response = await google_sso.get_login_redirect()
        ui.navigate.to(redirect_response.headers["location"])


@ui.page("/google/callback")
async def google_callback_redirect(request: Request):
    async with google_sso:
        user = await google_sso.verify_and_process(request)
    LOGGER.debug("google %s", user)
    linked_user = get_or_create_sso_user(
        provider="google",
        account_id=user.id,
        display_name=getattr(user, "name", ""),
        email=getattr(user, "email", None),
    )
    begin_user_session(linked_user.id_name)
    return ui.navigate.to("/welcome")


@ui.page("/discord/callback")
async def discord_callback_redirect(request: Request):
    LOGGER.info("discord callback")
    async with discord_sso:
        user = await discord_sso.verify_and_process(request)
    LOGGER.debug("discord %s", user)
    linked_user = get_or_create_sso_user(
        provider="discord",
        account_id=user.id,
        display_name=getattr(user, "username", ""),
    )
    begin_user_session(linked_user.id_name)
    return ui.navigate.to("/welcome")


async def discord_login_redirect():
    LOGGER.info("discord login")
    async with discord_sso:
        redirect_response = await discord_sso.get_login_redirect()
        ui.navigate.to(redirect_response.headers["location"])


@app.get("/api/qr")
def qr(share_id: str, sheet_id: str):
    img_byte_arr = io.BytesIO()
    generate_sheet_share_qr_code(share_id, sheet_id).save(img_byte_arr, format="PNG")
    return Response(content=img_byte_arr.getvalue(), media_type="image/png")


def redact_string(s: str) -> str:
    if s == "-default-":
        return s
    return "!!NULL!!" if s is None else f"<REDACTED {len(s)}>"


def startup_message(current_settings: Settings):
    LOGGER.info("========== Starting Lester's Content Pact ==========")
    LOGGER.info("DB_CONNECTION_STRING: %s", current_settings.db_connection_string)
    LOGGER.info("LOGLEVEL: %s", current_settings.log_level)
    LOGGER.info("GOOGLE_CLIENT_ID: %s", current_settings.google_client_id)
    LOGGER.info(
        "GOOGLE_CLIENT_SECRET: %s",
        redact_string(current_settings.google_client_secret),
    )
    LOGGER.info("DISCORD_CLIENT_ID: %s", current_settings.discord_client_id)
    LOGGER.info(
        "DISCORD_CLIENT_SECRET: %s",
        redact_string(current_settings.discord_client_secret),
    )
    LOGGER.info("BASE_URL: %s", current_settings.base_url)
    LOGGER.info("ADMINS: %s", ",".join(current_settings.admins) or "<none>")
    LOGGER.info("SEED_ON_STARTUP: %s", current_settings.seed_on_startup)
    LOGGER.info("RELOAD: %s", current_settings.reload)
    LOGGER.info(
        "STORAGE_SECRET: %s",
        redact_string(current_settings.storage_secret),
    )
    LOGGER.info(
        "DISCORD_ALLOW_INSECURE_HTTP: %s", current_settings.discord_allow_insecure_http
    )
    LOGGER.info("PORT: %s", current_settings.port)
    LOGGER.info("====================================================")


if __name__ in {"__main__", "__mp_main__"}:
    if settings.seed_on_startup:
        seed_consent_questioneer()
    startup_message(settings)
    if request_metrics:
        startup_duration_ms = (perf_counter() - APP_START_TIME) * 1000
        request_metrics.record_startup_duration(startup_duration_ms)
    storage_secret = settings.storage_secret or "".join(
        random.choices(string.ascii_letters + string.digits, k=32)
    )
    ui.run(
        root=root,
        title="Lester's Content Pact",
        favicon=Path("src/favicon.ico"),
        storage_secret=storage_secret,
        reload=settings.reload,
        port=settings.port,
    )
