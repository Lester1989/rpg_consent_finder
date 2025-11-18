import io
import logging
import random
import string
import traceback
from pathlib import Path

from fastapi import Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi_sso.sso.discord import DiscordSSO
from fastapi_sso.sso.google import GoogleSSO
from nicegui import Client, app, ui
from nicegui.page import page

from a_logger_setup import LOGGER_NAME, configure_logging
from controller.user_controller import (
    get_user_by_id_name,
    get_user_from_storage,
    update_user,
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

settings = get_settings()
configure_logging(settings.log_level)
LOGGER = logging.getLogger(LOGGER_NAME)


project_version = Path("src/version.txt").read_text().strip()


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


def set_language(lang: str):
    # app.storage.user.set("lang", lang)
    app.storage.user["lang"] = lang
    ui.navigate.reload()


def page_header(current_page: str = None):
    link_classes = "text-lg lg:text-xl text-white hover:text-gray-300 no-underline bg-gray-600 p-1 lg:p-2 rounded"
    highlight = " shadow-md shadow-yellow-500"
    with ui.row().classes("m-0 w-full bg-gray-800 text-white p-2"):
        with ui.column(align_items="start").classes("gap-0 p-0 m-0"):
            ui.label("Lester's Content Pact").classes("text-md lg:text-2xl p-0 m-0")
            ui.label(project_version).classes("text-xs text-gray-500 p-0 m-0")
        ui.space()
        if user_id := app.storage.user.get("user_id"):
            user: User = get_user_by_id_name(user_id)
            if not user and current_page in {"home", "admin"}:
                ui.navigate.to("/welcome")
                return
            ui.label(f"Hi {user.nickname if user else ''}!").classes(
                "text-md lg:text-xl mt-1"
            )

            user = get_user_from_storage()
            LOGGER.info("User: %s", user)
        else:
            user = None
        ui.space()
        if user:
            home_link = ui.link("Home", "/home").classes(
                link_classes + (highlight if current_page == "home" else "")
            )
            home_link.mark("home_link home_button")
        ui.link("News", "/news").classes(
            link_classes + (highlight if current_page == "news" else "")
        )
        ui.link("Contents", "/content_trigger").classes(
            link_classes + (highlight if current_page == "content_trigger" else "")
        )
        ui.link("FAQ", "/faq").classes(
            link_classes + (highlight if current_page == "faq" else "")
        )
        ui.link("Playstyle", "/playstyle").classes(
            link_classes + (highlight if current_page == "playstyle" else "")
        )
        if user_id in settings.admins:
            ui.link("Admin", "/admin").classes(
                link_classes + (highlight if current_page == "admin" else "")
            )
        ui.space()
        lang = app.storage.user.get("lang", "en")
        if lang == "de":
            ui.button("EN", on_click=lambda: set_language("en")).classes(link_classes)
        else:
            ui.button("DE", on_click=lambda: set_language("de")).classes(link_classes)

        dark = ui.dark_mode(value=True)
        ui.switch("Dark").bind_value(dark)
        if user_id:
            ui.link("Logout", "/logout").classes(
                link_classes.replace("bg-gray-600", "bg-red-800")
            ).mark("logout_btn")
        else:
            ui.link("Login", "/login").classes(
                link_classes
                + (highlight if current_page in {"welcome", "login"} else "")
            ).mark("login_nav_button")


def page_frame(current_page=None):
    page_header(current_page=current_page)
    page_footer()


def page_footer():
    impressum_h1_classes = "text-lg lg:text-xl"
    impressum_p_classes = "text-sm lg:text-md"
    with ui.footer(fixed=False).classes("m-0 w-full bg-gray-800 text-white p-4"):
        with ui.row():
            with ui.column():
                ui.link("Impressum", "/impressum").classes(
                    "text-lg lg:text-xl text-white hover:text-gray-300 no-underline bg-gray-600 p-1 lg:p-2 rounded"
                )
                ui.link("DSGVO", "/dsgvo").classes(
                    "text-lg lg:text-xl text-white hover:text-gray-300 no-underline bg-gray-600 p-1 lg:p-2 rounded"
                )
            with ui.column():
                ui.label("Impressum").classes(impressum_h1_classes)
                ui.label("Lukas Jaspaert").classes(impressum_p_classes)
                ui.label("Jürgingsmühle 9").classes(impressum_p_classes)
                ui.label("33739 Bielefeld").classes(impressum_p_classes)
            with ui.column():
                ui.label("Kontakt").classes(impressum_h1_classes)
                ui.label("Telefon: 015150236860").classes(impressum_p_classes)
                ui.label("E-Mail: l.ester@gmx.de").classes(impressum_p_classes)


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


def welcome_page():
    if user_id := app.storage.user.get("user_id"):
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
    app.storage.user["user_id"] = None
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
    app.storage.user["user_id"] = f"google-{user.id}"
    return ui.navigate.to("/welcome")


@ui.page("/discord/callback")
async def discord_callback_redirect(request: Request):
    LOGGER.info("discord callback")
    async with discord_sso:
        user = await discord_sso.verify_and_process(request)
    LOGGER.debug("discord %s", user)
    app.storage.user["user_id"] = f"discord-{user.id}"
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
