from pathlib import Path
import os
from sqlmodel import create_engine

import string
import bcrypt

from models.db_models import RPGGroup


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def sanitize_name(name: str) -> str:
    return "".join(c for c in name if c in string.ascii_letters + string.digits).lower()


sqlite_file_name = Path("db", "database.sqlite")
sqlite_file_name.parent.mkdir(exist_ok=True)

sqlite_url = os.getenv("DB_CONNECTION_STRING", f"sqlite:///{sqlite_file_name}")

engine = create_engine(sqlite_url, echo=False)


def generate_group_name_id(group: RPGGroup) -> str:
    return f"{sanitize_name(group.name)}-{group.id}"
