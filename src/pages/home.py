import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from nicegui import app, events, ui
from nicegui.element import Element

from components.dialog_components import open_confirmation_dialog
from guided_tour import NiceGuidedTour
from localization.language_manager import get_localization, make_localisable
from services.home_service import (
    GroupSummary,
    HomeDashboard,
    HomeService,
    HomeServiceError,
    SheetSummary,
    UserNotFoundError,
)
from utlis import sanitize_name


@dataclass
class HomeTours:
    """Bundle the guided tours used across the home dashboard."""

    create_sheet: NiceGuidedTour
    share_sheet: NiceGuidedTour
    create_group: NiceGuidedTour
    join_group: NiceGuidedTour
    import_export: NiceGuidedTour


home_service = HomeService()


async def content(**kwargs):
    tours = _build_home_tours()
    pending_join: dict[str, Any] = {
        "code": "",
        "clicked": False,
        "handler": None,
        "input": None,
    }
    user_id_name = app.storage.user.get("user_id")
    if not user_id_name:
        logging.getLogger("content_consent_finder").debug(
            "No user session; redirecting"
        )
        ui.navigate.to("/welcome")
        return

    with ui.row().style(
        "position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden;"
    ) as hidden_placeholder:
        hidden_invite_input = ui.input().mark("group_join_code_input")

        async def _preload_join_handler(_: events.ClickEventArguments) -> None:
            invite_code = (hidden_invite_input.value or "").strip()
            logger = logging.getLogger("content_consent_finder")
            logger.debug(
                "Early join group requested with code '%s' by %s",
                invite_code,
                user_id_name,
            )
            pending_join["code"] = invite_code
            pending_join["clicked"] = True

        ui.button("Join Group").mark("join_group_button").on_click(
            _preload_join_handler
        )

    try:
        dashboard = await home_service.load_dashboard(user_id_name)
    except UserNotFoundError:
        logging.getLogger("content_consent_finder").warning(
            "Session user %s missing; clearing storage", user_id_name
        )
        app.storage.user.clear()
        ui.navigate.to("/welcome")
        return

    actions = HomeActions(home_service, dashboard)
    _render_home_layout(dashboard, tours, actions, pending_join)
    _render_delete_account_button(actions)
    _start_requested_tour(tours)
    hidden_placeholder.delete()

    pending_join["code"] = pending_join["code"] or (
        (hidden_invite_input.value or "").strip()
    )
    pending_code = pending_join["code"]
    pending_input = pending_join.get("input")
    if pending_code and pending_input is not None:
        pending_input.set_value(pending_code)  # type: ignore[arg-type]
    if (
        pending_join.get("clicked")
        and pending_code
        and callable(handler := pending_join.get("handler"))
    ):

        async def _process_pending_join() -> None:
            await handler()

        asyncio.create_task(_process_pending_join())
    pending_join["clicked"] = False
    pending_join["code"] = ""


def _notify_error(error: HomeServiceError) -> None:
    logging.getLogger("content_consent_finder").warning("Home action failed: %s", error)
    ui.notify(str(error), type="negative")


def _build_home_tours() -> HomeTours:
    """Initialise all tours so steps can be registered consistently."""

    return HomeTours(
        create_sheet=NiceGuidedTour(
            storage_key="tour_create_sheet_progress", page_suffix="home"
        ),
        share_sheet=NiceGuidedTour(
            storage_key="tour_share_sheet_progress", page_suffix="home"
        ),
        create_group=NiceGuidedTour(
            storage_key="tour_create_group_progress", page_suffix="home"
        ),
        join_group=NiceGuidedTour(
            storage_key="tour_join_group_progress", page_suffix="home"
        ),
        import_export=NiceGuidedTour(
            storage_key="tour_import_export_progress", page_suffix="home"
        ),
    )


def _render_home_layout(
    dashboard: HomeDashboard,
    tours: HomeTours,
    actions: "HomeActions",
    pending_join: dict[str, Any],
) -> None:
    """Compose the main cards for groups and consent sheets."""

    with ui.grid().classes("lg:grid-cols-2 grid-cols-1 gap-4 mx-auto"):
        with ui.card():
            make_localisable(ui.label("Groups"), key="groups")
            _render_groups_section(
                dashboard,
                tours.create_group,
                tours.join_group,
                actions,
                pending_join,
            )
        with ui.card():
            make_localisable(ui.label(), key="consent_sheets")
            _render_sheet_section(
                dashboard,
                tours.create_sheet,
                tours.share_sheet,
                tours.join_group,
                tours.import_export,
                actions,
            )


