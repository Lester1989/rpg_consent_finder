import logging
import random
import string

from sqlmodel import Session, delete, select

from controller.sheet_controller import create_new_consentsheet
from models.db_models import (
    ConsentSheet,
    GroupConsentSheetLink,
    RPGGroup,
    User,
    UserGroupLink,
)
from models.model_utils import add_and_refresh, engine
from utlis import sanitize_name


def get_group_by_id(group_id: int) -> RPGGroup:
    logging.debug(f"get_group_by_id {group_id}")
    with Session(engine) as session:
        if group := session.get(RPGGroup, group_id):
            group.name = sanitize_name(group.name)
            session.commit()
            session.refresh(group)
            return group


def get_group_by_name_id(group_name_id: str):
    logging.debug(f"get_group_by_name_id {group_name_id}")
    with Session(engine) as session:
        name, group_id = group_name_id.rsplit("-", 1)
        group = session.get(
            RPGGroup,
            int(group_id),
        )
        if group and group.name.lower().replace(" ", "") == name.lower().replace(
            " ", ""
        ):
            return group
        elif group:
            raise ValueError(f"Mismatch questioneer_id: {group_name_id}", group.name)
        else:
            groups = session.exec(select(RPGGroup)).all()
            for group in groups:
                logging.debug(str(group))

        raise ValueError(f"Invalid questioneer_id: {group_name_id}")


def assign_consent_sheet_to_group(sheet: ConsentSheet, group: RPGGroup):
    logging.debug(
        f"assign_consent_sheet_to_group {sheet} <RPGGroup id={group.id} name={group.name}>"
    )
    with Session(engine) as session:
        group = session.get(RPGGroup, group.id)
        sheet = session.get(ConsentSheet, sheet.id)
        group.consent_sheets.append(sheet)
        session.merge(group)
        session.commit()
        logging.debug(f"merged {group}")
        return group


def unassign_consent_sheet_from_group(sheet: ConsentSheet, group: RPGGroup):
    logging.debug(
        f"unassign_consent_sheet_from_group {sheet} <RPGGroup id={group.id} name={group.name}>"
    )
    with Session(engine) as session:
        group = session.get(RPGGroup, group.id)
        sheet = session.get(ConsentSheet, sheet.id)
        group.consent_sheets.remove(sheet)
        session.merge(group)
        session.commit()
        logging.debug(f"merged {group}")
        return group


def create_new_group(user: User) -> RPGGroup:
    logging.debug(f"create_new_group {user}")
    with Session(engine) as session:
        sheet = create_new_consentsheet(user)
        group = RPGGroup(
            name=sanitize_name(f"{user.nickname}-Group"),
            gm_id=user.id,
            gm_user=user,
            gm_consent_sheet_id=sheet.id,
            gm_consent_sheet=sheet,
            users=[user],
            consent_sheets=[sheet],
            invite_code="-".join(
                [
                    "?",
                    "".join(random.choices(string.digits, k=3)),
                    "".join(random.choices(string.digits, k=3)),
                ]
            ),
        )
        add_and_refresh(session, group)
    return regenerate_invite_code(group)


def update_group(group: RPGGroup):
    logging.debug(f"update_group {group}")
    with Session(engine) as session:
        group.name = sanitize_name(group.name)
        session.merge(group)
        session.commit()
        logging.debug(f"merged {group}")
        return group


def regenerate_invite_code(group: RPGGroup):
    logging.debug(f"regenerate_invite_code {group}")
    with Session(engine) as session:
        group.invite_code = "-".join(
            [
                str(group.id),
                "".join(random.choices(string.digits, k=3)),
                "".join(random.choices(string.digits, k=3)),
            ]
        )
        session.merge(group)
        session.commit()
        logging.debug(f"merged {group}")
        return group


def delete_group(group: RPGGroup):
    logging.debug(f"delete_group {group}")
    with Session(engine) as session:
        # remove sheets from group
        for sheet in group.consent_sheets:
            group.consent_sheets.remove(sheet)
        # remove users from group
        for user in group.users:
            group.users.remove(user)
        session.exec(
            delete(GroupConsentSheetLink).where(
                GroupConsentSheetLink.group_id == group.id
            )
        )
        session.exec(delete(UserGroupLink).where(UserGroupLink.group_id == group.id))
        session.delete(group)
        session.commit()
        logging.debug(f"deleted {group}")
        return group


def join_group(code: str, user: User):
    logging.debug(f"join_group <{user}> invite_code={code}")
    with Session(engine) as session:
        user = session.get(User, user.id)
        if group := session.exec(
            select(RPGGroup).where(RPGGroup.invite_code == code)
        ).first():
            return _join_group(user, group, session)
        logging.debug(f"no group found {code}")
        return None


def _join_group(user: User, group: RPGGroup, session: Session):
    if user in group.users:
        logging.debug(f"already in {group}")
        return group
    group.users.append(user)
    session.merge(group)
    session.commit()
    logging.debug(f"joined {group}")
    return group


def leave_group(group: RPGGroup, user: User):
    logging.debug(f"leave_group {group} {user}")
    with Session(engine) as session:
        group = session.get(RPGGroup, group.id)
        user = session.get(User, user.id)
        group.users.remove(user)
        group.consent_sheets = [
            sheet for sheet in group.consent_sheets if sheet.user_id != user.id
        ]
        session.exec(
            delete(UserGroupLink).where(
                UserGroupLink.user_id == user.id, UserGroupLink.group_id == group.id
            )
        )
        session.exec(
            delete(GroupConsentSheetLink).where(
                GroupConsentSheetLink.group_id == group.id,
                GroupConsentSheetLink.consent_sheet_id == ConsentSheet.id,
                ConsentSheet.user_id == user.id,
            )
        )
        session.merge(group)
        session.commit()
        logging.debug(f"left {group}")
        return group
