import logging
from pathlib import Path

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
    UserContentQuestion,
    UserFAQ,
    UserGroupLink,
)
from models.model_utils import add_all_and_refresh, add_and_refresh, engine


def clear_all():
    with Session(engine) as session:
        session.exec(delete(ConsentTemplate))
        session.exec(delete(FAQItem))
        session.exec(delete(PlayFunQuestion))
        session.exec(delete(LocalizedText))
        session.exec(delete(ConsentEntry))
        session.exec(delete(ConsentSheet))
        session.exec(delete(RPGGroup))
        session.exec(delete(CustomConsentEntry))
        session.exec(delete(GroupConsentSheetLink))
        session.exec(delete(UserGroupLink))
        session.exec(delete(PlayFunResult))
        session.exec(delete(UserContentQuestion))
        session.exec(delete(UserFAQ))
        # session.exec(delete(User))
        # session.exec(delete(UserLogin))
        session.commit()


def seed_consent_questioneer():
    topic_files = Path("src", "seeding", "contents").glob("*.md")
    with Session(engine) as session:
        existing_templates = session.exec(select(ConsentTemplate)).all()
        category_cache: dict[str, LocalizedText] = {}
        for file in topic_files:
            category_en = file.stem.capitalize()
            category_de = {
                "horror": "Horror",
                "romance": "Romantik",
                "sex": "Sex",
                "social": "Sozial",
                "health": "Gesundheit",
            }[category_en.lower()]
            contents_de, contents_en = file.read_text(encoding="utf-8").split(
                "---ENG---"
            )
            for content_de, content_en in zip(
                contents_de.split("## "), contents_en.split("## ")
            ):
                if not content_de.strip() or not content_en.strip():
                    continue
                logging.debug(f"Content: {content_de[:20]}...")
                content_de, explanation_de = content_de.strip().split("\n", 1)
                content_en, explanation_en = content_en.strip().split("\n", 1)
                existing_template = any(
                    template.topic_local.text_de == content_de
                    for template in existing_templates
                )
                if existing_template:
                    continue
                logging.debug(f"Creating template for topic:{content_en}")
                local_topic = LocalizedText(text_en=content_en, text_de=content_de)
                local_category = category_cache.get(
                    category_en,
                    LocalizedText(text_en=category_en, text_de=category_de),
                )
                category_cache[category_en] = local_category
                local_explanation = LocalizedText(
                    text_en=explanation_en, text_de=explanation_de
                )
                add_all_and_refresh(
                    session, [local_topic, local_category, local_explanation]
                )
                session.add(
                    ConsentTemplate(
                        category_id=local_category.id,
                        category_local=local_category,
                        topic_id=local_topic.id,
                        topic_local=local_topic,
                        explanation_id=local_explanation.id,
                        explanation_local=local_explanation,
                    )
                )
                session.commit()

        all_templates = session.exec(select(ConsentTemplate)).all()
        logging.debug(f"Templates: {len(all_templates)}")
    # seed_users()
    seed_faq()
    seed_playfun_questions()


