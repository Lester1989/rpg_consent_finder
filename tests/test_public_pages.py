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

pytest_plugins = ["nicegui.testing.plugin"]


async def test_news_page(user: User):
    await user.open("/news")
    await user.should_not_see("error_label")
    await user.should_not_see("notfound_label")


async def test_contents_page(user: User):
    await user.open("/content_trigger")
    await user.should_not_see("error_label")
    await user.should_not_see("notfound_label")


async def test_faq_page(user: User):
    await user.open("/faq")
    await user.should_not_see("error_label")
    await user.should_not_see("notfound_label")


async def test_playstyle_page(user: User):
    await user.open("/playstyle")
    await user.should_not_see("error_label")
    await user.should_not_see("notfound_label")
