import logging
from nicegui import ui, app

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
        edit_tab = ui.tab("Edit")
        general_tab = ui.tab("General")
        make_localisable(display_tab, key="display", language=lang)
        make_localisable(edit_tab, key="edit", language=lang)
        make_localisable(general_tab, key="general", language=lang)
    with ui.tab_panels(tabs, value=display_tab).classes("w-full") as panels:
        with ui.tab_panel(display_tab):
            sheet_display = SheetDisplayComponent(
                consent_sheets=group.consent_sheets,
                lang=lang,
            )
        if is_gm:
            with ui.tab_panel(edit_tab):
                SheetEditableComponent(group.gm_consent_sheet, lang)
        else:
            user_sheet = next(
                (sheet for sheet in group.consent_sheets if sheet.user_id == user.id),
                None,
            )
            with ui.tab_panel(edit_tab):
                if user_sheet:
                    SheetEditableComponent(user_sheet, lang)
                else:
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

        with ui.tab_panel(general_tab):
            general_tab_content(lang, group, is_gm)
    panels.on_value_change(lambda: sheet_display.content.refresh())


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
