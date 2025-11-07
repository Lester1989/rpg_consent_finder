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

os.environ["LOGLEVEL"] = "DEBUG"

from models.db_models import ConsentStatus  # type: ignore

pytest_plugins = ["nicegui.testing.plugin"]


def marked_elements(user: User, marker: str):
    return {
        "".join(element._markers): element
        for element in user.find(marker).elements
        if element._markers
    }


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
    await user.should_see("logout_btn", retries=5)


async def login_and_create_sheet(user: User):
    await login(user)
    await user.should_see("new_sheet_button", retries=5)
    user.find("new_sheet_button").click()
    await user.should_see("sheet_tabs", retries=5)
    user.find("sheet_tabs").elements.pop().set_value(
        user.find("edit_tab").elements.pop()._props["name"]
    )
    # get sheet_id from url
    sheet_id = user.back_history[-1].split("/")[-1].split("?")[0]
    # check if created
    user.find("home_link").click()
    await user.should_see(f"details_button-{sheet_id}", retries=5)
    return sheet_id


async def delete_sheet(user: User, sheet_id: str):
    user.find("home_link").click()
    await user.should_see(f"delete_sheet_button-{sheet_id}", retries=5)
    user.find(f"delete_sheet_button-{sheet_id}").click()
    await user.should_see("yes_button", retries=5)
    user.find("yes_button").click()
    await user.should_not_see(f"delete_sheet_button-{sheet_id}", retries=5)


async def test_create_and_delete_sheet(user: User, caplog) -> None:
    sheet_id = await login_and_create_sheet(user)
    await delete_sheet(user, sheet_id)


async def test_public_sheet(user: User, caplog) -> None:
    sheet_id = await login_and_create_sheet(user)
    user.find(f"details_button-{sheet_id}").click()
    await user.should_see("sheet_tabs")
    # goto edit
    user.find("sheet_tabs").elements.pop().set_value(
        user.find("edit_tab").elements.pop()._props["name"]
    )
    # set public
    await user.should_see("share_button", retries=5)
    user.find("share_button").click()

    # go to display
    user.find("sheet_tabs").elements.pop().set_value(
        user.find("display_tab").elements.pop()._props["name"]
    )
    await user.should_see("share_link", retries=5)
    user.find("share_link").click()
    await user.should_see("public_sheet_separator", retries=5)
    public_sheet_url = user.back_history[-1]
    await user.should_see("logout_btn", retries=5)
    user.find("logout_btn").click()
    user.open(public_sheet_url)
    await user.should_see("public_sheet_separator", retries=5)
    await user.should_not_see("logout_btn", retries=5)
    await login(user)
    await delete_sheet(user, sheet_id)


async def test_modify_sheet_by_category(user: User, caplog) -> None:
    sheet_id = await login_and_create_sheet(user)
    user.find(f"details_button-{sheet_id}").click()
    await user.should_see("sheet_tabs")
    user.find("sheet_tabs").elements.pop().set_value(
        user.find("edit_tab").elements.pop()._props["name"]
    )
    await user.should_see("category_toggle_horror")
    # set category to maybe
    marked_elements(user, "🟠").get("category_toggle_horror").set_value(
        ConsentStatus.maybe
    )
    await asyncio.sleep(2)
    # goto ordered_topics
    user.find("sheet_tabs").elements.pop().set_value(
        user.find("ordered_topics_tab").elements.pop()._props["name"]
    )
    # count limits
    await user.should_see("status_expansion_unknown", retries=5)
    await user.should_see("status_expansion_maybe", retries=5)
    await delete_sheet(user, sheet_id)


async def test_modify_sheet_comment(user: User, caplog) -> None:
    sheet_id = await login_and_create_sheet(user)
    user.find(f"details_button-{sheet_id}").click()
    await user.should_see("sheet_tabs")
    # gotot edit
    user.find("sheet_tabs").elements.pop().set_value(
        user.find("edit_tab").elements.pop()._props["name"]
    )
    # add comment to entry
    await user.should_see("sheet_comment_input")
    user.find("sheet_comment_input").type("comment_abc")
    user.find("sheet_comment_input").trigger("focusout")
    await asyncio.sleep(2)
    # goto display
    user.find("sheet_tabs").elements.pop().set_value(
        user.find("display_tab").elements.pop()._props["name"]
    )
    # check if comment is displayed
    await user.should_see("sheet_comments_display", retries=5)
    # display_comment = user.find("custom_consent_entry_comment").elements.pop()
    # assert display_comment._text == "comment_abc", list(display_comment.descendants())

    await delete_sheet(user, sheet_id)


async def test_modify_sheet_custom_entry(user: User, caplog) -> None:
    sheet_id = await login_and_create_sheet(user)
    user.find(f"details_button-{sheet_id}").click()
    await user.should_see("sheet_tabs")
    # goto edit
    user.find("sheet_tabs").elements.pop().set_value(
        user.find("edit_tab").elements.pop()._props["name"]
    )
    # add custom entry
    await user.should_see("add_custom_entry_button")
    user.find("add_custom_entry_button").click()
    await user.should_see("custom_consent_entry_content")
    # modify custom entry
    user.find("custom_consent_entry_content").type("custom_abc")
    user.find("custom_consent_entry_content").trigger("focusout")
    user.find("custom_consent_entry_toggle").elements.pop().set_value(ConsentStatus.no)
    user.find("custom_consent_entry_comment_toggle").click()
    await user.should_see("custom_consent_entry_comment")
    user.find("custom_consent_entry_comment").type("custom_comment_abc")
    user.find("custom_consent_entry_comment").trigger("focusout")

    # goto ordered_topics
    user.find("sheet_tabs").elements.pop().set_value(
        user.find("ordered_topics_tab").elements.pop()._props["name"]
    )
    # count limits
    await user.should_see("status_expansion_no")
    await user.should_see("status_expansion_unknown")
    # check comments
    await user.should_see("custom_abc")
    await user.should_see("custom_comment_abc")
    # goto edt
    user.find("sheet_tabs").elements.pop().set_value(
        user.find("edit_tab").elements.pop()._props["name"]
    )
    # delete custom entry
    user.find("custom_consent_entry_content").clear()
    user.find("custom_consent_entry_content").trigger("focusout")
    await asyncio.sleep(2)

    # goto ordered_topics
    user.find("sheet_tabs").elements.pop().set_value(
        user.find("ordered_topics_tab").elements.pop()._props["name"]
    )
    user.find("sheet_tabs").elements.pop().set_value(
        user.find("display_tab").elements.pop()._props["name"]
    )
    # count limits
    await user.should_not_see("status_expansion_no")
    await delete_sheet(user, sheet_id)
