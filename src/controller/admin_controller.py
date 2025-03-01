import logging

from sqlmodel import Session, delete, select

from models.db_models import (
    ConsentEntry,
    ConsentSheet,
    ConsentTemplate,
    CustomConsentEntry,
    FAQItem,
    GroupConsentSheetLink,
    LocalizedText,
    PlayFunQuestion,
    PlayFunResult,
    RPGGroup,
    User,
    UserContentQuestion,
    UserFAQ,
    UserGroupLink,
)
from models.model_utils import add_and_refresh, engine


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
            add_and_refresh(session, text)
            logging.debug(f"added {text}")
        return text


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


def get_status():
    logging.debug("get_status")
    with Session(engine) as session:
        return {
            "sheets": (
                len(session.exec(select(ConsentSheet)).all()),
                lambda: clear_table(ConsentSheet),
            ),
            "entries": (
                len(session.exec(select(ConsentEntry)).all()),
                lambda: clear_table(ConsentEntry),
            ),
            "templates": (
                len(session.exec(select(ConsentTemplate)).all()),
                lambda: clear_table(ConsentTemplate),
            ),
            "custom_entries": (
                len(session.exec(select(CustomConsentEntry)).all()),
                lambda: clear_table(CustomConsentEntry),
            ),
            "groups": (
                len(session.exec(select(RPGGroup)).all()),
                lambda: clear_table(RPGGroup),
            ),
            "users": (len(session.exec(select(User)).all()), lambda: clear_table(User)),
            "group_sheet_links": (
                len(session.exec(select(GroupConsentSheetLink)).all()),
                lambda: clear_table(GroupConsentSheetLink),
            ),
            "user_group_links": (
                len(session.exec(select(UserGroupLink)).all()),
                lambda: clear_table(UserGroupLink),
            ),
            "local_texts": (
                len(session.exec(select(LocalizedText)).all()),
                lambda: clear_table(LocalizedText),
            ),
            "faq_items": (
                len(session.exec(select(FAQItem)).all()),
                lambda: clear_table(FAQItem),
            ),
            "content_questions": (
                len(session.exec(select(UserContentQuestion)).all()),
                lambda: clear_table(UserContentQuestion),
            ),
            "faq_questions": (
                len(session.exec(select(UserFAQ)).all()),
                lambda: clear_table(UserFAQ),
            ),
            "playfun_questions": (
                len(session.exec(select(PlayFunQuestion)).all()),
                lambda: clear_table(PlayFunQuestion),
            ),
            "playfun_results": (
                len(session.exec(select(PlayFunResult)).all()),
                lambda: clear_table(PlayFunResult),
            ),
        }


def clear_table(table):
    logging.debug(f"clear_table {table}")
    with Session(engine) as session:
        logging.debug(session.exec(delete(table)).rowcount)
        session.commit()
        return get_status()


def get_all_faq_questions():
    logging.debug("get_all_faq_questions")
    with Session(engine) as session:
        return session.exec(select(UserFAQ)).all()


def get_all_content_questions():
    logging.debug("get_all_content_questions")
    with Session(engine) as session:
        return session.exec(select(UserContentQuestion)).all()


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
        add_and_refresh(session, content_template)
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
        add_and_refresh(session, faq)
        return faq
