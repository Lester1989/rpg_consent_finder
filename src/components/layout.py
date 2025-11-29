import logging
from pathlib import Path

from nicegui import Client, ui

from a_logger_setup import LOGGER_NAME
from controller.user_controller import get_user_by_id_name, get_user_from_storage
from services.session_service import (
    get_current_user_id,
    session_storage,
)
from settings import get_settings

LOGGER = logging.getLogger(LOGGER_NAME)
settings = get_settings()

try:
    project_version = Path("src/version.txt").read_text().strip()
except Exception:
    project_version = "unknown"


def set_language(lang: str):
    session_storage["lang"] = lang
    ui.navigate.reload()


@ui.refreshable
def page_header(current_page: str = None):
    link_classes = "text-lg lg:text-xl text-white hover:text-gray-300 no-underline bg-gray-600 p-1 lg:p-2 rounded"
    highlight = " shadow-md shadow-yellow-500"

    LOGGER.debug("Rendering page header for current_page=%s", current_page)

    def nav_entry(
        label: str,
        target: str,
        page_key: str,
        *,
        mark_id: str | None = None,
        active_keys: set[str] | None = None,
        base_classes: str | None = None,
    ):
        keys = active_keys if active_keys is not None else {page_key}
        css = (base_classes or link_classes) + (
            highlight if current_page in keys else ""
        )
        button = ui.button(
            label,
            on_click=lambda _=None, dest=target, marker=page_key: _navigate_to_page(
                dest, marker
            ),
        ).classes(css)
        button.props("flat no-caps")
        if mark_id:
            button.mark(mark_id)
        return button

    with ui.row().classes("m-0 w-full bg-gray-800 text-white p-2"):
        with ui.column(align_items="start").classes("gap-0 p-0 m-0"):
            ui.label("Lester's Content Pact").classes("text-md lg:text-2xl p-0 m-0")
            ui.label(project_version).classes("text-xs text-gray-500 p-0 m-0")
        ui.space()

        # Try to get user from context/storage
        user = None
        if user_id := get_current_user_id():
            user = get_user_by_id_name(user_id)
            if not user and current_page in {"home", "admin"}:
                ui.navigate.to("/welcome")
                return
            ui.label(f"Hi {user.nickname if user else ''}!").classes(
                "text-md lg:text-xl mt-1"
            )

        if not user:
            user = get_user_from_storage()

        ui.space()
        if user:
            nav_entry("Home", "/home", "home", mark_id="home_link home_button")
        nav_entry("News", "/news", "news")
        nav_entry("Contents", "/content_trigger", "content_trigger")
        nav_entry("FAQ", "/faq", "faq")
        if user:
            nav_entry("Playstyle", "/playstyle", "playstyle")
        if user and user.id_name in settings.admins:
            nav_entry("Admin", "/admin", "admin")
        ui.space()
        lang = session_storage.get("lang", "en")
        if lang == "de":
            ui.button("EN", on_click=lambda: set_language("en")).classes(link_classes)
        else:
            ui.button("DE", on_click=lambda: set_language("de")).classes(link_classes)

        dark = ui.dark_mode(value=True)
        ui.switch("Dark").bind_value(dark)
        if user:
            nav_entry(
                "Logout",
                "/logout",
                "home",
                mark_id="logout_btn",
                active_keys=set(),
                base_classes=link_classes.replace("bg-gray-600", "bg-red-800"),
            )
        else:
            nav_entry(
                "Login",
                "/login",
                "login",
                mark_id="login_nav_button",
                active_keys={"welcome", "login"},
            )


async def safe_refresh_header(current_page: str | None = None) -> None:
    """Safely refresh the page header, handling dead clients."""
    try:
        # check if client is still alive and connected
        client: Client | None = getattr(ui.context, "client", None)
        if client is None or not client.has_socket_connection:
            LOGGER.info("Client disconnected, skipping header refresh")
            return
        if any(
            target.container._client() is None
            for target in page_header.targets[0].refreshable.targets
        ):
            LOGGER.info("No client associated with page header, skipping refresh")
            return
        await page_header.refresh(current_page=current_page)
    except RuntimeError as e:
        LOGGER.warning("page header refresh failed RuntimeError: %s", e, exc_info=True)
    except Exception as e:
        LOGGER.warning("page header refresh failed Exception: %s", e, exc_info=True)


def set_current_page_marker(page: str) -> None:
    """Helper used as click handler on header links to update current page marker.

    Setting session_storage['current_page'] triggers the registered session
    listener which will refresh the header for the current client.
    """
    try:
        session_storage["current_page"] = page
    except Exception:
        LOGGER.debug("failed to set current_page in session_storage", exc_info=True)


async def _navigate_to_page(target: str, page: str) -> None:
    set_current_page_marker(page)
    ui.navigate.to(target)
    await safe_refresh_header(current_page=page)


# def _refresh_header_on_session_change(session: SessionData) -> None:
#     client = getattr(ui.context, "client", None)
#     if client is None:
#         return
#     current_page = session_storage.get("current_page", "")
#     LOGGER.info("Session change detected, refreshing header for page=%s", current_page)

#     async def _trigger_refresh() -> None:
#         try:
#             # Check if client is still alive and connected
#             if not client.has_socket_connection:
#                 LOGGER.info("Client disconnected, skipping header refresh")
#                 return

#             await safe_refresh_header(current_page=current_page or None)
#         except Exception:
#             LOGGER.warning("skipping header refresh", exc_info=True)

#     ui.timer(0, _trigger_refresh, once=True)


# register_session_listener(_refresh_header_on_session_change)


def page_frame(current_page=None):
    session_storage["current_page"] = current_page or ""
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
