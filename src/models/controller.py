from datetime import datetime
import logging
from models.db_models import (
    ConsentEntry,
    ConsentSheet,
    ConsentTemplate,
    RPGGroup,
    User,
    GroupConsentSheetLink,
    UserGroupLink,
    FAQItem,
    UserContentQuestion,
    UserFAQ,
    LocalizedText,
)
from models.model_utils import engine
from sqlmodel import Session, select, delete
import random
import string


def store_faq_question(question: str):
    logging.debug(f"store_faq_question {question}")
    with Session(engine) as session:
        faq = UserFAQ(question=question)
        session.add(faq)
        session.commit()
        session.refresh(faq)
        return faq


def remove_faq_question(faq_question: UserFAQ):
    logging.debug(f"remove_faq_question {faq_question}")
    with Session(engine) as session:
        session.exec(delete(UserFAQ).where(UserFAQ.id == faq_question.id))
        session.commit()


def remove_content_question(content_question: UserContentQuestion):
    logging.debug(f"remove_content_question {content_question}")
    with Session(engine) as session:
        session.exec(
            delete(UserContentQuestion).where(
                UserContentQuestion.id == content_question.id
            )
        )
        session.commit()


def store_content_answer(
    category: str,
    topic: str,
    explanation: str,
    recommendation: UserContentQuestion = None,
):
    logging.debug(f"store_content_answer {category} {topic} {explanation}")
    with Session(engine) as session:
        if recommendation:
            session.exec(
                delete(UserContentQuestion).where(
                    UserContentQuestion.id == recommendation.id
                )
            )
        content_template = ConsentTemplate(
            category=category, topic=topic, explanation=explanation
        )
        session.add(content_template)
        session.commit()
        session.refresh(content_template)
        return content_template


def store_faq_answer(question: str, answer: str, faq_question: UserFAQ = None):
    logging.debug(f"store_faq_answer {question} to {faq_question.id}")
    with Session(engine) as session:
        if faq_question:
            session.exec(delete(UserFAQ).where(UserFAQ.id == faq_question.id))
        faq = FAQItem(question=question, answer=answer)
        session.add(faq)
        session.commit()
        session.refresh(faq)
        return faq


def get_all_faq_questions():
    logging.debug("get_all_faq_questions")
    with Session(engine) as session:
        return session.exec(select(UserFAQ)).all()


def get_all_content_questions():
    logging.debug("get_all_content_questions")
    with Session(engine) as session:
        return session.exec(select(UserContentQuestion)).all()


def store_content_question(question: str):
    logging.debug(f"store_content_question {question}")
    with Session(engine) as session:
        content_question = UserContentQuestion(question=question)
        session.add(content_question)
        session.commit()
        session.refresh(content_question)
        return content_question


def get_all_faq():
    logging.debug("get_all_faq")
    with Session(engine) as session:
        return session.exec(select(FAQItem)).all()


def get_status():
    logging.debug("get_status")
    with Session(engine) as session:
        sheet_count = len(session.exec(select(ConsentSheet)).all())
        entry_count = len(session.exec(select(ConsentEntry)).all())
        template_count = len(session.exec(select(ConsentTemplate)).all())
        group_count = len(session.exec(select(RPGGroup)).all())
        user_count = len(session.exec(select(User)).all())
        group_sheet_links = len(session.exec(select(GroupConsentSheetLink)).all())
        user_group_links = len(session.exec(select(UserGroupLink)).all())
        return {
            "sheets": (sheet_count, clear_sheets),
            "entries": (entry_count, clear_entries),
            "templates": (template_count, clear_templates),
            "groups": (group_count, clear_groups),
            "users": (user_count, clear_users),
            "group_sheet_links": (group_sheet_links, clear_group_sheet_links),
            "user_group_links": (user_group_links, clear_user_group_links),
        }


def clear_group_sheet_links():
    logging.debug("clear_group_sheet_links")
    with Session(engine) as session:
        logging.debug(session.exec(delete(GroupConsentSheetLink)).rowcount)
        session.commit()
        return get_status()


def clear_user_group_links():
    logging.debug("clear_user_group_links")
    with Session(engine) as session:
        logging.debug(session.exec(delete(UserGroupLink)).rowcount)
        session.commit()
        return get_status()


