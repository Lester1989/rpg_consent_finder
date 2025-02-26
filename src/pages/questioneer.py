from nicegui import ui, app

from components.consent_legend_component import consent_legend_component
from components.sheet_display_component import SheetDisplayComponent
from components.sheet_editable_component import SheetEditableComponent
from components.preference_ordered_sheet_display_component import (
    PreferenceOrderedSheetDisplayComponent,
)

from guided_tour import NiceGuidedTour
from localization.language_manager import get_localization, make_localisable
from models.db_models import (
    User,
)
from models.controller import (
    assign_consent_sheet_to_group,
    get_consent_sheet_by_id,
    create_new_consentsheet,
    get_user_from_storage,
    unassign_consent_sheet_from_group,
)
import logging

SHOW_TAB_STORAGE_KEY = "sheet_show_tab"


@ui.refreshable
def content(questioneer_id: str = None, lang: str = "en", **kwargs):
    tour_create_sheet = NiceGuidedTour(
        storage_key="tour_create_sheet_progress", page_suffix="consentsheet"
    )
    tour_share_sheet = NiceGuidedTour(
        storage_key="tour_share_sheet_progress", page_suffix="consentsheet"
    )
    user: User = get_user_from_storage()
    logging.debug(f"{questioneer_id}")
    if not user:
        ui.navigate.to(f"/welcome?lang={lang}")
        return
    if not questioneer_id:
        sheet = create_new_consentsheet(user)
        ui.navigate.to(f"/consentsheet/{sheet.id}?show=edit&lang={lang}")
        return
    else:
        sheet = get_consent_sheet_by_id(
            app.storage.user.get("user_id"), int(questioneer_id)
        )

    consent_legend_grid = consent_legend_component(lang)
    tour_create_sheet.add_step(
        consent_legend_grid,
        get_localization("tour_create_sheet_consent_legend_grid", lang),
    )
    ui.separator()

    with ui.tabs() as tabs:
        display_tab = ui.tab("display")
        ordered_topics_tab = ui.tab("ordered_topics")
        edit_tab = ui.tab("edit")
        groups_tab = ui.tab("groups")
        tour_create_sheet.add_step(
            edit_tab, get_localization("tour_create_sheet_edit_tab", lang)
        )
        tour_create_sheet.add_step(
            display_tab, get_localization("tour_create_sheet_display_tab", lang)
        )
        tour_create_sheet.add_step(
            ordered_topics_tab,
            get_localization("tour_create_sheet_ordered_topics_tab", lang),
        )
        tour_create_sheet.add_step(
            groups_tab, get_localization("tour_create_sheet_groups_tab", lang)
        )
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
            tour_create_sheet.add_step(
                sheet_editor,
                get_localization("tour_create_sheet_sheet_editor", lang),
                lambda: tabs.set_value(edit_tab),
            )
            tour_share_sheet.add_step(
                sheet_editor,
                get_localization("tour_share_sheet_sheet_editor", lang),
                lambda: tabs.set_value(edit_tab),
            )
            tour_share_sheet.add_step(
                sheet_editor.share_button,
                get_localization("tour_share_sheet_share_button", lang),
                lambda: tabs.set_value(edit_tab),
            )
            tour_share_sheet.add_step(
                ordered_topics_tab,
                get_localization("tour_share_sheet_ordered_topics_tab", lang),
            )
            tour_share_sheet.add_step(
                ordered_topics_display.share_expansion,
                get_localization("tour_share_sheet_share_expansion", lang),
                lambda: tabs.set_value(ordered_topics_tab),
            )
            tour_share_sheet.add_step(
                ordered_topics_display.share_image,
                get_localization("tour_share_sheet_share_image", lang),
                lambda: ordered_topics_display.share_expansion.set_value(True),
            )

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
                create_group_from_sheet_button = ui.button(
                    get_localization("create_group_from_sheet", lang),
                    on_click=lambda: ui.notify("Not implemented yet", type="negative"),
                )
                tour_create_sheet.add_step(
                    create_group_from_sheet_button,
                    get_localization(
                        "tour_create_sheet_create_group_from_sheet_button", lang
                    ),
                    lambda: tabs.set_value(groups_tab),
                )

    panels.on_value_change(
        lambda x: storage_show_tab_and_refresh(
            x.value, category_topics_display, ordered_topics_display, sheet_editor
        )
    )
    active_tour = app.storage.user.get("active_tour", "")
    if active_tour == "create_sheet":
        ui.timer(0.5, tour_create_sheet.start_tour, once=True)
    elif active_tour == "share_sheet":
        ui.timer(0.5, tour_share_sheet.start_tour, once=True)


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
