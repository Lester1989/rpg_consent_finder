import logging
from nicegui import ui, app

from components.preference_ordered_sheet_display_component import (
    PreferenceOrderedSheetDisplayComponent,
)
from components.sheet_display_component import SheetDisplayComponent
from components.sheet_editable_component import SheetEditableComponent

from localization.language_manager import get_localization, make_localisable
from models.db_models import (
    RPGGroup,
    User,
)
from models.controller import (
    create_new_group,
    get_group_by_name_id,
    get_user_by_id_name,
    leave_group,
    regenerate_invite_code,
    update_group,
    assign_consent_sheet_to_group,
)
from models.model_utils import generate_group_name_id


SHOW_TAB_STORAGE_KEY = "group_show_tab"


def reload_after(func, *args, **kwargs):
    func(*args, **kwargs)
    content.refresh()


@ui.refreshable
def content(lang: str = "en", group_name_id: str = None, **kwargs):
    user: User = get_user_by_id_name(app.storage.user.get("user_id"))
    if not user:
        ui.navigate.to(f"/welcome?lang={lang}")
        return
    logging.debug(f"{group_name_id}")
    if not group_name_id:
        group = create_new_group(user)
        group_name_id = generate_group_name_id(group)
        ui.navigate.to(f"/groupconsent/{group_name_id}?lang={lang}")
        return
    group: RPGGroup = get_group_by_name_id(group_name_id)
    is_gm = user.id == group.gm_user_id
    with ui.tabs() as tabs:
        display_tab = ui.tab("Consent")
        ordered_topics_tab = ui.tab("ordered_topics")
        edit_tab = ui.tab("Edit")
        general_tab = ui.tab("General")
        make_localisable(display_tab, key="display", language=lang)
        make_localisable(edit_tab, key="edit", language=lang)
        make_localisable(ordered_topics_tab, key="ordered_topics", language=lang)
        make_localisable(general_tab, key="general", language=lang)
        named_tabs = {
            "display": display_tab,
            "ordered_topics": ordered_topics_tab,
            "edit": edit_tab,
            "general": general_tab,
        }

    show_tab = app.storage.user.get(SHOW_TAB_STORAGE_KEY, "display")
    with ui.tab_panels(tabs, value=named_tabs.get(show_tab, display_tab)).classes(
        "w-full"
    ) as panels:
        with ui.tab_panel(display_tab):
            sheet_display = SheetDisplayComponent(
                consent_sheets=group.consent_sheets,
                lang=lang,
            )
        with ui.tab_panel(ordered_topics_tab):
            ordered_topics_display = PreferenceOrderedSheetDisplayComponent(
                consent_sheets=group.consent_sheets, lang=lang
            )
        with ui.tab_panel(edit_tab):
            sheet_editor = edit_tab_content(lang, user, group, is_gm)

        with ui.tab_panel(general_tab):
            general_tab_content(lang, group, is_gm)
    panels.on_value_change(
        lambda x: storage_show_tab_and_refresh(
            x.value, sheet_display, ordered_topics_display, sheet_editor
        )
    )


def edit_tab_content(lang: str, user: User, group: RPGGroup, is_gm: bool):
    if is_gm:
        sheet_editor = SheetEditableComponent(group.gm_consent_sheet, lang)
    else:
        if user_sheet := next(
            (sheet for sheet in group.consent_sheets if sheet.user_id == user.id),
            None,
        ):
            sheet_editor = SheetEditableComponent(user_sheet, lang)
        else:
            sheet_editor = None
            make_localisable(
                ui.label("No Consent Sheet assigned yet"),
                key="no_sheet_assigned",
                language=lang,
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
    app.storage.user[SHOW_TAB_STORAGE_KEY] = tab
    logging.debug(f"storage_show_tab_and_refresh {tab}")
    if tab == "display":
        category_topics_display.content.refresh()
    elif tab == "ordered_topics":
        ordered_topics_display.content.refresh()
    elif tab == "edit" and sheet_editor:
        sheet_editor.content.refresh()


def general_tab_content(lang: str, group: RPGGroup, is_gm: bool):
    group_name_input = (
        ui.input("Group Name")
        .bind_value(group, "name")
        .on("focusout", lambda _: update_group(group))
        .classes("lg:w-1/2 w-full")
    )
    group_name_input.set_enabled(is_gm)
    make_localisable(
        group_name_input,
        key="group_name",
        language=lang,
    )
    with ui.row():
        make_localisable(
            ui.label("Group Join Code"),
            key="group_join_code",
            language=lang,
        )
        ui.label(group.invite_code).bind_text(group, "invite_code")
        new_button = ui.button(
            "New Code", on_click=lambda: regenerate_invite_code(group)
        ).tooltip(get_localization("gm_only_invite_code", lang))
        new_button.set_enabled(is_gm)
        make_localisable(
            new_button,
            key="new_code",
            language=lang,
        )

    with ui.grid().classes("grid-cols-3 lg:gap-4 gap-1"):
        for player in group.users:
            ui.label(player.nickname)
            has_sheet_in_consent = any(
                sheet for sheet in group.consent_sheets if sheet.user_id == player.id
            )
            make_localisable(
                ui.label("Part of Consent"),
                key="part_of_consent"
                if has_sheet_in_consent
                else "sheet_missing_in_consent",
                language=lang,
            )
            if player.id == group.gm_user_id:
                ui.label("GM")
            else:
                remove_button = (
                    ui.button("Remove Player", color="red")
                    .on_click(lambda player=player: leave_group(group, player))
                    .tooltip(get_localization("gm_only_remove_player", lang))
                )
                remove_button.set_enabled(is_gm)
                make_localisable(
                    remove_button,
                    key="remove_player",
                    language=lang,
                )
