from nicegui import ui, app

from components.consent_entry_component import (
    CategoryEntryComponent,
    ConsentEntryComponent,
)
from components.consent_legend_component import consent_legend_component
from components.sheet_display_component import SheetDisplayComponent
from components.sheet_editable_component import SheetEditableComponent

from localization.language_manager import get_localization, make_localisable
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
def content(questioneer_id: str = None, lang: str = "en", **kwargs):
    user: User = get_user_by_id_name(app.storage.user.get("user_id"))
    logging.debug(f"{questioneer_id} {kwargs}")
    if not user:
        ui.navigate.to(f"/welcome?lang={lang}")
        return
    if not questioneer_id:
        sheet = create_new_consentsheet(user)
        ui.navigate.to(f"/consentsheet/{sheet.id}?show=edit&lang={lang}")
        return
    else:
        sheet = get_consent_sheet_by_id(int(questioneer_id))

    consent_legend_component(lang)
    ui.separator()

    with ui.tabs() as tabs:
        display_tab = ui.tab("Sheet")
        edit_tab = ui.tab("Edit")
        groups_tab = ui.tab("Groups")
        make_localisable(display_tab, key="display", language=lang)
        make_localisable(edit_tab, key="edit", language=lang)
        make_localisable(groups_tab, key="groups", language=lang)
    with ui.tab_panels(
        tabs, value=edit_tab if kwargs.get("show", "") == "edit" else display_tab
    ).classes("w-full") as panels:
        with ui.tab_panel(display_tab):
            sheet_display = SheetDisplayComponent(sheet, lang)
        with ui.tab_panel(edit_tab):
            SheetEditableComponent(sheet, lang)
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
                        assign_checkbox.tooltip(
                            get_localization("cannot_unassign_gm_sheet", lang)
                        )
    panels.on_value_change(lambda: sheet_display.content.refresh())