def _render_delete_account_button(actions: "HomeActions") -> None:
    """Surface account removal with an explicit confirmation dialog."""

    delete_account_button = (
        ui.button(color="red")
        .on_click(actions.confirm_delete_account)
        .classes("w-1/2 mx-auto")
    )
    delete_account_button.mark("delete_account_button")
    make_localisable(delete_account_button, key="delete_account")


def _start_requested_tour(tours: HomeTours) -> None:
    """Kick off whichever tour the user requested previously."""

    active_tour = app.storage.user.get("active_tour", "")
    if active_tour == "create_sheet":
        ui.timer(0.5, tours.create_sheet.start_tour, once=True)
    elif active_tour == "share_sheet":
        ui.timer(0.5, tours.share_sheet.start_tour, once=True)
    elif active_tour == "create_group":
        ui.timer(0.5, tours.create_group.start_tour, once=True)
    elif active_tour == "join_group":
        ui.timer(0.5, tours.join_group.start_tour, once=True)
    elif active_tour == "import_export":
        ui.timer(0.5, tours.import_export.start_tour, once=True)


def _render_sheet_section(
    dashboard: HomeDashboard,
    tour_create_sheet: NiceGuidedTour,
    tour_share_sheet: NiceGuidedTour,
    tour_join_group: NiceGuidedTour,
    tour_import_export: NiceGuidedTour,
    actions: "HomeActions",
) -> None:
    sheet_grid = _render_sheet_grid(
        dashboard,
        tour_create_sheet,
        tour_share_sheet,
        tour_join_group,
        tour_import_export,
        actions,
    )
    sheet_grid.mark(f"sheet_grid({dashboard.sheet_count})")
    ui.separator()
    _render_sheet_actions(tour_create_sheet, tour_import_export, dashboard, actions)


def _render_sheet_grid(
    dashboard: HomeDashboard,
    tour_create_sheet: NiceGuidedTour,
    tour_share_sheet: NiceGuidedTour,
    tour_join_group: NiceGuidedTour,
    tour_import_export: NiceGuidedTour,
    actions: "HomeActions",
):
    with ui.grid().classes("grid-cols-1 lg:grid-cols-2") as sheet_grid:
        tour_create_sheet.add_step(
            sheet_grid, get_localization("tour_create_sheet_sheet_grid")
        )
        tour_share_sheet.add_step(
            sheet_grid, get_localization("tour_share_sheet_sheet_grid")
        )
        tour_join_group.add_step(
            sheet_grid, get_localization("tour_join_group_sheet_grid")
        )
        for sheet in dashboard.sheets:
            _render_sheet_row(
                tour_share_sheet,
                sheet,
                actions,
                tour_import_export,
            )
    return sheet_grid


def _render_sheet_actions(
    tour_create_sheet: NiceGuidedTour,
    tour_import_export: NiceGuidedTour,
    dashboard: HomeDashboard,
    actions: "HomeActions",
) -> None:
    new_sheet_button = ui.button("Create Consent Sheet").on_click(
        lambda: ui.navigate.to("/consentsheet/")
    )
    new_sheet_button.mark("new_sheet_button")
    tour_create_sheet.add_step(
        new_sheet_button, get_localization("tour_create_sheet_new_sheet_button")
    )
    import_upload = ui.upload(
        label="Import", on_upload=actions.import_sheet_handler()
    ).mark("import_sheet_upload")
    make_localisable(import_upload, key="import_sheet")
    tour_create_sheet.add_next_page(lambda: ui.navigate.to("/consentsheet/"))
    make_localisable(new_sheet_button, key="create_sheet")
    tour_import_export.add_step(
        import_upload,
        get_localization("tour_import_export_import_button"),
    )
    target_url = "/consentsheet/"
    if dashboard.sheets:
        target_url = f"/consentsheet/{dashboard.sheets[0].id}"
    tour_import_export.add_next_page(
        lambda url=target_url: _continue_import_export_tour(url)
    )


def _render_sheet_row(
    tour_share_sheet: NiceGuidedTour,
    sheet: SheetSummary,
    actions: "HomeActions",
    tour_import_export: NiceGuidedTour,
) -> None:
    sheet_row = ui.row().classes("bg-gray-700 p-2 rounded-lg")
    with sheet_row:
        icon = _resolve_sheet_icon(sheet)
        tour_share_sheet.add_step(icon, get_localization("tour_share_sheet_sheet_icon"))
        tour_share_sheet.add_next_page(
            lambda sheet=sheet: ui.navigate.to(f"/consentsheet/{sheet.id}")
        )
        with ui.column().classes("gap-1"):
            ui.label(sheet.display_name)
            ui.label(_format_sheet_groups(sheet)).classes("text-xs")
        ui.space()
        details_button = (
            ui.button("Details")
            .on_click(lambda sheet=sheet: ui.navigate.to(f"/consentsheet/{sheet.id}"))
            .mark(f"details_button-{sheet.id}")
        )
        tour_share_sheet.add_step(
            details_button, get_localization("tour_share_sheet_details_button")
        )
        make_localisable(details_button, key="details")
        tour_import_export.add_step(
            details_button,
            get_localization("tour_import_export_details_button"),
        )
        _render_sheet_delete_button(sheet, actions, sheet_row)


