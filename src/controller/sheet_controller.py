import logging
import random
import string
from datetime import datetime
from functools import lru_cache

from sqlmodel import Session, delete, select

from models.db_models import (
    ConsentEntry,
    ConsentSheet,
    ConsentTemplate,
    CustomConsentEntry,
    RPGGroup,
    User,
    ConsentStatus,
    UserGroupLink,
    GroupConsentSheetLink,
)
from models.model_utils import add_and_refresh, engine


def fetch_sheet_groups(sheet: ConsentSheet) -> list[RPGGroup]:
    logging.getLogger("content_consent_finder").debug(f"fetch_sheet_groups {sheet}")
    with Session(engine) as session:
        return sheet.fetch_groups(session)


def create_share_id():
    with Session(engine) as session:
        existing_share_ids = set(
            session.exec(select(ConsentSheet.public_share_id)).all()
        )
        share_id = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        while share_id in existing_share_ids:
            share_id = "".join(
                random.choices(string.ascii_letters + string.digits, k=12)
            )
        return share_id


def create_new_consentsheet(user: User, session: Session = None) -> ConsentSheet:
    if not session:
        with Session(engine) as session:
            return create_new_consentsheet(user, session)
    logging.getLogger("content_consent_finder").info(
        f"create_new_consentsheet for {user}"
    )
    sheet_unique_name = "".join(
        random.choices(string.ascii_letters + string.digits, k=8)
    )
    possible_collision = set(session.exec(select(ConsentSheet.unique_name)).all())
    while sheet_unique_name in possible_collision:
        sheet_unique_name = "".join(
            random.choices(string.ascii_letters + string.digits, k=8)
        )
    user = session.get(User, user.id)
    sheet = ConsentSheet(
        unique_name=sheet_unique_name,
        user_id=user.id,
        user=user,
    )
    user.consent_sheets.append(sheet)
    session.commit()
    session.refresh(sheet)
    templates = session.exec(select(ConsentTemplate)).all()
    for template in templates:
        entry = ConsentEntry(
            consent_sheet_id=sheet.id,
            consent_sheet=sheet,
            consent_template_id=template.id,
            consent_template=template,
        )
        # session.add(entry)
        sheet.consent_entries.append(entry)
    # session.merge(sheet)
    session.commit()
    session.refresh(sheet)
    session.merge(user)
    session.commit()
    logging.getLogger("content_consent_finder").info(f"created {sheet}")
    return sheet


def duplicate_sheet(sheet_id: int, user_id: str | int):
    logging.getLogger("content_consent_finder").debug(
        f"duplicate_sheet {sheet_id} {user_id}"
    )

    sheet_unique_name = "".join(
        random.choices(string.ascii_letters + string.digits, k=8)
    )
    with Session(engine) as session:
        possible_collision = set(session.exec(select(ConsentSheet.unique_name)).all())
        while sheet_unique_name in possible_collision:
            sheet_unique_name = "".join(
                random.choices(string.ascii_letters + string.digits, k=8)
            )
        sheet = session.get(ConsentSheet, sheet_id)
        user = session.get(User, int(user_id))
        new_sheet = ConsentSheet(
            unique_name=sheet_unique_name,
            user_id=user.id,
            user=user,
            human_name=f"Copy of {sheet.display_name}",
            comment=sheet.comment,
        )
        add_and_refresh(session, new_sheet)
        blueprint_entries = session.exec(
            select(ConsentEntry).where(ConsentEntry.consent_sheet_id == sheet_id)
        ).all()
        for blueprint in blueprint_entries:
            entry = ConsentEntry(
                consent_sheet_id=new_sheet.id,
                consent_sheet=new_sheet,
                consent_template_id=blueprint.consent_template_id,
                consent_template=blueprint.consent_template,
                preference=blueprint.preference,
                comment=blueprint.comment,
            )
            session.add(entry)
            new_sheet.consent_entries.append(entry)
        session.commit()
        session.refresh(new_sheet)
        return new_sheet


def delete_sheet(user: User, sheet: ConsentSheet, session: Session = None):
    logging.getLogger("content_consent_finder").debug(f"delete_sheet {sheet}")
    if not session:
        with Session(engine) as session:
            return delete_sheet(user, sheet, session)
    _user_may_edit_sheet(user, sheet)
    sheet = session.get(ConsentSheet, sheet.id)
    # delete group links
    session.exec(
        delete(GroupConsentSheetLink).where(
            GroupConsentSheetLink.consent_sheet_id == sheet.id
        )
    )
    # delete entries
    session.exec(delete(ConsentEntry).where(ConsentEntry.consent_sheet_id == sheet.id))
    if sheet in user.consent_sheets:
        user.consent_sheets.remove(sheet)
    session.delete(sheet)
    session.commit()
    logging.getLogger("content_consent_finder").debug(f"deleted {sheet}")
    return sheet


def _user_may_see_sheet(user: User, sheet: ConsentSheet, session: Session):
    # is own sheet
    if sheet.user_id == user.id or sheet.public_share_id:
        return True
    # is in group
    if session.exec(
        select(GroupConsentSheetLink).where(
            GroupConsentSheetLink.consent_sheet_id == sheet.id,
            GroupConsentSheetLink.group_id == UserGroupLink.group_id,
            UserGroupLink.user_id == user.id,
        )
    ).first():
        return True
    logging.getLogger("content_consent_finder").warning(
        f"User {user} may not see sheet {sheet}"
    )


