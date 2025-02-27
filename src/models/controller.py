import logging
import random
import time
import string
from datetime import datetime

from nicegui import app
from sqlmodel import Session, delete, select
from models.model_utils import hash_password, check_password
from models.db_models import (
    ConsentEntry,
    ConsentSheet,
    ConsentTemplate,
    FAQItem,
    GroupConsentSheetLink,
    LocalizedText,
    PlayFunResult,
    RPGGroup,
    User,
    UserContentQuestion,
    UserFAQ,
    UserGroupLink,
    UserLogin,
    CustomConsentEntry,
    PlayFunQuestion,
)
from models.model_utils import engine
from utlis import sanitize_name


def get_user_by_account_and_password(account_name: str, password: str) -> User:
    logging.debug(
        f"get_user_by_account_and_password {account_name} and <redacted {len(password) if password else -1} chars>"
    )
    with Session(engine) as session:
        user_login = session.exec(
            select(UserLogin).where(UserLogin.account_name == account_name)
        ).first()
        logging.debug(f"found {user_login}")
        if user_login and check_password(password, user_login.password_hash):
            return session.get(User, user_login.user_id)
        logging.debug("login failed ")
        time.sleep(random.random() * 0.1)  # prevent timing attacks
        return None


def get_playfun_questions(shuffled: bool = True) -> list[PlayFunQuestion]:
    logging.info("get_playfun_questions")
    with Session(engine) as session:
        questions = session.exec(select(PlayFunQuestion)).all()
        if shuffled:
            random.shuffle(questions)
        return questions


def store_playfun_result(user: User, playfun_result: PlayFunResult):
    logging.debug(f"store_playfun_result {user} {playfun_result}")
    with Session(engine) as session:
        playfun_result.user_id = user.id
        session.add(playfun_result)
        session.commit()
        session.refresh(playfun_result)
        return playfun_result


def create_user_account(account_name: str, password: str) -> User:
    logging.debug(f"create_user_account {account_name}")
    with Session(engine) as session:
        if session.exec(
            select(UserLogin).where(UserLogin.account_name == account_name)
        ).first():
            raise ValueError("AccountName already in use")
        user = User(id_name=f"custom-{account_name}", nickname="")
        session.add(user)
        session.commit()
        session.refresh(user)
        user_login = UserLogin(
            user_id=user.id,
            user=user,
            account_name=account_name,
            password_hash=hash_password(password),
        )
        session.add(user_login)
        session.commit()
        session.refresh(user_login)
        logging.debug(f"created {user} and {user_login}")
        return user


def get_all_localized_texts() -> dict[int, LocalizedText]:
    logging.debug("get_all_localized_texts")
    with Session(engine) as session:
        return {text.id: text for text in session.exec(select(LocalizedText)).all()}


def update_localized_text(text: LocalizedText):
    logging.debug(f"update_localized_text {text}")
    with Session(engine) as session:
        if text.id:
            orig_text = session.get(LocalizedText, text.id)
            orig_text.text_de = text.text_de
            orig_text.text_en = text.text_en
            session.merge(orig_text)
            session.commit()
            session.refresh(orig_text)
            text.id = orig_text.id
            logging.debug(f"merged {text}")
        else:
            session.add(text)
            session.commit()
            session.refresh(text)
            logging.debug(f"added {text}")
        return text


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
    category_de: str,
    topic_de: str,
    explanation_de: str,
    topic_en: str,
    explanation_en: str,
    recommendation: UserContentQuestion = None,
):
    logging.debug(f"store_content_answer {category_de} {topic_de} {explanation_de}")
    with Session(engine) as session:
        if recommendation:
            session.exec(
                delete(UserContentQuestion).where(
                    UserContentQuestion.id == recommendation.id
                )
            )
        category = update_localized_text(
            LocalizedText(text_de=category_de, text_en=category_de)
        )
        topic = update_localized_text(LocalizedText(text_de=topic_de, text_en=topic_en))
        explanation = update_localized_text(
            LocalizedText(text_de=explanation_de, text_en=explanation_en)
        )

        content_template = ConsentTemplate(
            category_id=category.id,
            category_local=category,
            topic_id=topic.id,
            topic_local=topic,
            explanation_id=explanation.id,
            explanation_local=explanation,
        )
        session.add(content_template)
        session.commit()
        session.refresh(content_template)
        return content_template


