import logging
from nicegui import app, ui

from components.consent_display_component import ConsentDisplayComponent

from models.db_models import (
    ConsentTemplate,
    ConsentSheet,
)
from models.controller import (
    duplicate_sheet,
    get_all_consent_topics,
)


class SheetDisplayComponent(ui.grid):
    sheet: ConsentSheet = None
    sheets: list[ConsentSheet] = None
    redact_name: bool

    def __init__(
        self,
        consent_sheet: ConsentSheet = None,
        consent_sheets: list[ConsentSheet] = None,
        redact_name: bool = False,
    ):
        super().__init__()
        if consent_sheet is None:
            self.sheets = consent_sheets
        else:
            self.sheet = consent_sheet

        self.redact_name = redact_name
        self.topics: list[ConsentTemplate] = get_all_consent_topics()
        self.categories = sorted(list(set(topic.category for topic in self.topics)))
        self.grouped_topics = {
            category: [
                template for template in self.topics if template.category == category
            ]
            for category in self.categories
        }
        self.content()

    @property
    def sheet_name(self):
        if self.redact_name:
            return f"Consent Sheet"
        return (
            self.sheet.human_name
            if self.sheet
            else f"Consent of {len(self.sheets)} players"
        )

    @property
    def sheet_comments(self):
        return (
            self.sheet.comment
            if self.sheet
            else "\n---\n".join(sheet.comment for sheet in self.sheets if sheet.comment)
        )

    def button_duplicate(self, user_id_name):
        logging.debug(f"Duplicating {self.sheet}")
        duplicate = duplicate_sheet(self.sheet, user_id_name)
        if duplicate:
            ui.navigate.to("/home")
            ui.notify(f"Sheet {duplicate.human_name} duplicated")
        else:
            ui.notify("Sheet could not be duplicated")

    @ui.refreshable
    def content(self):
        logging.debug(f"SheetDisplayComponent {self.sheet} {self.sheets}")
        self.clear()
        with self.classes("lg:grid-cols-3 grid-cols-1"):
            ui.label(self.sheet_name)
            ui.label(self.sheet_comments)
            if self.sheet and self.sheet.public_share_id:
                with ui.expansion("Share Link"):
                    ui.link(
                        "Link to this sheet",
                        f"/consent/{self.sheet.public_share_id}/{self.sheet.id}",
                    )
                    ui.image(
                        f"/api/qr?share_id={self.sheet.public_share_id}&sheet_id={self.sheet.id}"
                    )

            else:
                ui.label("")

            for category in self.categories:
                templates = self.grouped_topics[category]
                lookup_consents = {
                    template.id: [
                        sheet.consent_entries_dict.get(template.id)
                        for sheet in self.sheets or [self.sheet]
                    ]
                    for template in templates
                }
                with ui.card().classes(f"row-span-{(len(templates) // 3) + 1} "):
                    with ui.row().classes("w-full pt-6"):
                        ui.label(category).classes("text-xl")
                        for topic in templates:
                            ConsentDisplayComponent(lookup_consents[topic.id])
            user_id_name = app.storage.user.get("user_id")
            if not user_id_name:
                ui.label("Login to Duplicate")
                return
            if self.sheet:
                ui.button(
                    "Duplicate",
                    on_click=lambda: self.button_duplicate(user_id_name),
                )