def _user_may_edit_sheet(user: User, sheet: ConsentSheet):
    # is own sheet
    if sheet.user_id == user.id:
        return True
    logging.getLogger("content_consent_finder").warning(
        f"User {user} may not edit sheet {sheet}"
    )
    raise PermissionError(f"User {user} may not edit sheet {sheet}")


def get_all_custom_entries() -> list[CustomConsentEntry]:
    logging.getLogger("content_consent_finder").debug("get_all_custom_entries")
    with Session(engine) as session:
        return session.exec(select(CustomConsentEntry)).all()


def update_custom_entry(user: User, entry: CustomConsentEntry):
    logging.getLogger("content_consent_finder").info(f"update_custom_entry {entry}")
    with Session(engine) as session:
        entry_sheet = session.get(ConsentSheet, entry.consent_sheet_id)
        entry.consent_sheet = entry_sheet
        entry.content = entry.content or ""
        _user_may_edit_sheet(user, entry_sheet)
        if entry.id:
            logging.getLogger("content_consent_finder").debug(f"saved {entry}")
            session.merge(entry)
            session.commit()
        else:
            add_and_refresh(session, entry)
            logging.getLogger("content_consent_finder").debug(f"saved {entry}")
            return entry


def update_entry(user: User, entry: ConsentEntry):
    logging.getLogger("content_consent_finder").debug(f"update_entry {entry}")
    with Session(engine) as session:
        entry_sheet = session.get(ConsentSheet, entry.consent_sheet_id)
        _user_may_edit_sheet(user, entry_sheet)
        existing_by_template = session.exec(
            select(ConsentEntry).where(
                ConsentEntry.consent_sheet_id == entry.consent_sheet_id,
                ConsentEntry.consent_template_id == entry.consent_template_id,
            )
        ).first()
        if entry.id:
            if entry.preference is None:
                logging.getLogger("content_consent_finder").warning(f"repaired {entry}")
                entry.preference = ConsentStatus.unknown
            session.merge(entry)
            session.commit()
        elif existing_by_template:
            existing_by_template.preference = entry.preference
            existing_by_template.comment = entry.comment
            add_and_refresh(session, existing_by_template)
            logging.getLogger("content_consent_finder").debug(
                f"merged {existing_by_template}"
            )
            entry.id = existing_by_template.id
        else:
            new_entry = ConsentEntry(
                consent_sheet_id=entry.consent_sheet_id or entry.consent_sheet.id,
                consent_template_id=entry.consent_template_id,
                preference=entry.preference,
                comment=entry.comment,
            )
            add_and_refresh(session, new_entry)
            logging.getLogger("content_consent_finder").debug(f"saved {new_entry}")
            entry.id = new_entry.id
            entry.consent_sheet_id = new_entry.consent_sheet_id
            entry.consent_template_id = new_entry.consent_template_id


@lru_cache
def get_consent_template_by_id(template_id: int) -> ConsentTemplate:
    logging.getLogger("content_consent_finder").debug(
        f"get_consent_template_by_id {template_id}"
    )
    with Session(engine) as session:
        return session.get(ConsentTemplate, template_id)


def get_all_consent_topics() -> list[ConsentTemplate]:
    logging.getLogger("content_consent_finder").debug("get_all_consent_topics")
    with Session(engine) as session:
        return session.exec(select(ConsentTemplate)).all()


def get_consent_sheet_by_id(user_id_name: str, sheet_id: int) -> ConsentSheet:
    logging.getLogger("content_consent_finder").debug(
        f"get_consent_sheet_by_id {sheet_id} as {user_id_name}"
    )
    with Session(engine) as session:
        if sheet := session.get(ConsentSheet, sheet_id):
            user = session.exec(
                select(User).where(User.id_name == user_id_name)
            ).first()
            if not user:
                logging.getLogger("content_consent_finder").warning(
                    f"User not found {user_id_name}"
                )
                all_users = session.exec(select(User)).all()
                for user in all_users:
                    logging.getLogger("content_consent_finder").debug(user)
                return None
            if not _user_may_see_sheet(user, sheet, session):
                return None
            # check entries
            templates = get_all_consent_topics()
            for template in templates:
                if not sheet.get_entry(template.id):
                    new_entry = ConsentEntry(
                        consent_sheet_id=sheet.id,
                        consent_sheet=sheet,
                        consent_template_id=template.id,
                        consent_template=template,
                    )
                    session.add(new_entry)
                    sheet.consent_entries.append(new_entry)
                    session.commit()
            session.commit()
            return session.get(ConsentSheet, sheet_id)


def update_consent_sheet(user: User, sheet: ConsentSheet):
    logging.getLogger("content_consent_finder").debug(f"update_consent_sheet {sheet}")
    with Session(engine) as session:
        _user_may_edit_sheet(user, sheet)
        if sheet.id:
            sheet.updated_at = datetime.now()
            session.merge(sheet)
            session.commit()
            logging.getLogger("content_consent_finder").debug(f"merged {sheet}")
        else:
            new_sheet = ConsentSheet(
                unique_name=sheet.unique_name,
                user_id=sheet.user_id,
                human_name=sheet.human_name,
                comment=sheet.comment,
                public_share_id=sheet.public_share_id,
            )
            add_and_refresh(session, new_sheet)
            sheet.id = new_sheet.id
            logging.getLogger("content_consent_finder").debug(f"added {new_sheet}")
