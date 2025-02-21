import io
import random
import string
import traceback
from fastapi.responses import JSONResponse, HTMLResponse
from nicegui import ui, app, Client
from nicegui.page import page
from localization.language_manager import make_localisable
from models.db_models import User
from models.controller import (
    get_user_by_id_name,
    update_user,
)
from models.seeder import seed_consent_questioneer
from pages.questioneer import content as questioneer_content
from pages.group_overview import content as group_overview_content
from pages.public_sheet import content as public_sheet_content
from pages.home import content as home_content
from pages.faq_page import content as faq_content
from pages.content_trigger_view import content as content_trigger_view
from pages.admin_page import content as admin_page_content
from pages.login_page import content as login_page_content
from pages.dsgvo import dsgvo_html
from fastapi import Depends, Request, Response
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.discord import DiscordSSO
import logging
import os

from public_share_qr import generate_sheet_share_qr_code


logging.basicConfig(
    level=os.getenv("LOGLEVEL", "INFO").upper(),
    format="%(asctime)s - %(levelname)-8s - %(pathname)s:%(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "...")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "...")
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "...")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "...")

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")

SEED_ON_STARTUP = os.getenv("SEED_ON_STARTUP", "False").lower() == "true"
if SEED_ON_STARTUP:
    seed_consent_questioneer()

RELOAD = os.getenv("RELOAD", "False").lower() == "true"

ADMINS = os.getenv("ADMINS", "").split(",")


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
    with ui.row().classes("m-0 w-full bg-gray-800 text-white p-4"):
        ui.label("RPG Content Consent Finder").classes("text-xl lg:text-3xl")
        ui.space()
        if user_id := app.storage.user.get("user_id"):
            user: User = get_user_by_id_name(user_id)
            if not user and current_page in {"home", "admin"}:
                ui.navigate.to(f"/welcome?lang={lang}")
                return
            ui.label(f"Hi {user.nickname if user else ''}!").classes(
                "text-md lg:text-xl mt-1"
            )
        else:
            user = None
        ui.space()
        if user:
            ui.link("Home", f"/home?lang={lang}").classes(
                link_classes + (highlight if current_page == "home" else "")
            )
        ui.link("Contents", f"/content_trigger?lang={lang}").classes(
            link_classes + (highlight if current_page == "content_trigger" else "")
        )
        ui.link("FAQ", f"/faq?lang={lang}").classes(
            link_classes + (highlight if current_page == "faq" else "")
        )
        if lang == "de":
            ui.link("EN", f"/{current_page}?lang=en").classes(link_classes)
        else:
            ui.link("DE", f"/{current_page}?lang=de").classes(link_classes)
        if user_id in ADMINS:
            ui.link("Admin", f"/admin?lang={lang}").classes(
                link_classes + (highlight if current_page == "admin" else "")
            )
        ui.space()
        if user_id:
            ui.link("Logout", "/logout").classes(
                link_classes.replace("bg-gray-600", "bg-red-800")
            )
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
    logging.debug("healthcheck_and_heartbeat")
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
        )
    return client.build_response(request, 404)


@app.exception_handler(500)
async def exception_handler_500(request: Request, exception: Exception) -> Response:
    stack_trace = traceback.format_exc()
    msg_to_user = f"**{exception}**\n\nStack trace: \n<pre>{stack_trace}"
    with Client(page(""), request=request) as client:
        language = request.query_params.get("lang", "en")
        header("error", lang=language)
        with ui.card().classes("p-4 mx-auto border-red-800 rounded-lg"):
            ui.label("Internal Application Error").classes("text-2xl")
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
            logging.debug(f"welcoming {user}")
            if not user or not user.nickname:
                ui.label("Welcome, yet unknown user").classes("text-2xl")
                new_user = user or User(
                    id_name=user_id,
                    nickname="",
                )
                ui.input("Your name").bind_value(new_user, "nickname")
                ui.button(
                    "Save", on_click=lambda: update_user_and_go_home(new_user, lang)
                )
            else:
                ui.navigate.to("/home")
        else:
            logging.debug("no user_id")
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
                ui.button(
                    "Log/Sign in via Account and Password",
                    on_click=lambda: ui.navigate.to("/login"),
                )

    @ui.page("/admin")
    def admin(lang: str = "en"):
        header("admin", lang)
        admin_page_content()

    @ui.page("/logout")
    def logout(lang: str = "en"):
        logging.debug("logout")
        app.storage.user["user_id"] = None
        return ui.navigate.to(f"/home?lang={lang}")

    @ui.page("/consent/{share_id}/{sheet_id}")
    def public_sheet(share_id: str, sheet_id: str, lang: str = None):
        header(f"consent/{share_id}/{sheet_id}", lang or "en")
        public_sheet_content(lang=lang or "en", share_id=share_id, sheet_id=sheet_id)

    @ui.page("/consentsheet/{questioneer_id}")
    def questioneer(questioneer_id: str, show: str = None, lang: str = None):
        header(f"consentsheet/{questioneer_id}", lang or "en")
        questioneer_content(lang=lang or "en", questioneer_id=questioneer_id, show=show)

    @ui.page("/consentsheet")
    def constentsheet_new(lang: str = "en"):
        header("consentsheet", lang)
        questioneer_content(lang=lang)

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
        logging.debug(f"google {user}")
        app.storage.user["user_id"] = f"google-{user.id}"
        return ui.navigate.to("/welcome")

    @ui.page("/discord/callback")
    async def discord_callback(
        request: Request, discord_sso: DiscordSSO = Depends(get_discord_sso)
    ):
        user = await discord_sso.verify_and_process(request)
        logging.debug(f"discord {user}")
        app.storage.user["user_id"] = f"discord-{user.id}"
        return ui.navigate.to("/welcome")

    @ui.page("/discord/login")
    async def discord_login(discord_sso: DiscordSSO = Depends(get_discord_sso)):
        return await discord_sso.get_login_redirect()


@app.get("/api/qr")
def qr(share_id: str, sheet_id: str):
    img_byte_arr = io.BytesIO()
    generate_sheet_share_qr_code(share_id, sheet_id).save(img_byte_arr, format="PNG")
    return Response(content=img_byte_arr.getvalue(), media_type="image/png")


app.on_startup(startup)
ui.run(
    title="RPG Content Consent Finder",
    dark=True,
    favicon="🔍",
    storage_secret=os.getenv(
        "STORAGE_SECRET",
        "".join(random.choices(string.ascii_letters + string.digits, k=32)),
    ),
    reload=RELOAD,
)
