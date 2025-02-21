from nicegui import ui, app

from components.consent_legend_component import consent_legend_component
from components.sheet_display_component import SheetDisplayComponent
from components.sheet_editable_component import SheetEditableComponent
from components.preference_ordered_sheet_display_component import (
    PreferenceOrderedSheetDisplayComponent,
)

from localization.language_manager import get_localization, make_localisable
from models.db_models import (
    User,
)
from models.controller import (
    assign_consent_sheet_to_group,
    get_consent_sheet_by_id,
    create_new_consentsheet,
    get_user_by_id_name,
    unassign_consent_sheet_from_group,
)
import logging

SHOW_TAB_STORAGE_KEY = "sheet_show_tab"


@ui.refreshable
def content(questioneer_id: str = None, lang: str = "en", **kwargs):
    user: User = get_user_by_id_name(app.storage.user.get("user_id"))
    logging.debug(f"{questioneer_id}")
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
        display_tab = ui.tab("display")
        ordered_topics_tab = ui.tab("ordered_topics")
        edit_tab = ui.tab("edit")
        groups_tab = ui.tab("groups")
        make_localisable(display_tab, key="display", language=lang)
        make_localisable(ordered_topics_tab, key="ordered_topics", language=lang)
        make_localisable(edit_tab, key="edit", language=lang)
        make_localisable(groups_tab, key="groups", language=lang)
        named_tabs = {
            "display": display_tab,
            "ordered_topics": ordered_topics_tab,
            "edit": edit_tab,
            "groups": groups_tab,
        }
    show_tab = app.storage.user.get(SHOW_TAB_STORAGE_KEY, "display")
    with ui.tab_panels(tabs, value=named_tabs.get(show_tab, display_tab)).classes(
        "w-full"
    ) as panels:
        with ui.tab_panel(display_tab):
            category_topics_display = SheetDisplayComponent(sheet, lang=lang)
        with ui.tab_panel(ordered_topics_tab):
            ordered_topics_display = PreferenceOrderedSheetDisplayComponent(
                sheet, lang=lang
            )
        with ui.tab_panel(edit_tab):
            sheet_editor = SheetEditableComponent(sheet, lang=lang)
        with ui.tab_panel(groups_tab):
            with ui.grid(columns=2) as group_grid:
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
                if not user.groups:
                    ui.label(get_localization("no_groups", lang))

    panels.on_value_change(
        lambda x: storage_show_tab_and_refresh(
            x.value, category_topics_display, ordered_topics_display, sheet_editor
        )
    )


def storage_show_tab_and_refresh(
    tab: str,
    category_topics_display: SheetDisplayComponent,
    ordered_topics_display: PreferenceOrderedSheetDisplayComponent,
    sheet_editor: SheetEditableComponent,
):
    app.storage.user[SHOW_TAB_STORAGE_KEY] = tab
    if tab == "display":
        category_topics_display.content.refresh()
    elif tab == "ordered_topics":
        ordered_topics_display.content.refresh()
    elif tab == "edit":
        sheet_editor.content.refresh()
