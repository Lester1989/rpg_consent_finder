import importlib
import os
import sys
from pathlib import Path
from typing import Generator

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

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
