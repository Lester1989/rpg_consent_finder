import logging
import random
import string
from models.models import (
    ConsentEntry,
    ConsentStatus,
    ConsentTemplate,
    RPGGroup,
    ConsentSheet,
    User,
    UserGroupLink,
    GroupConsentSheetLink,
)
from models.model_utils import engine, questioneer_id, hash_password
from sqlmodel import Session, select, delete


def seed_consent_questioneer():
    topics = {
        "Horror-Blut": "Das Beschreiben von Blut oder blutigen Szenen.\n\n Dabei ist auch das Zeigen von Blut oder blutigen Bildern und das Beschreiben von Geschmack, Geruch oder anderen Eigenschaften gemeint.",
        "Horror-Gore": "Gewalt oder Brutalität mit Blutvergießen oder Verstümmelung oder ernsthafte Verletzungen",
        "Horror-Verletzen von Tieren": "Verletzen oder Töten von Tieren. Das kann auch das Zeigen von Tierkadavern oder das Beschreiben von Tierquälerei sein. Es geht vor allen um Säugetiere, Vögel, Reptilien, Fische und Amphibien. Insekten, Spinnen oder Würmer sollten im Kommentarfeld genannt werden, falls sie für dich relevant sind.",
        "Horror-Verletzen von Kindern": "Gewalt oder Missbrauch an Kindern. Hier sind sowohl physische als auch psychische Gewalt gemeint. Jugendliche sind mitgemeint, die Grenze ist in etwa 18 Jahre, geht aber vor allem bei Kindlicher Darstellung auch darüber hinaus.",
        "Horror-Verletzen von Hilflosen": "Gewalt oder Missbrauch an Personen, die sich nicht wehren können. Das kann auch das Zeigen von Hilflosigkeit oder das Ausnutzen von Hilflosigkeit sein. Physische und psychische Gewalt sind gleichermaßen gemeint.",
        "Horror-Ratten": "Ratten oder andere Nagetiere(bitte als Kommentar angeben), die in einem Horror-Kontext auftreten. Das kann auch das Zeigen von Ratten oder das Beschreiben von Ratten sein.",
        "Horror-Spinnen / Insekten": "Spinnen oder Insekten, die in einem Horror-Kontext auftreten. Das kann auch das Zeigen von Spinnen oder Insekten oder das Beschreiben von Spinnen oder Insekten sein.",
        "Horror-Hilflosigkeit": "Hilflosigkeit oder Ausgeliefertsein in einem Horror-Kontext.",
        "Romantik-Schwarzblende": "Romantik, die nicht explizit beschrieben wird, sondern nur angedeutet und z.B. durch eine Schwarzblende/Zeitsprung übersprungen wird.",
        "Romantik-Explizit": "Das explizite Beschreiben von romantischen Szenen.",
        "Romantik-Zwischen SC und NSC": "Romantik, die zwischen einem SC und einem NSC stattfindet.",
        "Romantik-Zwischen SCs": "Romantik, die zwischen zwei SCs stattfindet.",
        "Romantik-Mit meinem Charakter": "Romantik, die mit dem eigenen Charakter.",
        "Sex-Schwarzblende": "Sex, der nicht explizit beschrieben wird, sondern nur angedeutet und z.B. durch eine Schwarzblende/Zeitsprung übersprungen wird.",
        "Sex-Explizit": "Das explizite Beschreiben von Sexszenen.",
        "Sex-Zwischen SC und NSC": "Sex, der zwischen einem SC und einem NSC stattfindet.",
        "Sex-Zwischen SCs": "Sex, der zwischen zwei SCs stattfindet.",
        "Sex-Mit meinem Charakter": "Sex, der mit dem eigenen Charakter stattfindet.",
        "Kulturell und Sozial-Queerfeindlichkeit": "Vorurteile, Diskriminierung oder Gewalt gegenüber queeren Menschen. Dabei sind auch herabsetzende Bemerkungen, Witze oder das Verwenden von Schimpfwörtern gemeint.",
        "Kulturell und Sozial-Rassismus": "Vorurteile, Diskriminierung oder Gewalt gegenüber Menschen aufgrund ihrer Hautfarbe oder Herkunft. Dabei sind auch herabsetzende Bemerkungen, Witze oder das Verwenden von Schimpfwörtern gemeint.",
        "Kulturell und Sozial-Sexismus": "Vorurteile, Diskriminierung oder Gewalt gegenüber Menschen aufgrund ihres Geschlechts. Dabei sind auch herabsetzende Bemerkungen, Witze oder das Verwenden von Schimpfwörtern gemeint.",
        "Kulturell und Sozial-reale Religion": "Das Darstellen von realen Religionen oder religiösen Praktiken. Dabei ist auch das Verwenden von religiösen Symbolen oder das Beschreiben von religiösen Ritualen gemeint.",
        "Kulturell und Sozial-Völkermord": "Das Darstellen von Völkermord oder Genozid.",
        "Kulturell und Sozial-Mobbing": "Gruppenbezogene Menschenfeindlichkeit, die sich in Form von Mobbing oder Ausgrenzung äußert.",
        "Kulturell und Sozial-Naturkatastrophen": "Das Darstellen von Naturkatastrophen oder Umweltkatastrophen.",
        "Gesundheit-Tödliche Krankheiten": "Das Darstellen von tödlichen Krankheiten oder Epidemien.",
        "Gesundheit-Psychische Krankheiten": "Das Darstellen von psychischen Erkrankungen.",
        "Gesundheit-Platzangst": "Das Darstellen von Platzangst oder klaustrophobischen Situationen.",
        "Gesundheit-Raumangst": "Das Darstellen von Raumangst oder agoraphobischen Situationen.",
        "Gesundheit-Erfrieren": "Das Darstellen von Erfrieren oder Erfrierung.",
        "Gesundheit-Ersticken": "Das Darstellen von Ersticken oder Atemnot.",
        "Gesundheit-Verhungern": "Das Darstellen von Verhungern oder Unterernährung.",
        "Gesundheit-Verdursten": "Das Darstellen von Verdursten oder Dehydrierung.",
        "Gesundheit-Schwangerschaft": "Das Darstellen von Schwangerschaft oder Geburt.",
        "Gesundheit-Fehlgeburt": "Das Darstellen von Fehlgeburt oder Totgeburt.",
        "Gesundheit-Abtreibung": "Das Darstellen von Abtreibung oder Schwangerschaftsabbruch.",
        "Gesundheit-Polizeigewalt": "Szenen, in denen Polizeigewalt oder Gewalt durch Sicherheitskräfte/Militär dargestellt wird.",
        "Gesundheit-Selbstverletzendes Verhalten": "Beschreibungen oder Darstellungen von selbstverletzendem Verhalten oder der Folgen davon.",
        "Gesundheit-Sexuelle Gewalt": "Gewalt oder Missbrauch in sexueller Form. Dabei sind sowohl physische als auch psychische Gewalt gemeint.",
        "Gesundheit-Psychische Gewalt": "Gewalt oder Missbrauch in psychischer Form. Dabei sind sowohl verbal als auch online Gewalt gemeint.",
        "Gesundheit-Folter": "Gewalt oder Missbrauch in Form von Folter. Dabei sind alle Formen Gewalt gemeint: Emotional, physisch, psychisch, sexuell.",
    }
    with Session(engine) as session:
        session.exec(delete(ConsentEntry))
        session.commit()
        for raw_topic in topics:
            logging.debug(f"Topic: {raw_topic}")
            category, topic = (
                raw_topic.split("-") if "-" in raw_topic else (raw_topic, None)
            )
            if not topic:
                continue
            existing_template = session.exec(
                select(ConsentTemplate).where(
                    ConsentTemplate.topic == topic, ConsentTemplate.category == category
                )
            ).first()
            if not existing_template:
                logging.debug("Creating template")
                session.add(
                    ConsentTemplate(
                        topic=topic, category=category, explanation=topics[raw_topic]
                    )
                )
        session.commit()
        all_templates = session.exec(select(ConsentTemplate)).all()
        logging.debug(f"Templates: {len(all_templates)}")
    # seed_users()


