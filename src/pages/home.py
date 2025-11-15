import logging
from dataclasses import dataclass

from nicegui import app, ui, events

from components.dialog_components import open_confirmation_dialog
from services.group_service import (
    delete_group,
    get_group_by_id,
    join_group,
    leave_group,
)
from controller.sheet_controller import (
    delete_sheet,
    fetch_sheet_groups,
    get_consent_sheet_by_id,
    import_sheet_from_json,
)
from controller.user_controller import (
    delete_account,
    fetch_user_groups,
    get_user_from_storage,
)
from guided_tour import NiceGuidedTour
from localization.language_manager import get_localization, make_localisable
from models.db_models import (
    ConsentSheet,
    RPGGroup,
    User,
)
from models.model_utils import generate_group_name_id


@dataclass
class HomeTours:
    """Bundle the guided tours used across the home dashboard."""

    create_sheet: NiceGuidedTour
    share_sheet: NiceGuidedTour
    create_group: NiceGuidedTour
    join_group: NiceGuidedTour
    import_export: NiceGuidedTour


def reload_after(func, *args, **kwargs):
    func(*args, **kwargs)
    ui.navigate.reload()


def remove_account(user: User) -> None:
    delete_account(user)
    app.storage.user.clear()
    ui.notify("Bye Bye!")


def content(**kwargs):
    tours = _build_home_tours()
    user = get_user_from_storage()
    if not user:
        logging.getLogger("content_consent_finder").debug("No user found")
        ui.navigate.to("/welcome")
        return
    _render_home_layout(user, tours)
    _render_delete_account_button(user)
    _start_requested_tour(tours)


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


def _render_home_layout(user: User, tours: HomeTours) -> None:
    """Compose the main cards for groups and consent sheets."""

    with ui.grid().classes("lg:grid-cols-2 grid-cols-1 gap-4 mx-auto"):
        with ui.card():
            make_localisable(ui.label("Groups"), key="groups")
            _render_groups_section(user, tours.create_group, tours.join_group)
        with ui.card():
            make_localisable(ui.label(), key="consent_sheets")
            _render_sheet_section(
                user,
                tours.create_sheet,
                tours.share_sheet,
                tours.join_group,
                tours.import_export,
            )


def _render_delete_account_button(user: User) -> None:
    """Surface account removal with an explicit confirmation dialog."""

    def _confirm_delete() -> None:
        open_confirmation_dialog(
            "delete_account",
            lambda: remove_account(user),
            refresh_after=True,
        )

    delete_account_button = (
        ui.button(color="red").on_click(_confirm_delete).classes("w-1/2 mx-auto")
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
    user: User,
    tour_create_sheet: NiceGuidedTour,
    tour_share_sheet: NiceGuidedTour,
    tour_join_group: NiceGuidedTour,
    tour_import_export: NiceGuidedTour,
) -> None:
    sheet_grid = _render_sheet_grid(
        user,
        tour_create_sheet,
        tour_share_sheet,
        tour_join_group,
        tour_import_export,
    )
    sheet_grid.mark(f"sheet_grid({len(user.consent_sheets)})")
    ui.separator()
    _render_sheet_actions(tour_create_sheet, tour_import_export, user)


