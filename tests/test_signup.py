from typing import Generator

import pytest

from nicegui.testing import User
import sys

sys.path.append("src")
from main import startup

pytest_plugins = ["nicegui.testing.plugin"]


@pytest.fixture
def user(user: User) -> Generator[User, None, None]:
    startup()
    yield user


async def test_login_wrong_pw(user: User, caplog) -> None:
    await user.open("/login")
    await user.should_see("login_account")
    await user.should_see("login_pw")
    user.find("login_account").type("testuser")
    user.find("login_pw").type("wrong")
    user.find("login_button").click()
    await user.should_not_see("logout_btn")


async def test_login_success(user: User, caplog) -> None:
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
    # assert len(caplog.records) == 1


async def test_signup(user: User, caplog) -> None:
    await user.open("/login")
    await user.should_see("register_tab")
    user.find("register_tab").click()
    await user.should_see("register_account")
    user.find("register_account").type("temptestuser")
    user.find("register_pw").type("123123123")
    user.find("register_pw_confirm").type("123123123")
    user.find("register_button").click()
    user.find("login_tab").click()
    await user.should_see("login_account")
    user.find("login_account").type("temptestuser")
    user.find("login_pw").type("123123123")
    user.find("login_button").click()
    await user.should_see("logout_btn")
    await user.should_see("welcome_nickname")
    user.find("welcome_nickname").type("testuser")
    user.find("welcome_save").click()
    await user.should_see("delete_account_button")
    user.find("delete_account_button").click()
    await user.should_see("yes_button")
    user.find("yes_button").click()
    await user.should_see("local_sign_in_button")
    await user.should_not_see("home_link")
    # assert len(caplog.records) == 1
