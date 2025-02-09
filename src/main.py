import random
import string
from fastapi.responses import JSONResponse
from nicegui import ui, app
from models.models import User
from models.controller import get_status, get_user_by_id_name, update_user
from models.seeder import seed_consent_questioneer
from pages.questioneer import content as questioneer_content
from pages.group_overview import content as group_overview_content
from pages.public_sheet import content as public_sheet_content
from pages.home import content as home_content
from pages.faq_page import content as faq_content
from pages.content_trigger_view import content as content_trigger_view
from fastapi import Depends, Request
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.discord import DiscordSSO
import logging
import os


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

ADMINS = os.getenv("ADMINS", "").split(",")
SEED_ON_STARTUP = os.getenv("SEED_ON_STARTUP", "False").lower() == "true"
if SEED_ON_STARTUP:
    seed_consent_questioneer()

RELOAD = os.getenv("RELOAD", "False").lower() == "true"


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


def header():
    with ui.row().classes("m-0 w-full bg-gray-800 text-white p-4"):
        ui.label("RPG Content Consent Finder").classes("text-3xl")
        ui.space()
        if user_id := app.storage.user.get("user_id"):
            user: User = get_user_by_id_name(user_id)
            ui.label(f"Hello {user.nickname}").classes("text-xl mt-1")
        ui.space()
        ui.link("Home", "/home").classes(
            "text-xl text-white hover:text-gray-300 no-underline bg-gray-600 p-2 rounded"
        )
        ui.link("Content Trigger", "/content_trigger").classes(
            "text-xl text-white hover:text-gray-300 no-underline bg-gray-600 p-2 rounded"
        )
        ui.link("FAQ", "/faq").classes(
            "text-xl text-white hover:text-gray-300 no-underline bg-gray-600 p-2 rounded"
        )
        if user_id in ADMINS:
            ui.link("Dev", "/dev").classes(
                "text-xl text-white hover:text-gray-300 no-underline bg-gray-600 p-2 rounded"
            )
        ui.space()
        if user_id:
            ui.link("Logout", "/logout").classes(
                "text-xl text-white hover:text-gray-300 no-underline bg-red-800 p-2 rounded"
            )
        else:
            ui.button(
                "Sign in with Google", on_click=lambda: ui.navigate.to("/google/login")
            )
            ui.button(
                "Sign in with Discord",
                on_click=lambda: ui.navigate.to("/discord/login"),
            )


@app.get("/healthcheck_and_heartbeat")
def healthcheck_and_heartbeat(request: Request):
    logging.debug("healthcheck_and_heartbeat")
    return JSONResponse({"status": "ok"})


def startup():
    @ui.page("/")
    def empty_uri():
        return ui.navigate.to("/home")

    @ui.page("/faq")
    def faq():
        header()
        faq_content()

    @ui.page("/content_trigger")
    def content_trigger():
        header()
        content_trigger_view()

    @ui.page("/home")
    def home():
        header()
        home_content()

    @ui.page("/welcome")
    def welcome():
        if user_id := app.storage.user.get("user_id"):
            user: User = get_user_by_id_name(user_id)
            logging.debug(f"welcoming {user}")
            if not user or not user.nickname:
                ui.label("Welcome, yet unknown user").classes("text-2xl")
                new_user = User(
                    id_name=user_id,
                    nickname="",
                )
                ui.input("Your name").bind_value(new_user, "nickname")
                ui.button("Save", on_click=lambda: update_user(new_user))
            else:
                ui.navigate.to("/home")
        else:
            logging.debug("no user_id")
            ui.button(
                "Sign in with Google", on_click=lambda: ui.navigate.to("/google/login")
            )
            ui.button(
                "Sign in with Discord",
                on_click=lambda: ui.navigate.to("/discord/login"),
            )

    @ui.page("/dev")
    def dev():
        header()
        user_id = app.storage.user.get("user_id")
        if user_id not in ADMINS:
            ui.label("Not an admin")
            ui.link("Home", "/home")
            return
        ui.button("Seed ", on_click=seed_consent_questioneer)

        for table, table_count_and_clear_func in get_status().items():
            with ui.row():
                ui.label(f"{table} {table_count_and_clear_func[0]}")
                ui.button("clear", color="red").on_click(table_count_and_clear_func[1])

    @ui.page("/logout")
    def logout():
        logging.debug("logout")
        app.storage.user["user_id"] = None
        return ui.navigate.to("/home")

    @ui.page("/consent/{share_id}/{sheet_id}")
    def public_sheet(share_id: str, sheet_id: str):
        header()
        public_sheet_content(share_id=share_id, sheet_id=sheet_id)

    @ui.page("/consentsheet/{questioneer_id}")
    def questioneer(questioneer_id: str, show: str = None):
        header()
        questioneer_content(questioneer_id=questioneer_id, show=show)

    @ui.page("/consentsheet")
    def constentsheet_new():
        header()
        questioneer_content()

    @ui.page("/groupconsent")
    def group_new():
        header()
        group_overview_content()

    @ui.page("/groupconsent/{group_name_id}")
    def groupconsent(group_name_id: str):
        header()
        group_overview_content(group_name_id=group_name_id)

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


app.on_startup(startup)
ui.run(
    title="RPG Content Consent Finder",
    dark=True,
    favicon="🔍",
    storage_secret="".join(random.choices(string.ascii_letters + string.digits, k=32)),
    reload=RELOAD,
)
