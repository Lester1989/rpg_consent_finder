import logging
import random

from sqlmodel import Session, select

from models.db_models import (
    PlayFunQuestion,
    PlayFunResult,
    User,
)
from models.model_utils import add_and_refresh, engine


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
        add_and_refresh(session, playfun_result)
        return playfun_result
