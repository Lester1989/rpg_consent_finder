from pathlib import Path
import os
from sqlmodel import create_engine

import string
import bcrypt

from models.db_models import RPGGroup
from utlis import sanitize_name


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


sqlite_file_name = Path("db", "database.sqlite")
sqlite_file_name.parent.mkdir(exist_ok=True)

sqlite_url = os.getenv("DB_CONNECTION_STRING", f"sqlite:///{sqlite_file_name}")

engine = create_engine(sqlite_url, echo=False)


def generate_group_name_id(group: RPGGroup) -> str:
    return f"{sanitize_name(group.name)}-{group.id}"