def _render_sheet_grid(
    user: User,
    tour_create_sheet: NiceGuidedTour,
    tour_share_sheet: NiceGuidedTour,
    tour_join_group: NiceGuidedTour,
    tour_import_export: NiceGuidedTour,
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
        for sheet_ref in user.consent_sheets:
            if not sheet_ref:
                continue
            sheet = get_consent_sheet_by_id(
                app.storage.user.get("user_id"), sheet_ref.id
            )
            _render_sheet_row(
                tour_share_sheet,
                sheet,
                user,
                tour_import_export,
            )
    return sheet_grid


def _render_sheet_actions(
    tour_create_sheet: NiceGuidedTour,
    tour_import_export: NiceGuidedTour,
    user: User,
) -> None:
    new_sheet_button = ui.button("Create Consent Sheet").on_click(
        lambda: ui.navigate.to("/consentsheet/")
    )
    new_sheet_button.mark("new_sheet_button")
    tour_create_sheet.add_step(
        new_sheet_button, get_localization("tour_create_sheet_new_sheet_button")
    )
    import_upload = ui.upload(label="Import", on_upload=handle_sheet_upload).mark(
        "import_sheet_upload"
    )
    make_localisable(import_upload, key="import_sheet")
    tour_create_sheet.add_next_page(lambda: ui.navigate.to("/consentsheet/"))
    make_localisable(new_sheet_button, key="create_sheet")
    tour_import_export.add_step(
        import_upload,
        get_localization("tour_import_export_import_button"),
    )
    target_url = "/consentsheet/"
    if user.consent_sheets:
        target_url = f"/consentsheet/{user.consent_sheets[0].id}"
    tour_import_export.add_next_page(
        lambda url=target_url: _continue_import_export_tour(url)
    )


async def handle_sheet_upload(upload_event: events.UploadEventArguments):
    user = get_user_from_storage()
    if imported_sheet_id := import_sheet_from_json(
        await upload_event.file.text(), user
    ):
        ui.notify(get_localization("sheet_imported_successfully"))
        ui.navigate.to(f"/consentsheet/{imported_sheet_id}")


def _render_sheet_row(
    tour_share_sheet: NiceGuidedTour,
    sheet: ConsentSheet,
    user: User,
    tour_import_export: NiceGuidedTour,
) -> None:
    if not sheet:
        return
    with ui.row().classes("bg-gray-700 p-2 rounded-lg"):
        icon = _resolve_sheet_icon(sheet)
        tour_share_sheet.add_step(icon, get_localization("tour_share_sheet_sheet_icon"))
        tour_share_sheet.add_next_page(
            lambda sheet=sheet: ui.navigate.to(f"/consentsheet/{sheet.id}")
        )
        sheet_groups = fetch_sheet_groups(sheet)
        with ui.column().classes("gap-1"):
            ui.label(sheet.display_name)
            ui.label(_format_sheet_groups(sheet_groups)).classes("text-xs")
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
        _render_sheet_delete_button(sheet, sheet_groups, user)


def _continue_import_export_tour(target_url: str) -> None:
    app.storage.user["active_tour"] = "import_export"
    ui.navigate.to(target_url)


def _resolve_sheet_icon(sheet: ConsentSheet):
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


def _format_sheet_groups(sheet_groups: list[RPGGroup]) -> str:
    if not sheet_groups:
        return get_localization("no_group")
    return ", ".join(group.name for group in sheet_groups)


def _render_sheet_delete_button(
    sheet: ConsentSheet, sheet_groups: list[RPGGroup], user: User
) -> None:
    can_be_deleted = not sheet_groups or all(
        group.gm_consent_sheet_id != sheet.id for group in sheet_groups
    )

    def _confirm_delete(target_sheet: ConsentSheet) -> None:
        open_confirmation_dialog(
            "delete_sheet",
            lambda: delete_sheet(user, target_sheet),
            refresh_after=True,
        )

    delete_button = ui.button("Remove", color="red").on_click(
        lambda sheet=sheet: _confirm_delete(sheet)
    )
    delete_button.mark(f"delete_sheet_button-{sheet.id}")
    make_localisable(delete_button, key="remove")
    delete_button.set_enabled(can_be_deleted)
    if not can_be_deleted:
        delete_button.tooltip(get_localization("cannot_delete_sheet_in_group"))


def _render_groups_section(
    user: User,
    tour_create_group: NiceGuidedTour,
    tour_join_group: NiceGuidedTour,
) -> None:
    group_grid = _render_group_grid(user)
    ui.separator()
    _render_group_creation_controls(tour_create_group)
    ui.separator()
    _render_group_join_controls(user, tour_join_group)
    tour_join_group.add_step(
        group_grid,
        get_localization("tour_join_group_group_grid"),
    )


def _render_group_grid(user: User):
    with ui.grid(columns=1) as group_grid:
        for group in fetch_user_groups(user):
            _render_group_row(user, group)
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
    user: User,
    tour_join_group: NiceGuidedTour,
) -> None:
    with ui.row():
        invite_code_input = ui.input("Group Code").mark("group_join_code_input")
        make_localisable(invite_code_input, key="group_join_code")
        join_button = make_localisable(
            ui.button("Join Group")
            .on_click(lambda: reload_after(join_group, invite_code_input.value, user))
            .mark("join_group_button"),
            key="join_group",
        )
        tour_join_group.add_step(
            invite_code_input,
            get_localization("tour_join_group_invite_code_input"),
        )
        tour_join_group.add_step(
            join_button,
            get_localization("tour_join_group_join_button"),
            lambda: invite_code_input.set_value("global"),
        )


def _render_group_row(user: User, group: RPGGroup) -> None:
    group = get_group_by_id(group.id)
    if not group:
        return
    with ui.row():
        ui.label(f"{group.name} {group.id}").mark(f"group_name_{group.id}")
        make_localisable(
            ui.button("Details").on_click(
                lambda group=group: ui.navigate.to(
                    f"/groupconsent/{generate_group_name_id(group)}"
                )
            ),
            key="details",
        )
        if group.gm_user_id == user.id:
            make_localisable(
                ui.button("DELETE", color="red")
                .on_click(lambda group=group: _confirm_group_delete(group))
                .mark(f"delete_group_button_{group.id}"),
                key="delete",
            )
        else:
            make_localisable(
                ui.button("Leave")
                .on_click(lambda group=group: _confirm_group_leave(group, user))
                .mark(f"leave_group_button_{group.id}"),
                key="leave",
            )


def _confirm_group_delete(group: RPGGroup) -> None:
    open_confirmation_dialog(
        "delete_group",
        lambda: delete_group(group),
        refresh_after=True,
    )


def _confirm_group_leave(group: RPGGroup, user: User) -> None:
    open_confirmation_dialog(
        "leave_group",
        lambda: leave_group(group, user),
        refresh_after=True,
    )
