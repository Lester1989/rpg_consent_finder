import logging

from nicegui import ui

from a_logger_setup import LOGGER_NAME
from components.preference_ordered_sheet_display_component import (
    PreferenceOrderedSheetDisplayComponent,
)
from components.sheet_display_component import SheetDisplayComponent
from components.sheet_editable_component import SheetEditableComponent
from components.tab_components import TabSpec, create_localised_tabs, create_tab_panels
from services.group_service import (
    assign_consent_sheet_to_group,
    create_new_group,
    fetch_group_sheets,
    fetch_group_users,
    get_group_by_name_id,
    leave_group,
    regenerate_invite_code,
    update_group,
)
from controller.user_controller import get_user_by_id_name
from guided_tour import NiceGuidedTour
from localization.language_manager import get_localization, make_localisable
from models.db_models import (
    ConsentSheet,
    RPGGroup,
    User,
)
from models.model_utils import generate_group_name_id
from services.session_service import get_current_user_id, session_storage

SHOW_TAB_STORAGE_KEY = "group_show_tab"


def reload_after(func, *args, **kwargs):
    func(*args, **kwargs)
    ui.navigate.reload()


def content(group_name_id: str = None, **kwargs):
    tour_create_group = NiceGuidedTour(
        storage_key="tour_create_group_progress", page_suffix="home"
    )
    user_id = get_current_user_id()
    user: User = get_user_by_id_name(user_id) if user_id else None
    if not user:
        ui.navigate.to("/welcome")
        return
    logging.getLogger(LOGGER_NAME).debug(f"{group_name_id}")
    if not group_name_id:
        logging.getLogger(LOGGER_NAME).debug("creating new group")
        group = create_new_group(user)
        group_name_id = generate_group_name_id(group)
        ui.navigate.to(f"/groupconsent/{group_name_id}")
        return
    group: RPGGroup = get_group_by_name_id(group_name_id)
    logging.getLogger(LOGGER_NAME).debug(f"{group}")
    logging.getLogger(LOGGER_NAME).debug(f"sheet {group.gm_consent_sheet}")
    logging.getLogger(LOGGER_NAME).debug(f"sheet_id {group.gm_consent_sheet_id}")
    group_consent_sheets = fetch_group_sheets(group)
    logging.getLogger(LOGGER_NAME).debug(f"consent_sheets {group_consent_sheets}")
    is_gm = user.id == group.gm_user_id
    tabs, named_tabs = _build_group_tabs(tour_create_group)
    panels = create_tab_panels(
        tabs,
        named_tabs,
        SHOW_TAB_STORAGE_KEY,
        default_key="ordered_topics",
    )
    show_tab = session_storage.get(SHOW_TAB_STORAGE_KEY, "ordered_topics")
    logging.getLogger(LOGGER_NAME).debug(f"show_tab {show_tab}")
    with panels:
        with ui.tab_panel(named_tabs["consent"]):
            logging.getLogger(LOGGER_NAME).info(f"sheet {group.gm_consent_sheet}")
            sheet_display = SheetDisplayComponent(
                consent_sheets=group_consent_sheets,
            )
        with ui.tab_panel(named_tabs["ordered_topics"]):
            ordered_topics_display = PreferenceOrderedSheetDisplayComponent(
                consent_sheets=group_consent_sheets
            )
        with ui.tab_panel(named_tabs["edit"]):
            sheet_editor = edit_tab_content(user, group, is_gm, group_consent_sheets)
            tour_create_group.add_step(
                sheet_editor,
                get_localization("tour_create_group_sheet_editor"),
                lambda: panels.set_value(named_tabs["edit"]),
            )
            tour_create_group.add_step(
                named_tabs["general"],
                get_localization("tour_create_group_general_tab"),
                lambda: panels.set_value(named_tabs["general"]),
            )
        with ui.tab_panel(named_tabs["general"]):
            if group.invite_code == "global":
                ui.label("Global Group")
            else:
                general_tab_content(
                    group, is_gm, tour_create_group, group_consent_sheets
                )
    panels.on_value_change(
        lambda x: storage_show_tab_and_refresh(
            x.value, sheet_display, ordered_topics_display, sheet_editor
        )
    )
    active_tour = session_storage.get("active_tour", "")
    if active_tour == "create_group":
        ui.timer(0.5, tour_create_group.start_tour, once=True)


