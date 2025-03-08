import logging
import random
import string

from sqlmodel import Session, delete, select

from controller.sheet_controller import create_new_consentsheet
from models.db_models import (
    ConsentSheet,
    ConsentStatus,
    GroupConsentSheetLink,
    RPGGroup,
    User,
    UserGroupLink,
)
from models.model_utils import add_and_refresh, engine
from utlis import sanitize_name


def get_group_by_id(group_id: int) -> RPGGroup:
    logging.getLogger("content_consent_finder").debug(f"get_group_by_id {group_id}")
    with Session(engine) as session:
        if group := session.get(RPGGroup, group_id):
            group.name = sanitize_name(group.name)
            session.commit()
            session.refresh(group)
            return group


def fetch_group_sheets(group: RPGGroup) -> list[ConsentSheet]:
    logging.getLogger("content_consent_finder").debug(f"fetch_group_sheets {group}")
    with Session(engine) as session:
        return group.fetch_consent_sheets(session)


def fetch_group_users(group: RPGGroup) -> list[User]:
    logging.getLogger("content_consent_finder").debug(f"fetch_group_users {group}")
    with Session(engine) as session:
        return group.fetch_users(session)


def get_group_by_name_id(group_name_id: str):
    logging.getLogger("content_consent_finder").debug(
        f"get_group_by_name_id {group_name_id}"
    )
    with Session(engine, autoflush=False) as session:
        name, group_id = group_name_id.rsplit("-", 1)
        group = session.get(
            RPGGroup,
            int(group_id),
        )
        if group.invite_code == "global" and not group.gm_consent_sheet:
            group.gm_consent_sheet = session.exec(
                select(ConsentSheet).where(ConsentSheet.user_id == group.gm_user_id)
            ).first()
            group.gm_consent_sheet_id = group.gm_consent_sheet.id
            session.merge(group)
            session.merge(
                GroupConsentSheetLink(
                    group_id=group.id, consent_sheet_id=group.gm_consent_sheet_id
                )
            )
            session.commit()
        if group and group.name.lower().replace(" ", "") == name.lower().replace(
            " ", ""
        ):
            return group
        elif group:
            raise ValueError(f"Mismatch questioneer_id: {group_name_id}", group.name)
        else:
            groups = session.exec(select(RPGGroup)).all()
            for group in groups:
                logging.getLogger("content_consent_finder").debug(str(group))

        raise ValueError(f"Invalid questioneer_id: {group_name_id}")


def assign_consent_sheet_to_group(sheet: ConsentSheet, group: RPGGroup):
    logging.getLogger("content_consent_finder").debug(
        f"assign_consent_sheet_to_group {sheet} <RPGGroup id={group.id} name={group.name}>"
    )
    with Session(engine) as session:
        group = session.get(RPGGroup, group.id)
        sheet = session.get(ConsentSheet, sheet.id)
        session.add(
            GroupConsentSheetLink(
                group_id=group.id,
                consent_sheet_id=sheet.id,
            )
        )
        session.commit()
        return group


def unassign_consent_sheet_from_group(sheet: ConsentSheet, group: RPGGroup):
    logging.getLogger("content_consent_finder").debug(
        f"unassign_consent_sheet_from_group {sheet} <RPGGroup id={group.id} name={group.name}>"
    )
    with Session(engine) as session:
        group = session.get(RPGGroup, group.id)
        sheet = session.get(ConsentSheet, sheet.id)
        if link := session.exec(
            select(GroupConsentSheetLink).where(
                GroupConsentSheetLink.group_id == group.id,
                GroupConsentSheetLink.consent_sheet_id == sheet.id,
            )
        ).first():
            session.delete(link)
            session.commit()
        else:
            logging.getLogger("content_consent_finder").warning(
                f"no link found {sheet} <RPGGroup id={group.id} name={group.name}>"
            )
        return group


def create_new_group(user: User, sheet_id: int = None) -> RPGGroup:
    logging.getLogger("content_consent_finder").debug(f"create_new_group {user}")
    with Session(engine, autoflush=False) as session:
        if sheet_id:
            sheet = session.get(ConsentSheet, sheet_id)
        else:
            sheet = create_new_consentsheet(user, session)
        group = RPGGroup(
            name=sanitize_name(f"{user.nickname}-Group"),
            gm_user_id=user.id,
            gm_consent_sheet_id=sheet.id,
            gm_consent_sheet=sheet,
            invite_code="-".join(
                [
                    "?",
                    "".join(random.choices(string.digits, k=3)),
                    "".join(random.choices(string.digits, k=3)),
                ]
            ),
        )
        session.add(group)
        session.commit()
        session.add(GroupConsentSheetLink(group_id=group.id, consent_sheet_id=sheet.id))
        session.add(UserGroupLink(user_id=user.id, group_id=group.id))
        session.commit()
        session.refresh(group)
        # if group.id is None:
    return regenerate_invite_code(group)


