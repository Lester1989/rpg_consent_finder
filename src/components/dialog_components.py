"""Reusable NiceGUI confirmation dialogs with localisation support."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from nicegui import ui

from localization.language_manager import make_localisable
from services.async_utils import ensure_awaitable


async def _handle_confirmation(
    dialog: ui.dialog,
    on_confirm: Callable[[], Any],
    *,
    refresh_after: bool,
) -> None:
    """Close the dialog, execute the action, and optionally refresh the page."""

    dialog.close()
    await ensure_awaitable(on_confirm())
    if refresh_after:
        ui.navigate.reload()


def open_confirmation_dialog(
    key: str,
    on_confirm: Callable[[], Any],
    *,
    refresh_after: bool = False,
) -> None:
    """Render a localized confirmation dialog before executing an action."""

    with ui.dialog() as dialog, ui.card():
        make_localisable(ui.label(), key=f"{key}_confirm")
        with ui.row():

            async def _on_yes() -> None:
                await _handle_confirmation(
                    dialog,
                    on_confirm,
                    refresh_after=refresh_after,
                )

            yes_button = ui.button("Yes", on_click=_on_yes)
            no_button = ui.button("No", on_click=dialog.close)
            yes_button.mark("yes_button")
            no_button.mark("no_button")
            make_localisable(yes_button, key="yes")
            make_localisable(no_button, key="no")
    dialog.open()


def confirm_before(
    key: str,
    refresh_after: bool,
    func: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> None:
    """Backwards compatible wrapper that mirrors the historic helper signature."""

    open_confirmation_dialog(
        key,
        lambda: func(*args, **kwargs),
        refresh_after=refresh_after,
    )
