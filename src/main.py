import io
import logging
import os
import random
import string
import traceback
from pathlib import Path

from fastapi import Depends, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi_sso.sso.discord import DiscordSSO
from fastapi_sso.sso.google import GoogleSSO
from nicegui import Client, app, ui
from nicegui.page import page

import a_logger_setup
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
from pages.login_page import content as login_page_content
from pages.playfun import content as playfun_content
from pages.public_sheet import content as public_sheet_content
from pages.sheet_page import content as sheet_content
from pages.news_page import content as news_content
from public_share_qr import generate_sheet_share_qr_code

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "...")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "...")
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "...")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "...")

BASE_URL = os.getenv("BASE_URL", f"http://localhost:{os.getenv('PORT', 8080)}")

SEED_ON_STARTUP = os.getenv("SEED_ON_STARTUP", "False").lower() == "true"
if SEED_ON_STARTUP:
    seed_consent_questioneer()

RELOAD = os.getenv("RELOAD", "False").lower() == "true"

ADMINS = os.getenv("ADMINS", "").split(",")

project_version = Path("src/version.txt").read_text().strip()


def get_google_sso() -> GoogleSSO:
    return GoogleSSO(
        GOOGLE_CLIENT_ID,
        GOOGLE_CLIENT_SECRET,
        redirect_uri=f"{BASE_URL}/google/callback",
    )


def get_discord_sso() -> DiscordSSO:
    return DiscordSSO(
        DISCORD_CLIENT_ID,
        DISCORD_CLIENT_SECRET,
        redirect_uri=f"{BASE_URL}/discord/callback",
        allow_insecure_http=True,
    )


def header(current_page=None, lang: str = "en"):
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
                ui.navigate.to(f"/welcome?lang={lang}")
                return
            ui.label(f"Hi {user.nickname if user else ''}!").classes(
                "text-md lg:text-xl mt-1"
            )

            user = get_user_from_storage()
            logging.getLogger("content_consent_finder").info(f"User: {user}")
        else:
            user = None
        ui.space()
        if user:
            home_link = ui.link("Home", f"/home?lang={lang}").classes(
                link_classes + (highlight if current_page == "home" else "")
            )
            home_link.mark("home_link")
        ui.link("News", f"/news?lang={lang}").classes(
            link_classes + (highlight if current_page == "news" else "")
        )
        ui.link("Contents", f"/content_trigger?lang={lang}").classes(
            link_classes + (highlight if current_page == "content_trigger" else "")
        )
        ui.link("FAQ", f"/faq?lang={lang}").classes(
            link_classes + (highlight if current_page == "faq" else "")
        )
        ui.link("Playstyle", f"/playstyle?lang={lang}").classes(
            link_classes + (highlight if current_page == "playstyle" else "")
        )
        if user_id in ADMINS:
            ui.link("Admin", f"/admin?lang={lang}").classes(
                link_classes + (highlight if current_page == "admin" else "")
            )
        ui.space()
        if lang == "de":
            ui.link("EN", f"/{current_page}?lang=en").classes(link_classes)
        else:
            ui.link("DE", f"/{current_page}?lang=de").classes(link_classes)

        dark = ui.dark_mode(value=True)
        ui.switch("Dark").bind_value(dark)
        if user_id:
            ui.link("Logout", "/logout").classes(
                link_classes.replace("bg-gray-600", "bg-red-800")
            ).mark("logout_btn")
        else:
            ui.link("Login", f"/welcome?lang={lang}").classes(
                link_classes
                + (highlight if current_page in {"welcome", "login"} else "")
            )
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


def update_user_and_go_home(new_user: User, lang: str = "en"):
    update_user(new_user)
    ui.navigate.to(f"/home?lang={lang}")


@app.get("/healthcheck_and_heartbeat")
def healthcheck_and_heartbeat(request: Request):
    logging.getLogger(a_logger_setup.LOGGER_NAME).debug("healthcheck_and_heartbeat")
    return JSONResponse({"status": "ok"})


@app.get("/dsgvo")
def dsgvo():
    return HTMLResponse(content=dsgvo_html, media_type="text/html")


@app.exception_handler(404)
async def exception_handler_404(request: Request, exception: Exception) -> Response:
    with Client(page(""), request=request) as client:
        language = request.query_params.get("lang", "en")
        header("notfound", lang=language)
        ui.label("Sorry, this page does not exist").classes(
            "text-2xl text-center mt-4 mx-auto"
        ).mark("notfound_label")
    return client.build_response(request, 404)