def update_group(group: RPGGroup):
    logging.getLogger("content_consent_finder").debug(f"update_group {group}")
    with Session(engine) as session:
        group.name = sanitize_name(group.name)
        session.merge(group)
        session.commit()
        logging.getLogger("content_consent_finder").debug(f"merged {group}")
        return group


def regenerate_invite_code(group: RPGGroup):
    with Session(engine) as session:
        group = session.get(RPGGroup, group.id)
        logging.getLogger("content_consent_finder").debug(
            f"regenerate_invite_code {group}"
        )
        group.invite_code = "-".join(
            [
                str(group.id),
                "".join(random.choices(string.digits, k=3)),
                "".join(random.choices(string.digits, k=3)),
            ]
        )
        session.commit()
        logging.getLogger("content_consent_finder").debug(f"merged {group}")
        return group


def delete_group(group: RPGGroup):
    logging.getLogger("content_consent_finder").debug(f"delete_group {group}")
    with Session(engine) as session:
        session.exec(
            delete(GroupConsentSheetLink).where(
                GroupConsentSheetLink.group_id == group.id
            )
        )
        session.exec(delete(UserGroupLink).where(UserGroupLink.group_id == group.id))
        session.delete(group)
        session.commit()
        logging.getLogger("content_consent_finder").debug(f"deleted {group}")
        return group


def ensure_global_group(session: Session):
    logging.getLogger("content_consent_finder").debug("ensure_global_group")
    if group := session.exec(
        select(RPGGroup).where(RPGGroup.invite_code == "global")
    ).first():
        return group
    global_gm_user = session.exec(
        select(User).where(User.id_name == "global_gm")
    ).first()
    if not global_gm_user:
        global_gm_user = User(
            id_name="global_gm",
            nickname="Global GM",
        )
        add_and_refresh(session, global_gm_user)
    global_gm_sheet = session.exec(
        select(ConsentSheet).where(ConsentSheet.user_id == global_gm_user.id)
    ).first()
    if not global_gm_sheet:
        global_gm_sheet = create_new_consentsheet(global_gm_user, session)
        for entry in global_gm_sheet.consent_entries:
            entry.preference = ConsentStatus.yes
        session.commit()
    group = RPGGroup(
        name="Global",
        gm_id=global_gm_user.id,
        gm_user=global_gm_user,
        gm_consent_sheet_id=global_gm_sheet.id,
        invite_code="global",
    )
    session.merge(group)
    session.commit()
    return group


def join_group(code: str, user: User):
    logging.getLogger("content_consent_finder").debug(
        f"join_group <{user}> invite_code={code}"
    )
    with Session(engine, autoflush=False) as session:
        user = session.get(User, user.id)
        if code.lower() == "global":
            return _join_group(user, ensure_global_group(session), session)

        if group := session.exec(
            select(RPGGroup).where(RPGGroup.invite_code == code)
        ).first():
            return _join_group(user, group, session)
        logging.getLogger("content_consent_finder").debug(f"no group found {code}")
        return None


def _join_group(user: User, group: RPGGroup, session: Session):
    session.merge(
        UserGroupLink(
            user_id=user.id,
            group_id=group.id,
        )
    )
    session.commit()
    logging.getLogger("content_consent_finder").debug(f"joined {group}")
    return group


def leave_group(group: RPGGroup, user: User):
    logging.getLogger("content_consent_finder").debug(f"leave_group {group} {user}")
    with Session(engine) as session:
        group = session.get(RPGGroup, group.id)
        user = session.get(User, user.id)
        session.exec(
            delete(UserGroupLink).where(
                UserGroupLink.user_id == user.id, UserGroupLink.group_id == group.id
            ),
            execution_options={"is_delete_using": True},
        )
        group_sheet_links = session.exec(
            select(GroupConsentSheetLink).where(
                GroupConsentSheetLink.group_id == group.id,
                GroupConsentSheetLink.consent_sheet_id == ConsentSheet.id,
                ConsentSheet.user_id == user.id,
            )
        ).all()
        for link in group_sheet_links:
            session.delete(link)
        session.merge(group)
        session.commit()
        logging.getLogger("content_consent_finder").debug(f"left {group}")
        return group