def seed_users():
    with Session(engine) as session:
        # clear
        session.exec(delete(RPGGroup))
        session.exec(delete(User))
        session.exec(delete(ConsentSheet))
        session.exec(delete(GroupConsentSheetLink))
        session.exec(delete(UserGroupLink))
        session.exec(delete(ConsentEntry))
        session.commit()

        # seed
        user_a = User(
            password_hash=hash_password("test"),
            nickname="User A",
            id_name="user_a",
            discord_id="",
            email="a@b.c",
        )
        user_b = User(
            password_hash=hash_password("test"),
            nickname="User B",
            id_name="user_b",
            discord_id="",
            email="b@c.d",
        )
        user_c = User(
            password_hash=hash_password("test"),
            nickname="User C",
            id_name="user_c",
            discord_id="",
            email="c@d.e",
        )
        session.add(user_a)
        session.add(user_b)
        session.add(user_c)
        session.commit()
        session.refresh(user_a)
        session.refresh(user_b)
        session.refresh(user_c)
        logging.debug("User A:", user_a)
        logging.debug("User B:", user_b)
        logging.debug("User C:", user_c)
        sheet_a_0 = seed_consent_sheet(session, user_a)
        sheet_a_0.public_share_id = "test123"
        session.commit()
        session.refresh(sheet_a_0)
        logging.debug("Sheet A:", sheet_a_0)
        sheet_a_1 = seed_consent_sheet(session, user_a)
        sheet_b = seed_consent_sheet(session, user_b)
        sheet_c = seed_consent_sheet(session, user_c)

        group_a = RPGGroup(
            name="Testgruppe",
            gm_id=user_a.id,
            gm_user=user_a,
            gm_consent_sheet_id=sheet_a_0.id,
            gm_consent_sheet=sheet_a_0,
            users=[user_b],
            consent_sheets=[sheet_b],
        )
        session.add(group_a)
        group_b = RPGGroup(
            name="Testgruppe 2",
            gm_id=user_b.id,
            gm_user=user_b,
            gm_consent_sheet_id=sheet_b.id,
            gm_consent_sheet=sheet_b,
            users=[user_a, user_c],
            consent_sheets=[sheet_a_1, sheet_c],
        )
        session.add(group_b)
        session.commit()
        session.refresh(group_a)
        session.refresh(group_b)
        logging.debug("Group:", group_a)
        logging.debug("Group:", group_b)


def seed_consent_sheet(session: Session, user: User) -> ConsentSheet:
    sheet = ConsentSheet(
        unique_name="".join(random.choices(string.ascii_letters + string.digits, k=8)),
        user_id=user.id,
        user=user,
    )
    session.add(sheet)
    session.commit()
    session.refresh(sheet)
    template_entries = session.exec(select(ConsentTemplate)).all()
    for template in template_entries:
        session.add(
            ConsentEntry(
                consent_sheet_id=sheet.id,
                consent_sheet=sheet,
                consent_template_id=template.id,
                consent_template=template,
                preference=random.choice(list(ConsentStatus)),
            )
        )
    session.commit()
    session.refresh(sheet)
    logging.debug("Sheet:", sheet)
    return sheet
