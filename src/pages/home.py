import logging

from nicegui import app, ui

from controller.group_controller import (
    delete_group,
    get_group_by_id,
    join_group,
    leave_group,
)
from controller.sheet_controller import delete_sheet, get_consent_sheet_by_id
from controller.user_controller import (
    delete_account,
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


def reload_after(func, *args, **kwargs):
    func(*args, **kwargs)
    content.refresh()


async def reload_after_async(func, *args, **kwargs):
    await func(*args, **kwargs)
    content.refresh()


def confirm_before(key: str, lang: str, refresh_after: bool, func, *args, **kwargs):
    return (
        await confirm_before_async(key, lang, refresh_after, func, *args, **kwargs)
        for _ in "_"
    ).__anext__()


async def confirm_before_async(
    key: str, lang: str, refresh_after: bool, func, *args, **kwargs
):
    with ui.dialog() as dialog, ui.card():
        make_localisable(ui.label(), key=f"{key}_confirm", language=lang)
        with ui.row():
            make_localisable(
                ui.button("Yes", on_click=lambda: dialog.submit("Yes")),
                key="yes",
                language=lang,
            )
            make_localisable(
                ui.button("No", on_click=lambda: dialog.submit("No")),
                key="no",
                language=lang,
            )

        if await dialog == "Yes":
            func(*args, **kwargs)
            if refresh_after:
                content.refresh()


def remove_account(user: User):
    delete_account(user)
    app.storage.user.clear()
    ui.notify("Bye Bye!")


@ui.refreshable
def content(lang: str = "en", **kwargs):
    tour_create_sheet = NiceGuidedTour(
        storage_key="tour_create_sheet_progress", page_suffix="home"
    )
    tour_share_sheet = NiceGuidedTour(
        storage_key="tour_share_sheet_progress", page_suffix="home"
    )
    tour_create_group = NiceGuidedTour(
        storage_key="tour_create_group_progress", page_suffix="home"
    )
    user: User = get_user_from_storage()
    if not user:
        logging.debug("No user found")
        ui.navigate.to(f"/welcome?lang={lang}")
        return
    with ui.grid().classes("lg:grid-cols-2 grid-cols-1 gap-4 mx-auto"):
        # list groups with button to leave and button to show details
        with ui.card():
            make_localisable(ui.label("Groups"), key="groups", language=lang)
            groups_content(lang, user, tour_create_group)

        # list consent sheets with icons for public or private and button to remove or to copy/duplicate
        with ui.card():
            make_localisable(ui.label(), key="consent_sheets", language=lang)
            sheet_content(lang, user, tour_create_sheet, tour_share_sheet)
    make_localisable(
        ui.button(color="red")
        .on_click(
            lambda: confirm_before("delete_account", lang, True, remove_account, user)
        )
        .classes("w-1/2 mx-auto"),
        key="delete_account",
        language=lang,
    )
    active_tour = app.storage.user.get("active_tour", "")
    if active_tour == "create_sheet":
        ui.timer(0.5, tour_create_sheet.start_tour, once=True)
    elif active_tour == "share_sheet":
        ui.timer(0.5, tour_share_sheet.start_tour, once=True)
    elif active_tour == "create_group":
        ui.timer(0.5, tour_create_group.start_tour, once=True)


def sheet_content(
    lang: str,
    user: User,
    tour_create_sheet: NiceGuidedTour,
    tour_share_sheet: NiceGuidedTour,
):
    with ui.grid().classes("grid-cols-1 lg:grid-cols-2") as sheet_grid:
        tour_create_sheet.add_step(
            sheet_grid, get_localization("tour_create_sheet_sheet_grid", lang)
        )
        tour_share_sheet.add_step(
            sheet_grid, get_localization("tour_share_sheet_sheet_grid", lang)
        )
        for sheet in user.consent_sheets:
            if not sheet:
                continue
            sheet: ConsentSheet = get_consent_sheet_by_id(
                app.storage.user.get("user_id"), sheet.id
            )
            sheet_display_row(lang, tour_share_sheet, sheet)

    ui.separator()
    # button to create new consent sheet
    new_sheet_button = ui.button("Create Consent Sheet").on_click(
        lambda: ui.navigate.to("/consentsheet/")
    )
    tour_create_sheet.add_step(
        new_sheet_button, get_localization("tour_create_sheet_new_sheet_button", lang)
    )
    tour_create_sheet.add_next_page(
        lambda: ui.navigate.to(f"/consentsheet/?lang={lang}")
    )
    make_localisable(
        new_sheet_button,
        key="create_sheet",
        language=lang,
    )


def sheet_display_row(lang, tour_share_sheet, sheet):
    with ui.row().classes("bg-gray-700 p-2 rounded-lg"):
        if sheet.public_share_id:
            icon = (
                ui.icon("public")
                .classes("pt-2 text-green-500")
                .tooltip(get_localization("public_sheet_tooltip", lang))
            )
        else:
            icon = (
                ui.icon("lock")
                .classes("pt-2 text-red-500")
                .tooltip(get_localization("private_sheet_tooltip", lang))
            )
        tour_share_sheet.add_step(
            icon, get_localization("tour_share_sheet_sheet_icon", lang)
        )
        tour_share_sheet.add_next_page(
            lambda sheet=sheet: ui.navigate.to(f"/consentsheet/{sheet.id}?lang={lang}")
        )
        with ui.column().classes("gap-1"):
            ui.label(sheet.display_name)
            group_text = get_localization("no_group", lang)
            if sheet.groups:
                group_text = ", ".join(group.name for group in sheet.groups)
            ui.label(group_text).classes("text-xs")
        ui.space()
        details_button = ui.button("Details").on_click(
            lambda sheet=sheet: ui.navigate.to(f"/consentsheet/{sheet.id}?lang={lang}")
        )
        tour_share_sheet.add_step(
            details_button,
            get_localization("tour_share_sheet_details_button", lang),
        )
        make_localisable(
            details_button,
            key="details",
            language=lang,
        )
        can_be_deleted = len(sheet.groups) == 0 or all(
            group.gm_consent_sheet_id != sheet.id for group in sheet.groups
        )
        delete_button = ui.button("Remove", color="red").on_click(
            lambda sheet=sheet: confirm_before(
                "delete_sheet", lang, True, delete_sheet, sheet
            )
        )
        make_localisable(delete_button, key="remove", language=lang)
        delete_button.set_enabled(can_be_deleted)
        if not can_be_deleted:
            delete_button.tooltip(
                get_localization("cannot_delete_sheet_in_group", lang)
            )


def groups_content(lang: str, user: User, tour_create_group: NiceGuidedTour):
    with ui.grid(columns=1):
        for group in user.groups:
            group_display_row(lang, user, group)

    ui.separator()
    # button to create group
    create_group_button = ui.button("Create Group").on_click(
        lambda: ui.navigate.to(f"/groupconsent/?lang={lang}")
    )
    tour_create_group.add_step(
        create_group_button,
        get_localization("tour_create_group_create_group_button", lang),
    )
    tour_create_group.add_next_page(
        lambda: ui.navigate.to(f"/groupconsent/?lang={lang}")
    )
    make_localisable(
        create_group_button,
        key="create_group",
        language=lang,
    )
    ui.separator()
    # button to join group
    with ui.row():
        invite_code_input = ui.input("Group Code")
        make_localisable(
            invite_code_input,
            key="group_join_code",
            language=lang,
        )
        make_localisable(
            ui.button("Join Group").on_click(
                lambda: reload_after(join_group, invite_code_input.value, user)
            ),
            key="join_group",
            language=lang,
        )


def group_display_row(lang: str, user: User, group: RPGGroup):
    group: RPGGroup = get_group_by_id(group.id)
    if not group:
        return
    with ui.row():
        ui.label(f"{group.name} {group.id}")
        make_localisable(
            ui.button("Details").on_click(
                lambda group=group: ui.navigate.to(
                    f"/groupconsent/{generate_group_name_id(group)}?lang={lang}"
                )
            ),
            key="details",
            language=lang,
        )
        if group.gm_user_id == user.id:
            make_localisable(
                ui.button("DELETE", color="red").on_click(
                    lambda group=group: confirm_before(
                        "delete_group", lang, True, delete_group, group
                    )
                ),
                key="delete",
                language=lang,
            )
        else:
            make_localisable(
                ui.button("Leave").on_click(
                    lambda group=group: confirm_before(
                        "leave_group", lang, True, leave_group, group, user
                    )
                ),
                key="leave",
                language=lang,
            )
