import logging
import random
import time

from nicegui import app
from sqlmodel import Session, delete, select

from models.db_models import (
    ConsentEntry,
    ConsentSheet,
    RPGGroup,
    User,
    UserLogin,
)
from models.model_utils import add_and_refresh, check_password, engine, hash_password
from utlis import sanitize_name


def get_user_by_account_and_password(account_name: str, password: str) -> User:
    logging.getLogger("content_consent_finder").debug(
        f"get_user_by_account_and_password {account_name} and <redacted {len(password) if password else -1} chars>"
    )
    with Session(engine) as session:
        user_login = session.exec(
            select(UserLogin).where(UserLogin.account_name == account_name)
        ).first()
        logging.getLogger("content_consent_finder").debug(f"found {user_login}")
        if user_login and check_password(password, user_login.password_hash):
            return session.get(User, user_login.user_id)
        logging.getLogger("content_consent_finder").debug("login failed ")
        time.sleep(random.random() * 0.1)  # prevent timing attacks
        return None


def create_user_account(account_name: str, password: str) -> User:
    logging.getLogger("content_consent_finder").debug(
        f"create_user_account {account_name}"
    )
    with Session(engine) as session:
        if session.exec(
            select(UserLogin).where(UserLogin.account_name == account_name)
        ).first():
            raise ValueError("AccountName already in use")
        user = User(id_name=f"custom-{account_name}", nickname="")
        add_and_refresh(session, user)
        user_login = UserLogin(
            user_id=user.id,
            user=user,
            account_name=account_name,
            password_hash=hash_password(password),
        )
        add_and_refresh(session, user_login)
        logging.getLogger("content_consent_finder").debug(
            f"created {user} and {user_login}"
        )
        return user


def delete_account(user: User):
    logging.getLogger("content_consent_finder").debug(f"delete_account {user}")
    with Session(engine) as session:
        user = session.get(User, user.id)
        created_groups = session.exec(
            select(RPGGroup).where(RPGGroup.gm_user_id == user.id)
        ).all()
        for group in created_groups:
            logging.getLogger("content_consent_finder").debug(f"deleting {group}")
            session.delete(group)
        joined_groups = session.exec(
            select(RPGGroup).where(RPGGroup.users.any(User.id == user.id))
        ).all()
        for group in joined_groups:
            logging.getLogger("content_consent_finder").debug(f"leaving {group}")
            group.users.remove(user)
            session.merge(group)
        created_sheets = session.exec(
            select(ConsentSheet).where(ConsentSheet.user_id == user.id)
        ).all()
        for sheet in created_sheets:
            # delete all entries
            deleted_entries = session.exec(
                delete(ConsentEntry).where(ConsentEntry.consent_sheet_id == sheet.id)
            ).rowcount
            logging.getLogger("content_consent_finder").debug(
                f"deleted {deleted_entries} entries"
            )
            session.delete(sheet)
            logging.getLogger("content_consent_finder").debug(f"deleted {sheet}")
        # delete userlogin if existing
        if user_login := session.exec(
            select(UserLogin).where(UserLogin.user_id == user.id)
        ).first():
            logging.getLogger("content_consent_finder").debug(f"deleting {user_login}")
            session.delete(user_login)
            session.commit()
        session.delete(user)
        session.commit()
        logging.getLogger("content_consent_finder").debug(f"deleted {user}")
        return user


def update_user(user: User):
    logging.getLogger("content_consent_finder").debug(f"update_user {user}")
    with Session(engine) as session:
        if user.id:
            session.merge(user)
            session.commit()
            logging.getLogger("content_consent_finder").debug(f"merged {user}")
        else:
            new_user = User(
                id_name=user.id_name,
                nickname=user.nickname,
            )
            add_and_refresh(session, new_user)
            user.id = new_user.id
            logging.getLogger("content_consent_finder").debug(f"added {new_user}")


def get_user_from_storage() -> User:
    # TODO fix after implementing cache invalidation on every relevant change (e.g. db change)
    # if user := app.storage.user.get("user"):
    #     return User.model_validate_json(user)
    if user_id := app.storage.user.get("user_id"):
        if user := get_user_by_id_name(user_id):
            # app.storage.user["user"] = user.model_dump_json()
            return user


get_user_by_id_name_chache = {}


def get_user_by_id_name(user_id: str, session: Session = None) -> User:
    if user_id in get_user_by_id_name_chache:
        return get_user_by_id_name_chache[user_id]
    logging.getLogger("content_consent_finder").debug(f"get_user_by_id_name {user_id}")
    if not session:
        with Session(engine) as session:
            return get_user_by_id_name(user_id, session)

    if found := session.exec(select(User).where(User.id_name == user_id)).first():
        for group in found.groups:
            group.name = sanitize_name(group.name)
        session.commit()
        session.refresh(found)
        get_user_by_id_name_chache[user_id] = found
        return found
    logging.getLogger("content_consent_finder").debug(f"User not found {user_id}")
    all_users = session.exec(select(User)).all()
    for user in all_users:
        logging.getLogger("content_consent_finder").debug(str(user))
