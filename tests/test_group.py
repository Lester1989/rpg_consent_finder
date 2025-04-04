import asyncio
import logging
import time
from typing import Generator

import pytest

from nicegui.testing import User
from nicegui import ui
import sys

sys.path.append("src")
import os

os.environ["LOGLEVEL"] = "INFO"

from main import startup  # type: ignore
from models.db_models import ConsentStatus  # type: ignore

pytest_plugins = ["nicegui.testing.plugin"]


@pytest.fixture
def user(user: User) -> Generator[User, None, None]:
    startup()
    yield user


def marked_elements(user: User, marker: str):
    return {
        "".join(element._markers): element
        for element in user.find(marker).elements
        if element._markers
    }


async def login(
    user: User, account_name: str = "testuser", password: str = "123123123"
):
    await user.open("/login")
    await user.should_see("login_tab")
    user.find("login_tab").click()
    await user.should_see("login_account")
    await user.should_see("login_pw")
    user.find("login_account").type(account_name)
    user.find("login_pw").type(password)
    user.find("login_button").click()
    await user.should_see("logout_btn")


async def test_create_and_delete_group(user: User):
    await login(user)
    await user.open("/home")
    # create group
    await user.should_see("create_group_button")
    user.find("create_group_button").click()
    await user.should_see("group_display_tab")
    # get sheet_id from url
    group_id = user.back_history[-1].split("/")[-1].split("?")[0].split("-")[-1]
    user.find("home_link").click()
    await user.should_see(f"group_name_{group_id}")
    await user.should_see(f"delete_group_button_{group_id}")
    # delete group
    user.find(f"delete_group_button_{group_id}").click()
    await user.should_see("yes_button")
    user.find("yes_button").click()

    # confirm deletion
    await user.should_not_see(f"group_name_{group_id}", retries=2)


async def test_join_global_group(user: User):
    await login(user)
    await user.open("/home")
    # join global group
    await user.should_see("join_group_button")
    await user.should_see("group_join_code_input")
    user.find("group_join_code_input").type("global")
    user.find("join_group_button").click()
    await user.should_see("global")
    global_group_id = user.find("global ").elements.pop()._text.split(" ")[-1]
    user.find(f"leave_group_button_{global_group_id}").click()
