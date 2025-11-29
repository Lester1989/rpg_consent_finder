import logging
import random
from sqlmodel import Session, select

from a_logger_setup import LOGGER_NAME
from models.db_models import (
    PlayFunQuestion,
    PlayFunResult,
    PlayFunAnswer,
    User,
)
from models.model_utils import add_and_refresh, session_scope


LOGGER = logging.getLogger(LOGGER_NAME)


def get_playfun_questions(
    shuffled: bool = True, session: Session | None = None
) -> list[PlayFunQuestion]:
    LOGGER.info("get_playfun_questions")

    def _query(active_session: Session) -> list[PlayFunQuestion]:
        questions = active_session.exec(select(PlayFunQuestion)).all()
        if shuffled:
            random.shuffle(questions)
        return questions

    if session is not None:
        return _query(session)

    with session_scope() as scoped_session:
        return _query(scoped_session)


def store_playfun_result(
    user: User, playfun_result: PlayFunResult, session: Session | None = None
) -> PlayFunResult:
    LOGGER.debug("store_playfun_result %s %s", user, playfun_result)
    playfun_result.user_id = user.id

    def _persist(active_session: Session) -> PlayFunResult:
        add_and_refresh(active_session, playfun_result)
        return playfun_result

    if session is not None:
        return _persist(session)

    with session_scope() as scoped_session:
        return _persist(scoped_session)


def get_playfun_result_by_id(
    user: User, session: Session | None = None
) -> PlayFunResult:
    LOGGER.debug("get_playfun_result_by_id %s", user)

    def _load(active_session: Session) -> PlayFunResult:
        existing_result = active_session.exec(
            select(PlayFunResult).where(PlayFunResult.user_id == user.id)
        ).first()
        if existing_result:
            return existing_result
        new_result = PlayFunResult(user_id=user.id)
        add_and_refresh(active_session, new_result)
        return new_result

    if session is not None:
        return _load(session)

    with session_scope() as scoped_session:
        return _load(scoped_session)


def update_playfun_answer(
    question: PlayFunQuestion,
    rating: int,
    result: PlayFunResult,
    session: Session | None = None,
) -> PlayFunAnswer:
    LOGGER.debug("update_playfun_answer %s %s %s", question, rating, result)

    def _update(active_session: Session) -> PlayFunAnswer:
        active_result = active_session.get(PlayFunResult, result.id)
        if not active_result:
            return None
        answer = active_session.exec(
            select(PlayFunAnswer).where(
                PlayFunAnswer.question_id == question.id,
                PlayFunAnswer.result_id == result.id,
            )
        ).first()
        if answer:
            answer.rating = rating
        else:
            answer = PlayFunAnswer(
                question_id=question.id, result_id=result.id, rating=rating
            )
        # Update the ratings in the PlayFunResult

        active_result.set_rating(question.play_style.lower(), rating)
        LOGGER.debug("Updated PlayFunResult %s", active_result)

        add_and_refresh(active_session, answer)
        return answer

    if session is not None:
        return _update(session)

    with session_scope() as scoped_session:
        return _update(scoped_session)


def get_playfun_answers_for_user(
    user: User, session: Session | None = None
) -> list[PlayFunAnswer]:
    def _fetch(active_session: Session) -> list[PlayFunAnswer]:
        result = get_playfun_result_by_id(user, session=active_session)
        return get_playfun_answers_for_result(result, session=active_session)

    if session is not None:
        return _fetch(session)

    with session_scope() as scoped_session:
        return _fetch(scoped_session)


def get_playfun_answers_for_result(
    result: PlayFunResult, session: Session | None = None
) -> list[PlayFunAnswer]:
    LOGGER.debug("get_playfun_answers_for_result %s", result)

    def _query(active_session: Session) -> list[PlayFunAnswer]:
        return active_session.exec(
            select(PlayFunAnswer).where(PlayFunAnswer.result_id == result.id)
        ).all()

    if session is not None:
        return _query(session)

    with session_scope() as scoped_session:
        return _query(scoped_session)
