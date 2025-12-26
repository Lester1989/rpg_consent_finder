import logging
import random
import time
from secrets import token_urlsafe

from sqlmodel import Session, select

from a_logger_setup import LOGGER_NAME
from models.db_models import (
    ConsentSheet,
    RPGGroup,
    User,
    UserGroupLink,
    UserLogin,
)
from models.model_utils import (
    add_and_refresh,
    check_password,
    hash_password,
    session_scope,
)
from controller.sheet_controller import delete_sheet
from services.session_service import session_storage
from telemetry import get_metrics_recorder


LOGGER = logging.getLogger(LOGGER_NAME)


def _record_login_attempt(provider: str, status: str) -> None:
    recorder = get_metrics_recorder()
    if recorder:
        recorder.record_login_attempt(provider, status)


def fetch_user_groups(user: User, session: Session | None = None) -> list[RPGGroup]:
    LOGGER.debug("fetch_user_groups %s", user)

    def _fetch(active_session: Session) -> list[RPGGroup]:
        return user.fetch_groups(active_session)

    if session is not None:
        return _fetch(session)

    with session_scope() as scoped_session:
        return _fetch(scoped_session)


def get_user_by_account_and_password(
    account_name: str, password: str, session: Session | None = None
) -> User | None:
    LOGGER.debug(
        "get_user_by_account_and_password %s and <redacted %s chars>",
        account_name,
        len(password) if password else -1,
    )

    def _load(active_session: Session) -> User | None:
        user_login = active_session.exec(
            select(UserLogin).where(UserLogin.account_name == account_name)
        ).first()
        LOGGER.debug("found %s", user_login)
        if user_login and check_password(password, user_login.password_hash):
            return active_session.get(User, user_login.user_id)
        LOGGER.debug("login failed")
        return None

    if session is not None:
        user = _load(session)
    else:
        with session_scope() as scoped_session:
            user = _load(scoped_session)

    _record_login_attempt("local", "success" if user else "failure")
    if not user:
        time.sleep(random.random() * 0.1)  # prevent timing attacks
    return user


def create_user_account(
    account_name: str, password: str, session: Session | None = None
) -> User:
    LOGGER.debug("create_user_account %s", account_name)

    def _create(active_session: Session) -> User:
        if active_session.exec(
            select(UserLogin).where(UserLogin.account_name == account_name)
        ).first():
            raise ValueError("AccountName already in use")
        user = User(id_name=f"custom-{account_name}", nickname="")
        add_and_refresh(active_session, user)
        user_login = UserLogin(
            user_id=user.id,
            account_name=account_name,
            password_hash=hash_password(password),
        )
        add_and_refresh(active_session, user_login)
        LOGGER.debug("created %s and %s", user, user_login)
        return user

    if session is not None:
        return _create(session)

    with session_scope() as scoped_session:
        return _create(scoped_session)


def delete_account(user: User, session: Session | None = None) -> User | None:
    LOGGER.debug("delete_account %s", user)

    def _delete(active_session: Session) -> User | None:
        managed_user = active_session.get(User, user.id)
        if managed_user is None:
            LOGGER.debug("user %s already removed", user)
            return None

        created_groups = active_session.exec(
            select(RPGGroup).where(RPGGroup.gm_user_id == managed_user.id)
        ).all()
        for group in created_groups:
            LOGGER.debug("deleting %s", group)
            active_session.delete(group)

        joined_group_links = active_session.exec(
            select(UserGroupLink).where(UserGroupLink.user_id == managed_user.id)
        ).all()
        for link in joined_group_links:
            LOGGER.debug("leaving %s", link)
            active_session.delete(link)

        created_sheets = active_session.exec(
            select(ConsentSheet).where(ConsentSheet.user_id == managed_user.id)
        ).all()
        for sheet in created_sheets:
            delete_sheet(managed_user, sheet, active_session)

        if user_login := active_session.exec(
            select(UserLogin).where(UserLogin.user_id == managed_user.id)
        ).first():
            LOGGER.debug("deleting %s", user_login)
            active_session.delete(user_login)

        active_session.delete(managed_user)
        active_session.commit()
        LOGGER.debug("deleted %s", managed_user)
        return managed_user

    if session is not None:
        return _delete(session)

    with session_scope() as scoped_session:
        return _delete(scoped_session)


def update_user(user: User, session: Session | None = None) -> None:
    LOGGER.debug("update_user %s", user)

    def _update(active_session: Session) -> None:
        if user.id:
            active_session.merge(user)
            active_session.commit()
            LOGGER.debug("merged %s", user)
            return

        new_user = User(
            id_name=user.id_name,
            nickname=user.nickname,
        )
        add_and_refresh(active_session, new_user)
        user.id = new_user.id
        LOGGER.debug("added %s", new_user)

    if session is not None:
        _update(session)
        return

    with session_scope() as scoped_session:
        _update(scoped_session)


def get_user_from_storage() -> User | None:
    # TODO fix after implementing cache invalidation on every relevant change (e.g. db change)
    if user_id := session_storage.get("user_id"):
        return get_user_by_id_name(user_id)
    return None


def get_or_create_sso_user(
    provider: str,
    account_id: str,
    *,
    display_name: str | None = None,
    email: str | None = None,
    session: Session | None = None,
) -> User:
    LOGGER.debug("get_or_create_sso_user provider=%s id=%s", provider, account_id)
    account_name = f"{provider}:{account_id}"
    id_name = f"{provider}-{account_id}"

    def _ensure(active_session: Session) -> User:
        login_record = active_session.exec(
            select(UserLogin).where(UserLogin.account_name == account_name)
        ).first()
        if login_record:
            user = active_session.get(User, login_record.user_id)
            if user is None:
                LOGGER.warning(
                    "dangling login mapping for %s; recreating user", account_name
                )
                active_session.delete(login_record)
                active_session.commit()
            else:
                return user

        user = active_session.exec(select(User).where(User.id_name == id_name)).first()
        if user is None:
            user = User(id_name=id_name, nickname=display_name or "")
            add_and_refresh(active_session, user)
        elif display_name and not user.nickname:
            user.nickname = display_name
            active_session.add(user)
            active_session.commit()
            active_session.refresh(user)

        random_secret = token_urlsafe(16)
        user_login = UserLogin(
            user_id=user.id,
            account_name=account_name,
            password_hash=hash_password(random_secret),
        )
        add_and_refresh(active_session, user_login)
        return user

    if session is not None:
        return _ensure(session)

    with session_scope() as scoped_session:
        user = _ensure(scoped_session)
        _record_login_attempt(provider, "success")
        return user


# get_user_by_id_name_chache = {}


def get_user_by_id_name(user_id: str, session: Session | None = None) -> User | None:
    # if user_id in get_user_by_id_name_chache:
    #     return get_user_by_id_name_chache[user_id]
    LOGGER.debug("get_user_by_id_name %s", user_id)

    def _fetch(active_session: Session) -> User | None:
        return active_session.exec(select(User).where(User.id_name == user_id)).first()

    if session is not None:
        found = _fetch(session)
    else:
        with session_scope() as scoped_session:
            found = _fetch(scoped_session)

    if not found:
        LOGGER.debug("User not found %s", user_id)
    return found
