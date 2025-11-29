import asyncio
import sys
import os

from nicegui.testing import User

sys.path.append("src")
os.environ["LOGLEVEL"] = "DEBUG"

from controller.playfun_controller import get_playfun_answers_for_user
from controller.user_controller import get_user_by_account_and_password

pytest_plugins = ["nicegui.testing.plugin"]


async def login(user: User):
    """Login helper function"""
    await user.open("/login")
    await user.should_see("login_tab")
    user.find("login_tab").click()
    await user.should_see("login_account")
    await user.should_see("login_pw")
    user.find("login_account").type("testuser")
    user.find("login_pw").type("123123123")
    user.find("login_button").click()
    await user.should_see("logout_btn", retries=5)


async def test_playstyle_slider_changes_persisted(user: User) -> None:
    """Test that playstyle slider changes are persisted"""
    await login(user)

    # Get the user object to check database state
    test_user = get_user_by_account_and_password("testuser", "123123123")
    assert test_user is not None

    # Navigate to playstyle page
    await user.open("/playstyle")

    # Should see the questions tab by default
    await user.should_see("❤️")
    await user.should_see("🤮")
    await user.should_see("save_button")
    await user.should_see("slider-8")

    # Find sliders - they should exist
    sliders_interaction = user.find("slider-1")

    # Change a slider value by setting it directly
    # Check if the slider value persisted in UI
    sliders_interaction.trigger("update:modelValue", -2)

    user.find("save_button").click()

    # Check if the database was updated after slider change
    answers_after_change = get_playfun_answers_for_user(test_user)

    # The answer should have been created/updated in the database
    changed_answer = next(
        (answer for answer in answers_after_change if answer.question_id == 1), None
    )
    assert changed_answer is not None, "No answer found for question ID 1 after change"
    assert changed_answer.rating == -2, (
        f"Database was not updated correctly after slider change. Expected rating -2, got {changed_answer.rating}"
    )

    await user.should_see("playfun_plot_tab")
    user.find("playfun_plot_tab").click()
    await asyncio.sleep(0.5)
    await user.should_see("top_styles")
    await user.should_see("Top 3: discovery, expression, fantasy")

    sliders_interaction.trigger("update:modelValue", 0)

    user.find("save_button").click()

    answers_after_restore = get_playfun_answers_for_user(test_user)
    restored_answer = next(
        (answer for answer in answers_after_restore if answer.question_id == 1), None
    )
    assert restored_answer is not None, (
        "No answer found for question ID 1 after restore"
    )
    assert restored_answer.rating == 0, (
        f"Database was not updated correctly after slider restore. Expected rating 0, got {restored_answer.rating}"
    )

    # Navigate away and back to verify UI persistence
    await user.open("/home")
    await user.should_see("logout_btn")

    # Go back to playstyle page
    await user.open("/playstyle")
    await user.should_see("❤️")

    # Switch to plot tab to verify the output changed
    await user.should_see("playfun_plot_tab")
    user.find("playfun_plot_tab").click()

    # Should see the plot content
    await asyncio.sleep(1)
    # The plot should be rendered (we can't easily verify the exact values,
    # but we can check that it doesn't error)