@app.exception_handler(500)
async def exception_handler_500(request: Request, exception: Exception) -> Response:
    stack_trace = traceback.format_exc()
    msg_to_user = f"**{exception}**\n\nStack trace: \n<pre>{stack_trace}"
    with Client(page(""), request=request) as client:
        language = request.query_params.get("lang", "en")
        header("error", lang=language)
        with ui.card().classes("p-4 mx-auto border-red-800 rounded-lg"):
            ui.label("Internal Application Error").classes("text-2xl").mark(
                "error_label"
            )
            ui.markdown(msg_to_user)

    return client.build_response(request, 500)


def startup():
    @ui.page("/impressum")
    def impressum_page(lang: str = "en"):
        header("impressum", lang)
        ui.html("""
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
                </p>""")

    @ui.page("/")
    def empty_uri(lang: str = "en"):
        return ui.navigate.to(f"/welcome?lang={lang}")

    @ui.page("/login")
    def login(lang: str = "en"):
        header("login", lang)
        login_page_content(lang=lang)

    @ui.page("/news")
    def news(lang: str = "en"):
        header("news", lang)
        news_content(lang=lang)

    @ui.page("/faq")
    def faq(lang: str = "en"):
        header("faq", lang or "en")
        faq_content(lang or "en")

    @ui.page("/content_trigger")
    def content_trigger(lang: str = "en"):
        header("content_trigger", lang or "en")
        content_trigger_view(lang=lang or "en")

    @ui.page("/home")
    def home(lang: str = "en"):
        header("home", lang or "en")
        home_content(lang=lang or "en")

    @ui.page("/welcome")
    def welcome(lang: str = "en"):
        header("welcome", lang or "en")
        if user_id := app.storage.user.get("user_id"):
            user: User = get_user_by_id_name(user_id)
            logging.getLogger("content_consent_finder").debug(f"welcoming {user}")
            if not user or not user.nickname:
                ui.label("Welcome, yet unknown user").classes("text-2xl")
                new_user = user or User(
                    id_name=user_id,
                    nickname="",
                )
                nick_input = ui.input("Your name").bind_value(new_user, "nickname")
                save_nick_button = ui.button(
                    "Save", on_click=lambda: update_user_and_go_home(new_user, lang)
                )
                nick_input.mark("welcome_nickname")
                save_nick_button.mark("welcome_save")
            else:
                ui.navigate.to("/home")
        else:
            logging.getLogger("content_consent_finder").debug("no user_id")
            with ui.card().classes("p-4 mx-auto"):
                make_localisable(
                    ui.label("Welcome, please sign in").classes("text-2xl"),
                    key="welcome_signin",
                    language=lang,
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

    @ui.page("/admin")
    def admin(lang: str = "en"):
        header("admin", lang)
        admin_page_content()

    @ui.page("/logout")
    def logout(lang: str = "en"):
        logging.getLogger("content_consent_finder").debug("logout")
        app.storage.user["user_id"] = None
        return ui.navigate.to(f"/home?lang={lang}")

    @ui.page("/playstyle")
    def playstyle(lang: str = "en"):
        header("playstyle", lang)
        playfun_content(lang=lang)

    @ui.page("/consent/{share_id}/{sheet_id}")
    def public_sheet(share_id: str, sheet_id: str, lang: str = None):
        header(f"consent/{share_id}/{sheet_id}", lang or "en")
        public_sheet_content(lang=lang or "en", share_id=share_id, sheet_id=sheet_id)

    @ui.page("/consentsheet/{questioneer_id}")
    def questioneer(questioneer_id: str, show: str = None, lang: str = None):
        header(f"consentsheet/{questioneer_id}", lang or "en")
        sheet_content(lang=lang or "en", questioneer_id=questioneer_id, show=show)

    @ui.page("/consentsheet")
    def constentsheet_new(lang: str = "en"):
        header("consentsheet", lang)
        sheet_content(lang=lang)

    @ui.page("/groupconsent")
    def group_new(lang: str = "en"):
        header("groupconsent", lang)
        group_overview_content(lang=lang)

    @ui.page("/groupconsent/{group_name_id}")
    def groupconsent(group_name_id: str, lang: str = None):
        header(f"groupconsent/{group_name_id}", lang or "en")
        group_overview_content(lang=lang or "en", group_name_id=group_name_id)

    @ui.page("/google/login")
    async def google_login(google_sso: GoogleSSO = Depends(get_google_sso)):
        return await google_sso.get_login_redirect()

    @ui.page("/google/callback")
    async def google_callback(
        request: Request, google_sso: GoogleSSO = Depends(get_google_sso)
    ):
        user = await google_sso.verify_and_process(request)
        logging.getLogger("content_consent_finder").debug(f"google {user}")
        app.storage.user["user_id"] = f"google-{user.id}"
        return ui.navigate.to("/welcome")

    @ui.page("/discord/callback")
    async def discord_callback(
        request: Request, discord_sso: DiscordSSO = Depends(get_discord_sso)
    ):
        user = await discord_sso.verify_and_process(request)
        logging.getLogger("content_consent_finder").debug(f"discord {user}")
        app.storage.user["user_id"] = f"discord-{user.id}"
        return ui.navigate.to("/welcome")

    @ui.page("/discord/login")
    async def discord_login(discord_sso: DiscordSSO = Depends(get_discord_sso)):
        return await discord_sso.get_login_redirect()


@app.get("/api/qr")
def qr(share_id: str, sheet_id: str, lang: str = "en"):
    img_byte_arr = io.BytesIO()
    generate_sheet_share_qr_code(share_id, sheet_id, lang).save(
        img_byte_arr, format="PNG"
    )
    return Response(content=img_byte_arr.getvalue(), media_type="image/png")


def redact_string(s: str) -> str:
    if s == "-default-":
        return s
    return "!!NULL!!" if s is None else f"<REDACTED {len(s)}>"


app.on_startup(startup)

if __name__ in {"__main__", "__mp_main__"}:
    logging.getLogger(a_logger_setup.LOGGER_NAME).info(
        "========== Starting Lester's Content Pact =========="
    )
    logging.getLogger(a_logger_setup.LOGGER_NAME).info(
        f"DB_CONNECTION_STRING: {os.getenv('DB_CONNECTION_STRING', '-default-')}"
    )
    logging.getLogger(a_logger_setup.LOGGER_NAME).info(
        f"LOGLEVEL: {os.getenv('LOGLEVEL', '-default-')}"
    )
    logging.getLogger(a_logger_setup.LOGGER_NAME).info(
        f"GOOGLE_CLIENT_ID: {os.getenv('GOOGLE_CLIENT_ID', '-default-')}"
    )
    logging.getLogger(a_logger_setup.LOGGER_NAME).info(
        f"GOOGLE_CLIENT_SECRET: {redact_string(os.getenv('GOOGLE_CLIENT_SECRET', '-default-'))}"
    )
    logging.getLogger(a_logger_setup.LOGGER_NAME).info(
        f"DISCORD_CLIENT_ID: {os.getenv('DISCORD_CLIENT_ID', '-default-')}"
    )
    logging.getLogger(a_logger_setup.LOGGER_NAME).info(
        f"DISCORD_CLIENT_SECRET: {redact_string(os.getenv('DISCORD_CLIENT_SECRET', '-default-'))}"
    )
    logging.getLogger(a_logger_setup.LOGGER_NAME).info(
        f"BASE_URL: {os.getenv('BASE_URL', '-default-')}"
    )
    logging.getLogger(a_logger_setup.LOGGER_NAME).info(
        f"ADMINS: {os.getenv('ADMINS', '-default-')}"
    )
    logging.getLogger(a_logger_setup.LOGGER_NAME).info(
        f"SEED_ON_STARTUP: {os.getenv('SEED_ON_STARTUP', '-default-')}"
    )
    logging.getLogger(a_logger_setup.LOGGER_NAME).info(
        f"RELOAD: {os.getenv('RELOAD', '-default-')}"
    )
    logging.getLogger(a_logger_setup.LOGGER_NAME).info(
        f"STORAGE_SECRET: {redact_string(os.getenv('STORAGE_SECRET', '-default-'))}"
    )
    logging.getLogger(a_logger_setup.LOGGER_NAME).info(
        "===================================================="
    )
    ui.run(
        title="Lester's Content Pact",
        favicon=Path("src/favicon.ico"),
        storage_secret=os.getenv(
            "STORAGE_SECRET",
            "".join(random.choices(string.ascii_letters + string.digits, k=32)),
        ),
        reload=RELOAD,
        port=int(os.getenv("PORT", 8080)),
    )
