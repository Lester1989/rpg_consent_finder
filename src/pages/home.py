from nicegui import ui, app

from models.models import (
    ConsentSheet,
    RPGGroup,
    User,
)
from models.controller import (
    delete_group,
    delete_sheet,
    get_consent_sheet_by_id,
    get_group_by_id,
    get_user_by_id_name,
    join_group,
    leave_group,
)
from models.model_utils import questioneer_id
import logging


def button_delete_group(group: RPGGroup):
    logging.debug(f"delete group {group}")
    delete_group(group)
    content.refresh()


def button_leave_group(group: RPGGroup, user: User):
    logging.debug(f"leave group {group}")
    leave_group(group, user)
    content.refresh()


def button_delete_sheet(sheet: ConsentSheet):
    logging.debug(f"delete sheet {sheet}")
    delete_sheet(sheet)
    content.refresh()


@ui.refreshable
def content(**kwargs):
    user: User = get_user_by_id_name(app.storage.user.get("user_id"))
    if not user:
        logging.debug("No user found")
        ui.navigate.to("/welcome")
        return
    ui.label(user.nickname)
    with ui.grid(columns=2).classes("gap-4 mx-auto"):
        # list groups with button to leave and button to show details
        with ui.card():
            ui.label("Groups")
            with ui.grid(columns=1):
                for group in user.groups:
                    group: RPGGroup = get_group_by_id(group.id)
                    with ui.row():
                        ui.label(f"{group.name} {group.id}")
                        ui.button("Details").on_click(
                            lambda group=group: ui.navigate.to(
                                f"/groupconsent/{questioneer_id(group)}"
                            )
                        )
                        if group.gm_user_id == user.id:
                            ui.button("DELETE", color="red").on_click(
                                lambda group=group: button_delete_group(group)
                            )
                        else:
                            ui.button("Leave").on_click(
                                lambda group=group: button_leave_group(group, user)
                            )
            ui.separator()
            # button to create group
            ui.button("Create Group").on_click(lambda: ui.navigate.to("/groupconsent/"))
            ui.separator()
            # button to join group
            with ui.row():
                invite_code_input = ui.input("Group Code")
                ui.button("Join Group").on_click(
                    lambda: join_group(invite_code_input.value, user)
                )

        # list consent sheets with icons for public or private and button to remove or to copy/duplicate
        with ui.card():
            ui.label("Consent Sheets")
            with ui.grid(columns=2):
                for sheet in user.consent_sheets:
                    sheet: ConsentSheet = get_consent_sheet_by_id(sheet.id)
                    with ui.row().classes("bg-gray-700 p-2 rounded-lg"):
                        if sheet.public_share_id:
                            ui.icon("public").classes("pt-2 text-green-500").tooltip(
                                "Can be accessed by anyone"
                            )
                        else:
                            ui.icon("lock").classes("pt-2 text-red-500").tooltip(
                                "Only accessible by you and the connected groups"
                            )
                        with ui.column().classes("gap-1"):
                            ui.label(sheet.display_name)
                            group_text = "No group connected"
                            if sheet.groups:
                                group_text = ", ".join(
                                    group.name for group in sheet.groups
                                )
                            ui.label(group_text).classes("text-xs")
                        ui.space()
                        ui.button("Details").on_click(
                            lambda sheet=sheet: ui.navigate.to(
                                f"/consentsheet/{sheet.id}"
                            )
                        )
                        can_be_deleted = len(sheet.groups) == 0 or all(
                            group.gm_consent_sheet_id != sheet.id
                            for group in sheet.groups
                        )
                        delete_button = ui.button("Remove", color="red").on_click(
                            lambda sheet=sheet: button_delete_sheet(sheet)
                        )
                        delete_button.set_enabled(can_be_deleted)
                        if not can_be_deleted:
                            delete_button.tooltip(
                                "Can only be deleted if not connected to a group"
                            )

            ui.separator()
            # button to create new consent sheet
            ui.button("Create Consent Sheet").on_click(
                lambda: ui.navigate.to("/consentsheet/")
            )