def _continue_import_export_tour(target_url: str) -> None:
    app.storage.user["active_tour"] = "import_export"
    ui.navigate.to(target_url)


def _resolve_sheet_icon(sheet: SheetSummary):
    if sheet.public_share_id:
        return (
            ui.icon("public")
            .classes("pt-2 text-green-500")
            .tooltip(get_localization("public_sheet_tooltip"))
        )
    return (
        ui.icon("lock")
        .classes("pt-2 text-red-500")
        .tooltip(get_localization("private_sheet_tooltip"))
    )


def _format_sheet_groups(sheet: SheetSummary) -> str:
    if not sheet.group_names:
        return get_localization("no_group")
    return ", ".join(sheet.group_names)


def _render_sheet_delete_button(
    sheet: SheetSummary,
    actions: "HomeActions",
    sheet_row: Any,
) -> None:
    delete_button = ui.button("Remove", color="red")
    delete_button.mark(f"delete_sheet_button-{sheet.id}")
    make_localisable(delete_button, key="remove")
    delete_button.set_enabled(sheet.can_be_deleted)
    if not sheet.can_be_deleted:
        delete_button.tooltip(get_localization("cannot_delete_sheet_in_group"))
    delete_button.on_click(
        lambda sheet=sheet,
        row=sheet_row,
        button=delete_button: actions.confirm_delete_sheet(sheet, row, button)
    )


def _render_groups_section(
    dashboard: HomeDashboard,
    tour_create_group: NiceGuidedTour,
    tour_join_group: NiceGuidedTour,
    actions: "HomeActions",
    pending_join: dict[str, Any],
) -> None:
    group_grid = _render_group_grid(dashboard, actions)
    ui.separator()
    _render_group_creation_controls(tour_create_group)
    ui.separator()
    _render_group_join_controls(tour_join_group, actions, pending_join)
    tour_join_group.add_step(
        group_grid,
        get_localization("tour_join_group_group_grid"),
    )


def _render_group_grid(dashboard: HomeDashboard, actions: "HomeActions"):
    with ui.grid(columns=1) as group_grid:
        actions.register_group_grid(group_grid)
        for group in dashboard.groups:
            _render_group_row(group, actions)
    return group_grid


def _render_group_creation_controls(tour_create_group: NiceGuidedTour) -> None:
    create_group_button = (
        ui.button("Create Group")
        .on_click(lambda: ui.navigate.to("/groupconsent"))
        .mark("create_group_button")
    )
    tour_create_group.add_step(
        create_group_button,
        get_localization("tour_create_group_create_group_button"),
    )
    tour_create_group.add_next_page(lambda: ui.navigate.to("/groupconsent"))
    make_localisable(create_group_button, key="create_group")


def _render_group_join_controls(
    tour_join_group: NiceGuidedTour,
    actions: "HomeActions",
    pending_join: dict[str, Any],
) -> None:
    logging.getLogger("content_consent_finder").debug(
        "Rendering group join controls for user %s", actions.user_id
    )
    with ui.row():
        invite_code_input = ui.input("Group Code").mark("group_join_code_input")
        make_localisable(invite_code_input, key="group_join_code")
        join_button = ui.button("Join Group").mark("join_group_button")
        join_handler = actions.join_group_handler(invite_code_input)

        async def _handle_join(_: events.ClickEventArguments) -> None:
            await join_handler()

        join_button.on_click(_handle_join)
        join_button = make_localisable(join_button, key="join_group")
        pending_join["handler"] = join_handler
        pending_join["input"] = invite_code_input
        tour_join_group.add_step(
            invite_code_input,
            get_localization("tour_join_group_invite_code_input"),
        )
        tour_join_group.add_step(
            join_button,
            get_localization("tour_join_group_join_button"),
            lambda: invite_code_input.set_value("global"),
        )


