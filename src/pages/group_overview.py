import logging
import random
import string
from nicegui import ui, app

from components.consent_entry_component import CategoryEntryComponent
from components.sheet_display_component import SheetDisplayComponent
from components.sheet_editable_component import SheetEditableComponent

from components.consent_display_component import ConsentDisplayComponent
from models.db_models import (
    ConsentEntry,
    ConsentSheet,
    ConsentStatus,
    ConsentTemplate,
    RPGGroup,
    User,
)
from models.controller import (
    create_new_consentsheet,
    create_new_group,
    get_all_consent_topics,
    get_group_by_name_id,
    get_user_by_id_name,
    leave_group,
    regenerate_invite_code,
    update_group,
)
from models.model_utils import questioneer_id


@ui.refreshable
def content(group_name_id: str = None, **kwargs):
    user: User = get_user_by_id_name(app.storage.user.get("user_id"))
    if not user:
        ui.navigate.to("/welcome")
        return
    logging.debug(f"{group_name_id}")
    if not group_name_id:
        group = create_new_group(user)
        group_name_id = questioneer_id(group)
    group: RPGGroup = get_group_by_name_id(group_name_id)
    is_gm = user.id == group.gm_user_id
    if user.id == group.gm_user_id:
        with ui.tabs() as tabs:
            display_tab = ui.tab("Consent")
            if is_gm:
                edit_tab = ui.tab("Edit")
            general_tab = ui.tab("General")
        with ui.tab_panels(tabs, value=display_tab).classes("w-full") as panels:
            with ui.tab_panel(display_tab):
                sheet_display = SheetDisplayComponent(
                    consent_sheets=group.consent_sheets
                )
            if is_gm:
                with ui.tab_panel(edit_tab):
                    SheetEditableComponent(group.gm_consent_sheet)
            with ui.tab_panel(general_tab):
                ui.input("Group Name").bind_value(group, "name").on(
                    "focusout", lambda _: update_group(group)
                )
                with ui.row():
                    ui.label("Group Join Code")
                    ui.label(group.invite_code).bind_text(group, "invite_code")
                    ui.button(
                        "New Code", on_click=lambda: regenerate_invite_code(group)
                    ).tooltip("[GM only] Generate a new invite code").set_enabled(is_gm)

                with ui.grid(columns=3):
                    for player in group.users:
                        ui.label(player.nickname)
                        if any(
                            sheet
                            for sheet in group.consent_sheets
                            if sheet.user_id == player.id
                        ):
                            ui.label("Part of Consent")
                        else:
                            ui.label("Consent Sheet missing")
                        if player.id == group.gm_user_id:
                            ui.label("GM")
                        else:
                            ui.button("Remove Player", color="red").on_click(
                                lambda player=player: leave_group(group, player)
                            ).tooltip(
                                "[GM only] Removes Player from Group"
                            ).set_enabled(is_gm)
        panels.on_value_change(lambda: sheet_display.content.refresh())
