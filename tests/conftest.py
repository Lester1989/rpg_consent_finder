import asyncio
import importlib
import os
import sys
from pathlib import Path
from typing import Callable, Generator

import pytest
from nicegui import ui
from nicegui.testing import User
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

# SRC_PATH = Path(__file__).resolve().parents[1] / "src"
# if str(SRC_PATH) not in sys.path:
#     sys.path.insert(0, str(SRC_PATH))

os.environ["DB_CONNECTION_STRING"] = "sqlite://"


@pytest.fixture(scope="session", autouse=True)
def in_memory_database() -> Generator[None, None, None]:
    model_utils = importlib.import_module("models.model_utils")
    seeder = importlib.import_module("models.seeder")
    admin_controller = importlib.import_module("controller.admin_controller")
    sheet_controller = importlib.import_module("controller.sheet_controller")
    util_controller = importlib.import_module("controller.util_controller")
    user_controller = importlib.import_module("controller.user_controller")
    importlib.import_module("models.db_models")

    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    modules_with_engine = [
        model_utils,
        sheet_controller,
        admin_controller,
        util_controller,
        seeder,
    ]

    for module in modules_with_engine:
        if hasattr(module, "engine"):
            module.engine = test_engine

    SQLModel.metadata.create_all(test_engine)

    seeder.seed_consent_questioneer()
    if not user_controller.get_user_by_account_and_password("testuser", "123123123"):
        default_user = user_controller.create_user_account("testuser", "123123123")
        default_user.nickname = "testuser"
        user_controller.update_user(default_user)

    yield

    SQLModel.metadata.drop_all(test_engine)
    test_engine.dispose()


@pytest.fixture
async def async_test_cleanup():  # sourcery skip: remove-redundant-if
    """Cleanup fixture that runs after each async test to allow background tasks to complete."""
    yield
    # Wait for pending asyncio tasks to complete
    current_task = asyncio.current_task()
    if pending := [
        task
        for task in asyncio.all_tasks()
        if task is not current_task and not task.done()
    ]:
        done, still_pending = await asyncio.wait(pending, timeout=2.0)

        # Handle tasks that didn't complete within timeout
        if still_pending:
            task_details = []
            for task in still_pending:
                coro = task.get_coro()
                task_info = (
                    f"{task.get_name()}: {coro}"
                    if hasattr(task, "get_name")
                    else repr(task)
                )
                task_details.append(task_info)
                task.cancel()  # Cancel to prevent leaking into other tests

            # Fail the test with details about hung tasks
            pytest.fail(
                f"Background tasks did not complete within 2s timeout:\n"
                + "\n".join(f"  - {detail}" for detail in task_details)
            )


@pytest.fixture
def component_page():
    """
    Factory fixture for creating minimal test pages with isolated components.

    Usage:
        async def test_my_component(user: User, component_page):
            @component_page('/test-component')
            def setup_page():
                my_component = MyComponent(some_arg="test")
                return my_component

            await user.open('/test-component')
            # ... test interactions
    """
    created_pages = []

    def create_page(path: str):
        """
        Decorator to create a minimal test page at the specified path.

        Args:
            path: URL path for the test page (e.g., '/test-component')

        Returns:
            Decorator function that wraps the component setup function
        """

        def decorator(setup_func: Callable):
            @ui.page(path)
            async def test_page():
                # Minimal page setup
                ui.label(f"Test Page: {path}").classes(
                    "hidden"
                )  # Hidden label for debugging
                # Call the setup function to create the component
                if asyncio.iscoroutinefunction(setup_func):
                    component = await setup_func()
                else:
                    component = setup_func()
                return component

            created_pages.append(path)
            return test_page

        return decorator

    yield create_page

    # Cleanup: Remove registered pages after test
    # Note: NiceGUI doesn't provide easy way to unregister pages,
    # but they'll be isolated per test run


@pytest.fixture
def test_user():
    """Fixture providing a test user instance for component testing."""
    user_controller = importlib.import_module("controller.user_controller")
    return user_controller.get_user_by_account_and_password("testuser", "123123123")


@pytest.fixture
def sample_consent_entry(test_user):
    """Fixture providing a sample consent entry for component testing."""
    sheet_controller = importlib.import_module("controller.sheet_controller")
    from models.db_models import ConsentEntry, ConsentStatus

    # Get or create a sheet for the test user
    if test_user.consent_sheets:
        sheet = test_user.consent_sheets[0]
    else:
        sheet = sheet_controller.create_new_consentsheet(test_user)

    # Get consent entries from the sheet
    if sheet.consent_entries:
        return sheet.consent_entries[0]

    # If no entries exist, return None (tests should handle this)
    return None
