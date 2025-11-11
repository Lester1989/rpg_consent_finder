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

from models.db_models import ConsentStatus  # type: ignore

pytest_plugins = ["nicegui.testing.plugin"]


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
    await user.should_see("logout_btn", retries=5)


async def test_create_and_delete_group(user: User):
    await login(user)
    await user.open("/home")
    # create group
    await user.should_see(marker="create_group_button")
    user.find("create_group_button").click()
    await user.should_see(marker="group_display_tab", retries=5)
    group_id = user.back_history[-1].split("/")[-1].split("?")[0].split("-")[-1]
    # get sheet_id from url
    user.find("home_link").click()
    await user.should_see(f"group_name_{group_id}")
    await user.should_see(f"delete_group_button_{group_id}")
    # delete group
    user.find(f"delete_group_button_{group_id}").click()
    await user.should_see("yes_button")
    user.find("yes_button").click()

    # confirm deletion
    await user.should_not_see(f"group_name_{group_id}", retries=5)


async def test_join_global_group(user: User):
    await login(user)
    await user.open("/home")
    # join global group
    await user.should_see("join_group_button")
    await user.should_see("group_join_code_input")
    user.find("group_join_code_input").type("global")
    user.find("join_group_button").click()
    await user.should_see("global 1")
    global_group_id_elements = user.find("global 1").elements
    assert len(global_group_id_elements) > 0, (
        "Could not find joined global group in home page"
    )
    global_group_id_first = global_group_id_elements.pop()
    assert global_group_id_first._text.startswith("global "), (
        global_group_id_first._to_dict()
    )
    global_group_id = global_group_id_first._text.split(" ")[-1]
    user.find(f"leave_group_button_{global_group_id}").click()
