import asyncio

import pytest
from nicegui.testing import User
from sqlmodel import Session, delete, select

from controller import user_controller
from models import model_utils
from models.db_models import (
    GroupConsentSheetLink,
    RPGGroup,
    User as DbUser,
    UserGroupLink,
)
from services.group_service import create_new_group, delete_group


GM_ACCOUNT = "gm_tester"
GM_PASSWORD = "gm_secret"
GM_NICKNAME = "GM Tester"


async def login(
    user: User, account_name: str = "testuser", password: str = "123123123"
) -> None:
    await user.open("/login")
    await user.should_see("login_tab")
    user.find("login_tab").click()
    await user.should_see("login_account")
    await user.should_see("login_pw")
    user.find("login_account").type(account_name)
    user.find("login_pw").type(password)
    user.find("login_button").click()
    await user.should_see("logout_btn", retries=5)


def _ensure_user(account_name: str, password: str, nickname: str) -> DbUser:
    established = user_controller.get_user_by_account_and_password(
        account_name, password
    )
    if not established:
        established = user_controller.create_user_account(account_name, password)
    established.nickname = nickname
    user_controller.update_user(established)
    refreshed = user_controller.get_user_by_account_and_password(account_name, password)
    assert refreshed is not None, "Expected user to be retrievable after creation"
    return refreshed


@pytest.mark.anyio
async def test_join_group_via_ui_persists_membership(user: User) -> None:
    gm_user = _ensure_user(GM_ACCOUNT, GM_PASSWORD, GM_NICKNAME)

    with Session(model_utils.engine) as session:
        gm_db = session.get(DbUser, gm_user.id)
        assert gm_db is not None
        test_user = session.exec(
            select(DbUser).where(DbUser.id_name == "custom-testuser")
        ).first()
        if test_user is None:
            test_user = session.exec(
                select(DbUser).where(DbUser.nickname == "testuser")
            ).first()
        assert test_user is not None
        group = create_new_group(gm_db, session=session)
        group.invite_code = f"{group.id}-111-222"
        session.add(group)
        session.commit()
        session.refresh(group)
        session.exec(
            delete(UserGroupLink).where(
                UserGroupLink.group_id == group.id,
                UserGroupLink.user_id == test_user.id,
            )
        )
        session.commit()
        invite_code = group.invite_code
        group_id = group.id
        test_user_id = test_user.id

    await login(user)
    await user.open("/home")
    user.find("group_join_code_input").type(invite_code)
    user.find("join_group_button").click()
    await asyncio.sleep(1.5)

    with Session(model_utils.engine) as session:
        membership = session.exec(
            select(UserGroupLink).where(
                UserGroupLink.group_id == group_id,
                UserGroupLink.user_id == test_user_id,
            )
        ).first()
        assert membership is not None
        group_obj = session.get(RPGGroup, group_id)
        if group_obj is not None:
            delete_group(group_obj, session=session)
        else:
            session.exec(
                delete(UserGroupLink).where(
                    UserGroupLink.group_id == group_id,
                    UserGroupLink.user_id == test_user_id,
                )
            )
            session.commit()


@pytest.mark.anyio
async def test_group_creation_route_creates_group_and_links(user: User) -> None:
    await login(user)

    with Session(model_utils.engine) as session:
        test_user = session.exec(
            select(DbUser).where(DbUser.nickname == "testuser")
        ).first()
        assert test_user is not None
        existing_group_ids = {
            group.id
            for group in session.exec(
                select(RPGGroup).where(RPGGroup.gm_user_id == test_user.id)
            ).all()
        }

    await user.open("/groupconsent")
    await asyncio.sleep(1.5)

    with Session(model_utils.engine) as session:
        updated_groups = session.exec(
            select(RPGGroup).where(RPGGroup.gm_user_id == test_user.id)
        ).all()
        new_group = next(
            (group for group in updated_groups if group.id not in existing_group_ids),
            None,
        )
        assert new_group is not None
        assert new_group.invite_code != "global"
        assert str(new_group.id) in new_group.invite_code
        gm_membership = session.exec(
            select(UserGroupLink).where(
                UserGroupLink.group_id == new_group.id,
                UserGroupLink.user_id == test_user.id,
            )
        ).first()
        assert gm_membership is not None
        sheet_links = session.exec(
            select(GroupConsentSheetLink).where(
                GroupConsentSheetLink.group_id == new_group.id,
            )
        ).all()
        assert sheet_links, "Expected at least one sheet linked to the new group"
        delete_group(new_group, session=session)
