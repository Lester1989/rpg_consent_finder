from nicegui import ui, app

from components.consent_entry_component import (
    CategoryEntryComponent,
    ConsentEntryComponent,
)
from components.sheet_display_component import SheetDisplayComponent
from components.sheet_editable_component import SheetEditableComponent

from models.db_models import (
    ConsentEntry,
    ConsentSheet,
    ConsentStatus,
    ConsentTemplate,
    RPGGroup,
    User,
)
from models.controller import (
    assign_consent_sheet_to_group,
    get_all_consent_topics,
    get_consent_sheet_by_id,
    get_group_by_name_id,
    create_new_consentsheet,
    get_user_by_id_name,
    unassign_consent_sheet_from_group,
)
import logging


@ui.refreshable
def content(questioneer_id: str = None, **kwargs):
    user: User = get_user_by_id_name(app.storage.user.get("user_id"))
    logging.debug(f"{questioneer_id} {kwargs}")
    if not user:
        ui.navigate.to("/welcome")
        return
    if not questioneer_id:
        sheet = create_new_consentsheet(user)
        ui.navigate.to(f"/consentsheet/{sheet.id}")
        return
    else:
        sheet = get_consent_sheet_by_id(int(questioneer_id))
    ui.label("Consent Levels").classes("text-2xl mx-auto")
    with ui.grid().classes("lg:grid-cols-5 grid-cols-2 gap-2 lg:w-5/6 w-full mx-auto"):
        for preference in ConsentStatus:
            with ui.column().classes(
                "p-2 rounded-lg shadow-sm shadow-white gap-1 items-center"
            ):
                ui.label(preference.as_emoji + preference.name.capitalize()).classes(
                    "text-xs text-gray-500 text-center"
                )
                ui.markdown(preference.explanation_de)
    ui.separator()
    with ui.tabs() as tabs:
        display_tab = ui.tab("Sheet")
        edit_tab = ui.tab("Edit")
        groups_tab = ui.tab("Groups")
    with ui.tab_panels(
        tabs, value=edit_tab if kwargs.get("show", "") == "edit" else display_tab
    ).classes("w-full") as panels:
        with ui.tab_panel(display_tab):
            sheet_display = SheetDisplayComponent(sheet)
        with ui.tab_panel(edit_tab):
            SheetEditableComponent(sheet)
        with ui.tab_panel(groups_tab):
            with ui.grid(columns=2):
                for group in user.groups:
                    assign_checkbox = ui.checkbox(
                        group.name, value=group.id in [g.id for g in sheet.groups]
                    ).on_value_change(
                        lambda change_evt_args, group=group: (
                            assign_consent_sheet_to_group(sheet, group)
                            if change_evt_args.value
                            else unassign_consent_sheet_from_group(sheet, group)
                        )
                    )
                    is_gm_sheet = group.gm_consent_sheet_id == sheet.id
                    if is_gm_sheet:
                        assign_checkbox.enabled = False
                        assign_checkbox.tooltip("GM sheet, cannot be unassigned")
    panels.on_value_change(lambda: sheet_display.content.refresh())
