from typing import Generator

import pytest

from nicegui.testing import User
import sys

sys.path.append("src")
import os

# os.environ["LOGLEVEL"] = "DEBUG"

from main import startup  # type: ignore
from controller.sheet_controller import get_consent_sheet_by_id  # type: ignore
from controller.user_controller import get_user_by_id_name  # type: ignore

pytest_plugins = ["nicegui.testing.plugin"]


@pytest.fixture
def user(user: User) -> Generator[User, None, None]:
    startup()
    yield user


async def login(user: User):
    await user.open("/login")
    # await user.should_see("register_tab")
    # user.find("register_tab").click()
    # await user.should_see("register_account")
    # user.find("register_account").type("testuser")
    # user.find("register_pw").type("123123123")
    # user.find("register_pw_confirm").type("123123123")
    # user.find("register_button").click()
    await user.should_see("login_tab")
    user.find("login_tab").click()
    await user.should_see("login_account")
    await user.should_see("login_pw")
    user.find("login_account").type("testuser")
    user.find("login_pw").type("123123123")
    user.find("login_button").click()
    # await user.should_see("welcome_nickname")
    # user.find("welcome_nickname").type("testuser")
    # user.find("welcome_save").click()
    await user.should_see("logout_btn")


async def test_create_and_delete_sheet(user: User, caplog) -> None:
    await login(user)
    await user.should_see("new_sheet_button")
    user.find("new_sheet_button").click()
    await user.should_see("edit_tab")
    user.find("edit_tab").click()
    await user.should_see("sheet_name_input")
    user.find("sheet_name_input").type("testsheet")
    # get sheet_id from url
    sheet_id = user.back_history[-1].split("/")[-1].split("?")[0]
    user.find("home_link").click()
    db_check_sheet = get_consent_sheet_by_id("custom-testuser", int(sheet_id))
    db_check_user = get_user_by_id_name("custom-testuser")
    assert db_check_sheet is not None, f"Sheet not found with id {sheet_id}"
    assert db_check_user is not None, "User not found with id custom-testuser"
    await user.should_see(f"delete_sheet_button-{sheet_id}")
    user.find(f"delete_sheet_button-{sheet_id}").click()
    await user.should_see("yes_button")
    user.find("yes_button").click()
    await user.should_not_see(f"delete_sheet_button-{sheet_id}")