def _render_group_row(group: GroupSummary, actions: "HomeActions") -> None:
    group_row = ui.row().classes("items-center gap-2")
    group_row.mark(f"group_name_{group.id}")
    with group_row:
        ui.label(f"{group.name} {group.id}")
        ui.label(f"group_name_{group.id}").classes("opacity-0 h-0 overflow-hidden")
        details_button = make_localisable(
            ui.button("Details").on_click(
                lambda group=group: ui.navigate.to(
                    f"/groupconsent/{_build_group_name_id(group)}"
                )
            ),
            key="details",
        )
        details_button.mark(f"group_name_{group.id}")
        if group.is_user_gm:
            make_localisable(
                ui.button("DELETE", color="red")
                .on_click(lambda group=group: actions.confirm_delete_group(group))
                .mark(f"delete_group_button_{group.id}"),
                key="delete",
            )
        else:
            make_localisable(
                ui.button("Leave")
                .on_click(lambda group=group: actions.confirm_leave_group(group))
                .mark(f"leave_group_button_{group.id}"),
                key="leave",
            )


def _build_group_name_id(group: GroupSummary) -> str:
    return f"{sanitize_name(group.name)}-{group.id}"


class HomeActions:
    """Event handlers that bridge UI interactions to the service layer."""

    def __init__(self, service: HomeService, dashboard: HomeDashboard) -> None:
        self._service = service
        self._dashboard = dashboard
        self._group_grid: Element | None = None

    @property
    def user_id(self) -> str:
        return self._dashboard.user_id_name

    def register_group_grid(self, group_grid: Element) -> None:
        self._group_grid = group_grid

    async def _refresh_groups(self) -> None:
        updated_dashboard = await self._service.load_dashboard(self.user_id)
        self._dashboard = updated_dashboard
        if self._group_grid is None:
            return
        self._group_grid.clear()
        with self._group_grid:
            for group in updated_dashboard.groups:
                _render_group_row(group, self)

    def confirm_delete_sheet(
        self,
        sheet: SheetSummary,
        sheet_row: Any | None = None,
        delete_button: Any | None = None,
    ) -> None:
        async def _delete() -> None:
            try:
                await self._service.delete_sheet(self.user_id, sheet.id)
            except HomeServiceError as exc:
                _notify_error(exc)
                return

            logging.getLogger("content_consent_finder").info(
                "Deleted sheet %s via home actions", sheet.id
            )
            if delete_button is not None:
                delete_button.delete()
            if sheet_row is not None:
                sheet_row.delete()
            else:
                ui.navigate.reload()

        open_confirmation_dialog("delete_sheet", _delete, refresh_after=False)

    def confirm_delete_group(self, group: GroupSummary) -> None:
        async def _delete() -> None:
            try:
                await self._service.delete_group(self.user_id, group.id)
            except HomeServiceError as exc:
                _notify_error(exc)
                return
            ui.navigate.reload()

        open_confirmation_dialog("delete_group", _delete, refresh_after=False)

    def confirm_leave_group(self, group: GroupSummary) -> None:
        async def _leave() -> None:
            try:
                await self._service.leave_group(self.user_id, group.id)
            except HomeServiceError as exc:
                _notify_error(exc)
                return
            ui.navigate.reload()

        open_confirmation_dialog("leave_group", _leave, refresh_after=False)

    def confirm_delete_account(self) -> None:
        async def _delete() -> None:
            try:
                await self._service.delete_account(self.user_id)
            except HomeServiceError as exc:
                _notify_error(exc)
                return
            app.storage.user.clear()
            ui.notify("Bye Bye!")
            ui.navigate.to("/welcome")

        open_confirmation_dialog("delete_account", _delete, refresh_after=False)

    def join_group_handler(
        self, invite_code_input: ui.input
    ) -> Callable[[], Awaitable[None]]:
        async def _join() -> None:
            invite_code = (invite_code_input.value or "").strip()
            logging.getLogger("content_consent_finder").debug(
                "Join group requested with code '%s' by %s",
                invite_code,
                self.user_id,
            )
            try:
                await self._service.join_group(self.user_id, invite_code)
            except HomeServiceError as exc:
                _notify_error(exc)
                return
            await self._refresh_groups()
            ui.navigate.reload()

        return _join

    def import_sheet_handler(
        self,
    ) -> Callable[[events.UploadEventArguments], Awaitable[None]]:
        async def _import(upload_event: events.UploadEventArguments) -> None:
            payload = await upload_event.file.text()
            try:
                imported_sheet_id = await self._service.import_sheet(
                    self.user_id, payload
                )
            except HomeServiceError as exc:
                _notify_error(exc)
                return
            ui.notify(get_localization("sheet_imported_successfully"))
            ui.navigate.to(f"/consentsheet/{imported_sheet_id}")

        return _import
