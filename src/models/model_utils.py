import os
from pathlib import Path

import bcrypt
from sqlmodel import Session, SQLModel, create_engine

from models.db_models import RPGGroup
from utlis import sanitize_name


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def add_and_refresh(session: Session, object: SQLModel):
    session.add(object)
    session.commit()
    session.refresh(object)


def add_all_and_refresh(session: Session, objects: list[SQLModel]):
    session.add_all(objects)
    session.commit()
    for obj in objects:
        session.refresh(obj)


sqlite_file_name = Path("db", "database.sqlite")
sqlite_file_name.parent.mkdir(exist_ok=True)

sqlite_url = os.getenv("DB_CONNECTION_STRING", f"sqlite:///{sqlite_file_name}")

engine = create_engine(sqlite_url, echo=False)


def generate_group_name_id(group: RPGGroup) -> str:
    return f"{sanitize_name(group.name)}-{group.id}"
