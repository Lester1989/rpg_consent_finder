import logging

from sqlmodel import Session, select

from models.db_models import (
    FAQItem,
    LocalizedText,
    UserContentQuestion,
    UserFAQ,
)
from models.model_utils import add_and_refresh, engine


def get_all_localized_texts() -> dict[int, LocalizedText]:
    logging.debug("get_all_localized_texts")
    with Session(engine) as session:
        return {text.id: text for text in session.exec(select(LocalizedText)).all()}


def store_faq_question(question: str):
    logging.debug(f"store_faq_question {question}")
    with Session(engine) as session:
        faq = UserFAQ(question=question)
        add_and_refresh(session, faq)
        return faq


def store_content_question(question: str):
    logging.debug(f"store_content_question {question}")
    with Session(engine) as session:
        content_question = UserContentQuestion(question=question)
        add_and_refresh(session, content_question)
        return content_question


def get_all_faq():
    logging.debug("get_all_faq")
    with Session(engine) as session:
        return session.exec(select(FAQItem)).all()
