import logging
from nicegui import ui, app

from components.faq_element_component import FAQElementComponent

faq = [
    ("What is this?", "This is a consent management system."),
    ("What does it do?", "It helps you manage your consent sheets."),
    ("How do I use it?", "You can create\n a new consent sheet\n or join a group."),
    (
        "How do I use it?",
        "You can create a new consent sheet or join a group.\n\n You can create a new consent sheet or join a group. You can create a new consent sheet or join a group. You can create a new consent sheet or join a group. You can create a new consent sheet or join a group. You can create a new consent sheet or join a group.",
    ),
]


@ui.refreshable
def content(**kwargs):
    with ui.grid(columns=2).classes("gap-4 mx-auto"):
        for question, answer in faq:
            FAQElementComponent(question, answer)