def store_faq_answer(
    question_de: str,
    question_en: str,
    answer_de: str,
    answer_en: str,
    faq_question: UserFAQ = None,
):
    logging.debug(f"store_faq_answer {question_de} to {faq_question.id}")
    with Session(engine) as session:
        if faq_question:
            session.exec(delete(UserFAQ).where(UserFAQ.id == faq_question.id))
        question = update_localized_text(
            LocalizedText(text_de=question_de, text_en=question_en)
        )
        answer = update_localized_text(
            LocalizedText(text_de=answer_de, text_en=answer_en)
        )
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
        local_texts = len(session.exec(select(LocalizedText)).all())
        faq_items = len(session.exec(select(FAQItem)).all())
        content_questions = len(session.exec(select(UserContentQuestion)).all())
        faq_questions = len(session.exec(select(UserFAQ)).all())
        return {
            "sheets": (sheet_count, clear_sheets),
            "entries": (entry_count, clear_entries),
            "templates": (template_count, clear_templates),
            "groups": (group_count, clear_groups),
            "users": (user_count, clear_users),
            "group_sheet_links": (group_sheet_links, clear_group_sheet_links),
            "user_group_links": (user_group_links, clear_user_group_links),
            "local_texts": (local_texts, clear_texts),
            "faq_items": (faq_items, lambda: None),
            "content_questions": (content_questions, lambda: None),
            "faq_questions": (faq_questions, lambda: None),
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


def clear_texts():
    logging.debug("clear_texts")
    with Session(engine) as session:
        logging.debug(session.exec(delete(LocalizedText)).rowcount)
        session.commit()
        return get_status()


def delete_account(user: User):
    logging.debug(f"delete_account {user}")
    with Session(engine) as session:
        user = session.get(User, user.id)
        created_groups = session.exec(
            select(RPGGroup).where(RPGGroup.gm_user_id == user.id)
        ).all()
        for group in created_groups:
            logging.debug(f"deleting {group}")
            session.delete(group)
        joined_groups = session.exec(
            select(RPGGroup).where(RPGGroup.users.any(User.id == user.id))
        ).all()
        for group in joined_groups:
            logging.debug(f"leaving {group}")
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
            logging.debug(f"deleted {deleted_entries} entries")
            session.delete(sheet)
            logging.debug(f"deleted {sheet}")
        # delete userlogin if existing
        if user_login := session.exec(
            select(UserLogin).where(UserLogin.user_id == user.id)
        ).first():
            logging.debug(f"deleting {user_login}")
            session.delete(user_login)
            session.commit()
        session.delete(user)
        session.commit()
        logging.debug(f"deleted {user}")
        return user


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


def get_user_from_storage() -> User:
    if user_id := app.storage.user.get("user_id"):
        user: User = get_user_by_id_name(user_id)
        return user


def get_user_by_id_name(user_id: str, session: Session = None) -> User:
    logging.debug(f"get_user_by_id_name {user_id}")
    if not session:
        with Session(engine) as session:
            return get_user_by_id_name(user_id, session)

    if found := session.exec(select(User).where(User.id_name == user_id)).first():
        for group in found.groups:
            group.name = sanitize_name(group.name)
        session.commit()
        session.refresh(found)
        return found
    logging.debug(f"User not found {user_id}")
    all_users = session.exec(select(User)).all()
    for user in all_users:
        logging.debug(str(user))


def user_may_see_sheet(user: User, sheet: ConsentSheet, session: Session):
    logging.debug(f"user_may_see_sheet {user} {sheet}")
    # is own sheet
    if sheet.user_id == user.id:
        return True
    # is in group
    if session.exec(
        select(RPGGroup).where(
            RPGGroup.users.any(User.id == user.id),
            RPGGroup.consent_sheets.any(ConsentSheet.id == sheet.id),
        )
    ).first():
        return True


def get_consent_sheet_by_id(user_id: int, sheet_id: int) -> ConsentSheet:
    logging.debug(f"get_consent_sheet_by_id {sheet_id} as {user_id}")
    with Session(engine) as session:
        if sheet := session.get(ConsentSheet, sheet_id):
            user = session.exec(select(User).where(User.id_name == user_id)).first()
            if not user:
                logging.warning(f"User not found {user_id}")
                all_users = session.exec(select(User)).all()
                for user in all_users:
                    logging.debug(user)
                return None
            if not user_may_see_sheet(user, sheet, session):
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
        existing_share_ids = set(
            session.exec(select(ConsentSheet.public_share_id)).all()
        )
        share_id = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        while share_id in existing_share_ids:
            share_id = "".join(
                random.choices(string.ascii_letters + string.digits, k=12)
            )
        return share_id


def update_custom_entry(entry: CustomConsentEntry):
    logging.debug(f"update_custom_entry {entry}")
    with Session(engine) as session:
        if entry.id:
            logging.debug(f"saved {entry}")
            session.merge(entry)
            session.commit()
        else:
            session.add(entry)
            session.commit()
            session.refresh(entry)
            logging.debug(f"saved {entry}")
            return entry


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
        session.add(group)
        session.commit()
        session.refresh(group)
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


def delete_sheet(sheet: ConsentSheet):
    logging.debug(f"delete_sheet {sheet}")
    with Session(engine) as session:
        sheet = session.get(ConsentSheet, sheet.id)
        session.delete(sheet)
        session.commit()
        logging.debug(f"deleted {sheet}")
        return sheet
