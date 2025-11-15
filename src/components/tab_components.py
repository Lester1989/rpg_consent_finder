"""Shared helpers for constructing localised NiceGUI tabs and panels."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Optional

from nicegui import app, ui

from localization.language_manager import make_localisable


@dataclass(frozen=True)
class TabSpec:
    """Describe a tab including localisation and optional marker overrides."""

    value: str
    localization_key: str
    title: Optional[str] = None
    mark: Optional[str] = None


def create_localised_tabs(
    tab_specs: Sequence[TabSpec],
    *,
    marker_prefix: str = "",
) -> tuple[ui.tabs, dict[str, ui.tab]]:
    """Build a tab bar with localised labels and optional custom markers."""
    with ui.tabs() as tabs:
        named_tabs: dict[str, ui.tab] = {}
        for spec in tab_specs:
            label = spec.title or spec.value
            tab = ui.tab(label)
            mark_name = spec.mark or (
                f"{marker_prefix}{spec.value}_tab"
                if marker_prefix
                else f"{spec.value}_tab"
            )
            tab.mark(mark_name)
            make_localisable(tab, key=spec.localization_key)
            named_tabs[spec.value] = tab
    return tabs, named_tabs


def create_tab_panels(
    tabs: ui.tabs,
    named_tabs: dict[str, ui.tab],
    storage_key: str,
    default_key: str,
    *,
    panel_classes: str = "w-full",
) -> ui.tab_panels:
    """Return a `tab_panels` element initialised with the stored active tab."""
    stored_value = app.storage.user.get(storage_key, default_key)
    selected_tab = (
        named_tabs.get(stored_value)
        or named_tabs.get(default_key)
        or next(iter(named_tabs.values()))
    )
    return ui.tab_panels(tabs, value=selected_tab).classes(panel_classes)