def _build_group_tabs(
    tour_create_group: NiceGuidedTour,
):
    tab_specs = [
        TabSpec("consent", "display", title="Consent", mark="group_display_tab"),
        TabSpec("ordered_topics", "ordered_topics"),
        TabSpec("edit", "edit"),
        TabSpec("general", "general"),
    ]
    tabs, named_tabs = create_localised_tabs(tab_specs)
    tour_create_group.add_step(
        named_tabs["edit"],
        get_localization("tour_create_group_edit_tab"),
    )
    return tabs, named_tabs


def edit_tab_content(
    user: User,
    group: RPGGroup,
    is_gm: bool,
    group_consent_sheets: list[ConsentSheet],
):
    if is_gm:
        sheet_editor = SheetEditableComponent(group.gm_consent_sheet)
    else:
        if user_sheet := next(
            (sheet for sheet in group_consent_sheets if sheet.user_id == user.id),
            None,
        ):
            sheet_editor = SheetEditableComponent(user_sheet)
        else:
            sheet_editor = None
            make_localisable(
                ui.label("No Consent Sheet assigned yet"),
                key="no_sheet_assigned",
            )
            for consent_sheet in user.consent_sheets:
                ui.button(
                    consent_sheet.display_name,
                    on_click=lambda consent_sheet=consent_sheet: (
                        reload_after(
                            assign_consent_sheet_to_group, consent_sheet, group
                        ),
                    ),
                )

    return sheet_editor


def storage_show_tab_and_refresh(
    tab: str,
    category_topics_display: SheetDisplayComponent,
    ordered_topics_display: PreferenceOrderedSheetDisplayComponent,
    sheet_editor: SheetEditableComponent,
):
    tab = tab.lower()
    session_storage[SHOW_TAB_STORAGE_KEY] = tab
    logging.getLogger(LOGGER_NAME).debug(f"storage_show_tab_and_refresh {tab}")
    if tab == "consent":
        category_topics_display.content.refresh()
    elif tab == "ordered_topics":
        ordered_topics_display.content.refresh()
    elif tab == "edit" and sheet_editor:
        sheet_editor.content.refresh()


def general_tab_content(
    group: RPGGroup,
    is_gm: bool,
    tour_create_group: NiceGuidedTour,
    group_consent_sheets: list[ConsentSheet],
):
    group_name_input = (
        ui.input("Group Name")
        .bind_value(group, "name")
        .on("focusout", lambda _: update_group(group))
        .classes("lg:w-1/2 w-full")
    )
    tour_create_group.add_step(
        group_name_input,
        get_localization("tour_create_group_group_name_input"),
    )
    group_name_input.set_enabled(is_gm)
    make_localisable(
        group_name_input,
        key="group_name",
    )
    with ui.row():
        make_localisable(
            ui.label("Group Join Code"),
            key="group_join_code",
        )
        code_label = ui.label(group.invite_code).bind_text(group, "invite_code")
        tour_create_group.add_step(
            code_label,
            get_localization("tour_create_group_group_join_code"),
        )
        new_button = ui.button(
            "New Code", on_click=lambda: regenerate_invite_code(group)
        ).tooltip(get_localization("gm_only_invite_code"))
        tour_create_group.add_step(
            new_button,
            get_localization("tour_create_group_new_code_button"),
        )
        new_button.set_enabled(is_gm)
        make_localisable(
            new_button,
            key="new_code",
        )

    with ui.grid().classes("grid-cols-3 lg:gap-4 gap-1") as grid:
        tour_create_group.add_step(
            grid,
            get_localization("tour_create_group_member_grid"),
        )
        for player in fetch_group_users(group):
            ui.label(player.nickname)
            has_sheet_in_consent = any(
                sheet for sheet in group_consent_sheets if sheet.user_id == player.id
            )
            make_localisable(
                ui.label("Part of Consent"),
                key="part_of_consent"
                if has_sheet_in_consent
                else "sheet_missing_in_consent",
            )
            if player.id == group.gm_user_id:
                ui.label("GM")
            else:
                remove_button = (
                    ui.button("Remove Player", color="red")
                    .on_click(lambda player=player: leave_group(group, player))
                    .tooltip(get_localization("gm_only_remove_player"))
                )
                remove_button.set_enabled(is_gm)
                make_localisable(
                    remove_button,
                    key="remove_player",
                )