def seed_faq():
    faqs_files = [
        file.read_text(encoding="utf-8").split("---ENG---")
        for file in Path("src", "seeding", "faqs").glob("*.md")
    ]
    with Session(engine) as session:
        session.exec(delete(FAQItem))
        session.commit()
        for all_de, all_en in faqs_files:
            question_de, answer_de = all_de.strip().split("\n", 1)
            question_en, answer_en = all_en.strip().split("\n", 1)
            logging.debug(f"Question: {question_de[:20]}...")
            logging.debug(f"Anser: {answer_de[:10]}...{answer_de[-10:]}")
            logging.debug(f"Question: {question_en[:20]}...")
            logging.debug(f"Anser: {answer_en[:10]}...{answer_en[-10:]}")
            existing_question = session.exec(
                select(LocalizedText).where(
                    LocalizedText.text_de == question_de,
                    LocalizedText.text_en == question_en,
                )
            ).first()
            existing_answer = session.exec(
                select(LocalizedText).where(
                    LocalizedText.text_de == answer_de,
                    LocalizedText.text_en == answer_en,
                )
            ).first()

            local_question = existing_question or LocalizedText(
                text_en=question_en, text_de=question_de
            )
            local_answer = existing_answer or LocalizedText(
                text_en=answer_en,
                text_de=answer_de,
            )
            if local_question.id:
                session.merge(local_question)
                session.commit()
            else:
                add_and_refresh(session, local_question)
            if local_answer.id:
                session.merge(local_answer)
                session.commit()
            else:
                add_and_refresh(session, local_answer)

            existing_faq = session.exec(
                select(FAQItem).where(
                    FAQItem.question_id == local_question.id,
                    FAQItem.answer_id == local_answer.id,
                )
            ).first()
            if existing_faq:
                continue
            session.add(
                FAQItem(
                    answer_id=local_answer.id,
                    answer_local=local_answer,
                    question_id=local_question.id,
                    question_local=local_question,
                )
            )
            session.commit()

        all_faqs = session.exec(select(FAQItem)).all()
        logging.debug(f"FAQs: {len(all_faqs)}")


def make_playfun_question(
    statement_de: str,
    statement_en: str,
    play_style: str,
    session: Session,
    existing_questions: list[PlayFunQuestion],
    existing_texts: list[LocalizedText],
    weight: int = 1,
):
    existing_question = any(
        question.question_local.text_de == statement_de
        for question in existing_questions
    )
    if existing_question:
        return
    local_statement = LocalizedText(text_en=statement_en, text_de=statement_de)
    existing_text = any(text.text_de == statement_de for text in existing_texts)
    if not existing_text:
        add_and_refresh(session, local_statement)
    session.add(
        PlayFunQuestion(
            play_style=play_style,
            question_id=local_statement.id,
            question_local=local_statement,
            weight=weight,
        )
    )
    session.commit()


def seed_playfun_questions():
    files = Path("src", "seeding", "playfun").glob("*.md")
    with Session(engine) as session:
        existing_questions = session.exec(select(PlayFunQuestion)).all()
        existing_texts = session.exec(select(LocalizedText)).all()
        logging.debug(f"Questions: {len(existing_questions)}")
        logging.debug(f"Texts: {len(existing_texts)}")
        for file in files:
            play_style = file.stem.capitalize()
            content_de, content_en = (
                file.read_text(encoding="utf-8")
                .replace(f"# {file.stem}\n", "")
                .strip()
                .split("---ENG---")
            )
            weigth_plus_de_raw, weight_minus_de_raw = content_de.split("## -1")
            weigth_plus_en_raw, weight_minus_en_raw = content_en.split("## -1")
            weigth_plus_de = [
                line.strip("-").strip()
                for line in weigth_plus_de_raw.split("\n")
                if line.strip().startswith("-")
            ]
            weigth_minus_de = [
                line.strip("-").strip()
                for line in weight_minus_de_raw.split("\n")
                if line.strip().startswith("-")
            ]
            weigth_plus_en = [
                line.strip("-").strip()
                for line in weigth_plus_en_raw.split("\n")
                if line.strip().startswith("-")
            ]
            weigth_minus_en = [
                line.strip("-").strip()
                for line in weight_minus_en_raw.split("\n")
                if line.strip().startswith("-")
            ]
            for statement_de, statement_en in zip(weigth_plus_de, weigth_plus_en):
                logging.debug(f"Statement +: {statement_de[:20]}... ")
                make_playfun_question(
                    statement_de,
                    statement_en,
                    play_style,
                    session,
                    existing_questions,
                    existing_texts,
                    1,
                )
            for statement_de, statement_en in zip(weigth_minus_de, weigth_minus_en):
                logging.debug(f"Statement -: {statement_de[:20]}...")
                make_playfun_question(
                    statement_de,
                    statement_en,
                    play_style,
                    session,
                    existing_questions,
                    existing_texts,
                    -1,
                )