def clear_users():
    logging.debug("clear_user")
    with Session(engine) as session:
        logging.debug(session.exec(delete(User)).rowcount)
        session.commit()
        return get_status()


def clear_groups():
    logging.debug("clear_groups")
    with Session(engine) as session:
        logging.debug(session.exec(delete(RPGGroup)).rowcount)
        session.commit()
        return get_status()


def clear_sheets():
    logging.debug("clear_sheets")
    with Session(engine) as session:
        logging.debug(session.exec(delete(ConsentSheet)).rowcount)
        session.commit()
        return get_status()


def clear_entries():
    logging.debug("clear_entries")
    with Session(engine) as session:
        logging.debug(session.exec(delete(ConsentEntry)).rowcount)
        session.commit()
        return get_status()


def clear_templates():
    logging.debug("clear_templates")
    with Session(engine) as session:
        logging.debug(session.exec(delete(ConsentTemplate)).rowcount)
        session.commit()
        return get_status()


def update_user(user: User):
    logging.debug(f"update_user {user}")
    with Session(engine) as session:
        if user.id:
            session.merge(user)
            session.commit()
            logging.debug(f"merged {user}")
        else:
            new_user = User(
                id_name=user.id_name,
                nickname=user.nickname,
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            user.id = new_user.id
            logging.debug(f"added {new_user}")


def get_user_by_id_name(user_id: str, session: Session = None) -> User:
    logging.debug(f"get_user_by_id_name {user_id}")
    if not session:
        with Session(engine) as session:
            return get_user_by_id_name(user_id, session)

    found = session.exec(select(User).where(User.id_name == user_id)).first()
    if found:
        return found
    logging.debug(f"User not found {user_id}")
    all_users = session.exec(select(User)).all()
    for user in all_users:
        logging.debug(str(user))


def get_consent_sheet_by_id(sheet_id: int) -> ConsentSheet:
    logging.debug(f"get_consent_sheet_by_id {sheet_id}")
    with Session(engine) as session:
        sheet = session.get(ConsentSheet, sheet_id)
        # check entries
        if sheet:
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
            return session.get(ConsentSheet, sheet_id)


def update_consent_sheet(sheet: ConsentSheet):
    logging.debug(f"update_consent_sheet {sheet}")
    with Session(engine) as session:
        if sheet.id:
            sheet.updated_at = datetime.now()
            session.merge(sheet)
            session.commit()
            logging.debug(f"merged {sheet}")
        else:
            new_sheet = ConsentSheet(
                unique_name=sheet.unique_name,
                user_id=sheet.user_id,
                human_name=sheet.human_name,
                comment=sheet.comment,
                public_share_id=sheet.public_share_id,
            )
            session.add(new_sheet)
            session.commit()
            session.refresh(new_sheet)
            sheet.id = new_sheet.id
            logging.debug(f"added {new_sheet}")


def create_share_id():
    with Session(engine) as session:
        share_id = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        collision = session.exec(
            select(ConsentSheet).where(ConsentSheet.public_share_id == share_id)
        ).first()
        while collision:
            share_id = "".join(
                random.choices(string.ascii_letters + string.digits, k=12)
            )
            collision = session.exec(
                select(ConsentSheet).where(ConsentSheet.public_share_id == share_id)
            ).first()
        return share_id


def update_entry(entry: ConsentEntry):
    logging.debug(f"update_entry {entry}")
    with Session(engine) as session:
        existing_by_template = session.exec(
            select(ConsentEntry).where(
                ConsentEntry.consent_sheet_id == entry.consent_sheet_id,
                ConsentEntry.consent_template_id == entry.consent_template_id,
            )
        ).first()
        if entry.id:
            session.merge(entry)
            session.commit()
        elif existing_by_template:
            existing_by_template.preference = entry.preference
            existing_by_template.comment = entry.comment
            session.merge(existing_by_template)
            session.commit()
            session.refresh(existing_by_template)
            logging.debug(f"merged {existing_by_template}")
            entry.id = existing_by_template.id
        else:
            new_entry = ConsentEntry(
                consent_sheet_id=entry.consent_sheet_id or entry.consent_sheet.id,
                consent_template_id=entry.consent_template_id,
                preference=entry.preference,
                comment=entry.comment,
            )
            session.add(new_entry)
            session.commit()
            session.refresh(new_entry)
            logging.debug(f"saved {new_entry}")
            entry.id = new_entry.id
            entry.consent_sheet_id = new_entry.consent_sheet_id
            entry.consent_template_id = new_entry.consent_template_id


def get_consent_template_by_id(template_id: int) -> ConsentTemplate:
    logging.debug(f"get_consent_template_by_id {template_id}")
    with Session(engine) as session:
        return session.get(ConsentTemplate, template_id)


def get_all_consent_topics() -> list[ConsentTemplate]:
    logging.debug("get_all_consent_topics")
    with Session(engine) as session:
        return session.exec(select(ConsentTemplate)).all()


def get_group_by_id(group_id: int) -> RPGGroup:
    logging.debug(f"get_group_by_id {group_id}")
    with Session(engine) as session:
        return session.get(RPGGroup, group_id)


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
            raise ValueError("Mismatch questioneer_id: " + group_name_id, group.name)
        else:
            groups = session.exec(select(RPGGroup)).all()
            for group in groups:
                logging.debug(str(group))

        raise ValueError("Invalid questioneer_id: " + group_name_id)


def create_new_consentsheet(user: User) -> ConsentSheet:
    logging.debug(f"create_new_consentsheet {user}")
    sheet_unique_name = "".join(
        random.choices(string.ascii_letters + string.digits, k=8)
    )
    with Session(engine) as session:
        possible_collision = set(session.exec(select(ConsentSheet.unique_name)).all())
        while sheet_unique_name in possible_collision:
            sheet_unique_name = "".join(
                random.choices(string.ascii_letters + string.digits, k=8)
            )

        sheet = ConsentSheet(
            unique_name=sheet_unique_name,
            user_id=user.id,
            user=user,
        )
        session.add(sheet)
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
            session.add(entry)
            sheet.consent_entries.append(entry)
        session.commit()
        session.refresh(sheet)
        return sheet


def get_localized_text(id: int) -> LocalizedText:
    logging.debug(f"get_localized_text {id}")
    with Session(engine) as session:
        return session.get(LocalizedText, id)


def get_all_localized_texts() -> dict[int, LocalizedText]:
    logging.debug("get_all_localized_texts")
    with Session(engine) as session:
        return {text.id: text for text in session.exec(select(LocalizedText)).all()}


def duplicate_sheet(sheet_id: int, user_id_name):
    logging.debug(f"duplicate_sheet {sheet_id} {user_id_name}")

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
        user = get_user_by_id_name(user_id_name)
        user = session.merge(user)
        new_sheet = ConsentSheet(
            unique_name=sheet_unique_name,
            user_id=user.id,
            user=user,
            human_name=f"Copy of {sheet.display_name}",
            comment=sheet.comment,
        )
        session.add(new_sheet)
        session.commit()
        session.refresh(new_sheet)
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
            name=user.nickname + " Group",
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
        session.add(group)
        session.commit()
        session.refresh(group)
    return regenerate_invite_code(group)


def update_group(group: RPGGroup):
    logging.debug(f"update_group {group}")
    with Session(engine) as session:
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
        session.delete(group)
        session.commit()
        logging.debug(f"deleted {group}")
        return group


def join_group(code: str, user: User):
    logging.debug(f"join_group <{user}> invite_code={code}")
    with Session(engine) as session:
        user = session.get(User, user.id)
        group = session.exec(
            select(RPGGroup).where(RPGGroup.invite_code == code)
        ).first()
        if group:
            if user in group.users:
                logging.debug(f"already in {group}")
                return group
            group.users.append(user)
            session.merge(group)
            session.commit()
            logging.debug(f"joined {group}")
            return group
        else:
            logging.debug(f"no group found {code}")
            return None


def leave_group(group: RPGGroup, user: User):
    logging.debug(f"leave_group {group} {user}")
    with Session(engine) as session:
        group = session.get(RPGGroup, group.id)
        user = session.get(User, user.id)
        group.users.remove(user)
        group.consent_sheets = [
            sheet for sheet in group.consent_sheets if sheet.user_id != user.id
        ]
        session.merge(group)
        session.commit()
        logging.debug(f"left {group}")
        return group


def delete_sheet(sheet: ConsentSheet):
    logging.debug(f"delete_sheet {sheet}")
    with Session(engine) as session:
        sheet = session.get(ConsentSheet, sheet.id)
        session.delete(sheet)
        session.commit()
        logging.debug(f"deleted {sheet}")
        return sheet
