"""
Component tests for ConsentEntryComponent.

These tests create minimal pages with just the component being tested,
allowing for isolated testing without full page context.
"""

import pytest
from nicegui import ui
from nicegui.testing import User

from components.consent_entry_component import ConsentEntryComponent
from models.db_models import ConsentStatus
from tests.utils import marked_elements

pytest_plugins = ["nicegui.testing.plugin"]


async def test_consent_entry_renders(
    user: User, component_page, test_user, sample_consent_entry
):
    """Test that ConsentEntryComponent renders correctly."""
    if not sample_consent_entry:
        pytest.skip("No consent entry available")

    @component_page("/test-consent-entry")
    def setup():
        with ui.column().classes("w-full"):
            component = ConsentEntryComponent(sample_consent_entry, test_user)
            return component

    await user.open("/test-consent-entry")

    # Check that the toggle element exists
    await user.should_see(f"toggle_{sample_consent_entry.consent_template.id}")

    # Check that the comment toggle exists
    await user.should_see(f"comment_toggle_{sample_consent_entry.consent_template.id}")


async def test_consent_entry_toggle_changes(
    user: User, component_page, test_user, sample_consent_entry
):
    """Test that changing the toggle updates the consent entry."""
    if not sample_consent_entry:
        pytest.skip("No consent entry available")

    @component_page("/test-consent-toggle")
    def setup():
        with ui.column().classes("w-full"):
            component = ConsentEntryComponent(sample_consent_entry, test_user)
            return component

    await user.open("/test-consent-toggle")

    # Find the toggle element
    toggle = marked_elements(user, "🟠").get(
        f"toggle_{sample_consent_entry.consent_template.id}"
    )

    toggle.set_value(ConsentStatus.unknown)
    # Initial state should be unknown
    assert sample_consent_entry.preference == ConsentStatus.unknown

    # Click to change status (assuming toggle cycles through statuses)
    toggle.set_value(ConsentStatus.maybe)

    # Verify that the preference was updated
    assert sample_consent_entry.preference == ConsentStatus.maybe

    toggle.set_value(ConsentStatus.unknown)
    # Initial state should be unknown
    assert sample_consent_entry.preference == ConsentStatus.unknown

    # Set back to initial state
    toggle.set_value(ConsentStatus.unknown)

    # Verify that the preference was reset
    assert sample_consent_entry.preference == ConsentStatus.unknown


async def test_consent_entry_comment_visibility(
    user: User, component_page, test_user, sample_consent_entry
):
    """Test that comment input shows/hides based on toggle."""
    if not sample_consent_entry:
        pytest.skip("No consent entry available")

    @component_page("/test-consent-comment")
    def setup():
        with ui.column().classes("w-full"):
            component = ConsentEntryComponent(sample_consent_entry, test_user)
            return component

    await user.open("/test-consent-comment")

    # Comment input should initially be hidden
    comment_toggle = user.find(
        f"comment_toggle_{sample_consent_entry.consent_template.id}"
    )

    # Initially, comment input should not be visible
    await user.should_not_see(
        f"comment_input_{sample_consent_entry.consent_template.id}"
    )
    # Toggle to show comment
    comment_toggle.click()

    # Now comment input should be visible
    await user.should_see(f"comment_input_{sample_consent_entry.consent_template.id}")


async def test_multiple_consent_entries(user: User, component_page, test_user):
    """Test rendering multiple consent entry components."""
    from controller import sheet_controller
    from models.db_models import ConsentEntry

    @component_page("/test-multiple-consents")
    def setup():
        with ui.column().classes("w-full"):
            # Get sheet and entries
            if test_user.consent_sheets:
                sheet = test_user.consent_sheets[0]
                entries = sheet.consent_entries

                # Render multiple components
                for entry in entries[:3]:  # Test with first 3 entries
                    ConsentEntryComponent(entry, test_user)

    await user.open("/test-multiple-consents")

    # Verify multiple components rendered
    # (Specific assertions depend on your data)
