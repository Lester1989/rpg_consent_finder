import logging
import random
import string
from models.db_models import (
    ConsentEntry,
    ConsentStatus,
    ConsentTemplate,
    RPGGroup,
    ConsentSheet,
    User,
    UserGroupLink,
    GroupConsentSheetLink,
    FAQItem,
)
from models.model_utils import engine, questioneer_id, hash_password
from sqlmodel import Session, select, delete


def seed_consent_questioneer():
    topics = {
        "Horror-Blut": "Das Beschreiben von Blut oder blutigen Szenen.\n\n Dabei ist auch das Zeigen von Blut oder blutigen Bildern und das Beschreiben von Geschmack, Geruch oder anderen Eigenschaften gemeint.",
        "Horror-Gore": "Gewalt oder Brutalität mit Blutvergießen oder Verstümmelung oder ernsthafte Verletzungen",
        "Horror-Verletzen von Tieren": "Verletzen oder Töten von Tieren. Das kann auch das Zeigen von Tierkadavern oder das Beschreiben von Tierquälerei sein. Es geht vor allen um Säugetiere, Vögel, Reptilien, Fische und Amphibien. Insekten, Spinnen oder Würmer sollten im Kommentarfeld genannt werden, falls sie für dich relevant sind.",
        "Horror-Verletzen von Kindern": "Gewalt oder Missbrauch an Kindern. Hier sind sowohl physische als auch psychische Gewalt gemeint. Jugendliche sind mitgemeint, die Grenze ist in etwa 18 Jahre, geht aber vor allem bei Kindlicher Darstellung auch darüber hinaus.",
        "Horror-Pädophile": "Das Zeigen oder Beschreiben von Pädophilen oder deren Überlebenden. ",
        "Horror-Verletzen von Hilflosen": "Gewalt oder Missbrauch an Personen, die sich nicht wehren können. Das kann auch das Zeigen von Hilflosigkeit oder das Ausnutzen von Hilflosigkeit sein. Physische und psychische Gewalt sind gleichermaßen gemeint.",
        "Horror-Ratten": "Ratten oder andere Nagetiere(bitte als Kommentar angeben), die in einem Horror-Kontext auftreten. Das kann auch das Zeigen von Ratten oder das Beschreiben von Ratten sein.",
        "Horror-Spinnen / Insekten": "Spinnen oder Insekten, die in einem Horror-Kontext auftreten. Das kann auch das Zeigen von Spinnen oder Insekten oder das Beschreiben von Spinnen oder Insekten sein.",
        "Horror-Hilflosigkeit": "Hilflosigkeit oder Ausgeliefertsein in einem Horror-Kontext.",
        "Horror-Bedeutungslosigkeit": "Das Gefühl, dass das eigene Leben oder das Leben anderer keine Bedeutung hat. Alles was SCs wie unbedeutende Mikroben wirken lässt oder mit echter Unendlichkeit spielt.",
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
        "Kulturell und Sozial-Rassismus Real": "Vorurteile, Diskriminierung oder Gewalt gegenüber Menschen aufgrund ihrer Hautfarbe oder Herkunft. Dabei sind auch herabsetzende Bemerkungen, Witze oder das Verwenden von Schimpfwörtern gemeint.",
        "Kulturell und Sozial-Rassismus Fiction": "Vorurteile, Diskriminierung oder Gewalt gegenüber Lebensformen mit Bewusstsein aufgrund ihrer Hautfarbe oder Herkunft. Dabei sind auch herabsetzende Bemerkungen, Witze oder das Verwenden von Schimpfwörtern gemeint. Z.b. Orks, Ferengi oder andere fiktive Rassen.\n\n (Bedenke Grundsätzlich, dass viele fiktive Völker stark von realen rassistischen Vorurteilen beeinflusst sind) ",
        "Kulturell und Sozial-Sexismus": "Vorurteile, Diskriminierung oder Gewalt gegenüber Menschen aufgrund ihres Geschlechts. Dabei sind auch herabsetzende Bemerkungen, Witze oder das Verwenden von Schimpfwörtern gemeint.",
        "Kulturell und Sozial-reale Religion": "Das Darstellen von realen Religionen oder religiösen Praktiken. Dabei ist auch das Verwenden von religiösen Symbolen oder das Beschreiben von religiösen Ritualen gemeint.",
        "Kulturell und Sozial-Völkermord": "Das Darstellen von Völkermord oder Genozid.",
        "Kulturell und Sozial-Inzest": "Das Darstellen von Inzest oder sexuellen Beziehungen zwischen Verwandten.",
        "Kulturell und Sozial-Mobbing": "Gruppenbezogene Menschenfeindlichkeit, die sich in Form von Mobbing oder Ausgrenzung äußert.",
        "Kulturell und Sozial-Dickenfeindlichkeit": "Vorurteile, Diskriminierung oder Gewalt gegenüber dicken Menschen. Dabei sind auch herabsetzende Bemerkungen, Witze oder das Verwenden von Schimpfwörtern gemeint.",
        "Kulturell und Sozial-Behindertenfeindlichkeit": "Vorurteile, Diskriminierung oder Gewalt gegenüber Menschen mit Behinderungen. Dabei sind auch herabsetzende Bemerkungen, Witze oder das Verwenden von Schimpfwörtern gemeint.",
        "Kulturell und Sozial-Naturkatastrophen": "Das Darstellen von Naturkatastrophen oder Umweltkatastrophen.",
        "Gesundheit-Tod und Sterben": "Das Darstellen von Tod oder Sterben. Dabei sind sowohl natürliche als auch unnatürliche Tode gemeint. Auch das Auslöschen von Bewusstsein (Löschen von KI, Zerstören von fühlenden Robotern, vernichten von Untoten) ist gemeint.",
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
        "Gesundheit-Suizid/Selbstmord": "Beschreibungen oder Darstellungen von Selbstmord. Dabei ist der Versuch oder die Absicht mit gemeint",
        "Gesundheit-Sexuelle Gewalt": "Gewalt oder Missbrauch in sexueller Form. Dabei sind sowohl physische als auch psychische Gewalt gemeint.",
        "Gesundheit-Psychische Gewalt": "Gewalt oder Missbrauch in psychischer Form. Dabei sind sowohl verbal als auch online Gewalt gemeint.",
        "Gesundheit-Folter": "Gewalt oder Missbrauch in Form von Folter. Dabei sind alle Formen Gewalt gemeint: Emotional, physisch, psychisch, sexuell.",
        "Gesundheit-Verwahrlosung": "Das Darstellen von Verwahrlosung oder Vernachlässigung.",
    }
    with Session(engine) as session:
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
    seed_faq()


def seed_faq():
    faqs = {
        "Was ist das hier?": """
        Das ist ein Tool, um einen Konsent über Inhalte für Rollenspiele zu verwalten.

        Dabei ist es egal, ob es sich um ein Pen&Paper-Rollenspiel, ein LARP oder ein Computerspiel handelt.
        Das Tool hilft dabei, die Grenzen und Wünsche der Spieler:innen zu klären und zu dokumentieren.

        """,
        "Was sind Inhalte/Content?": """
        Inhalte sind alle Dinge, die in einem Rollenspiel vorkommen können und für einige Menschen belastend sind.

        Das können zum Beispiel Gewalt, Sex, Horror, Krankheiten, Diskriminierung oder andere Themen sein.

        Jede Person hat andere Grenzen und Wünsche, was sie in einem Rollenspiel erleben möchte.

        Deshalb ist es wichtig, dass alle Spieler:innen darüber sprechen und sich einigen, was im Spiel vorkommen darf und was nicht.
        Für eine Liste schau Oben in der Menüleiste unter `Content Trigger` nach.

        Zu jedem Inhalt gibt es 4 Einstufungen, eine Kommentarfunktion und ein "❔"->"nicht beantwortet".
        Um möglichst treffsicher einen Konsent zu bilden, wähle bitte eine Einstufung aus.
        Du kannst die Einstufung in einer Kategorie für alle Inhalte gleichzeitig setzen, indem du in der Kopfzeile auf die Einstufung klickst.
        Dabei wird die Einstufung von "❔" auf die gewählte Einstufung geändert. Inhalte, die bereits eine Einstufung haben, werden nicht verändert.
        """,
        """Bei den Inhalten fehlt etwas oder ist falsch. Was kann ich tun?""": """
        Unterhalb der `Content Trigger` findest du ein Formular, in dem du deine Frage oder dein Problem eingeben kannst.

        Bedenke, dass dieses Tool ein Hobbyprojekt von einem Vater mit Kleinkind ist und Antworten ein paar Tage dauern können.
        """,
        "Was ist ein Konsent?": """
        Ein Konsent ist eine Einigung zwischen Beteiligten, bei der sich alle wohlfühlen.

        Nicht zu verwechseln mit einem Kompromiss, bei dem sich irgendwo in der Mitte getroffen.

        Ein Konsent ist also eine klare und eindeutige Zustimmung zu etwas.
        """,
        "Was kann ich hier machen?": """
        Du kannst hier deine eigenen Grenzen für ein Rollenspiel festlegen und dokumentieren. Du kannst dazu `Consent Sheets` erstellen und pflegen.

        Diese Sheets kannst du entweder über einen Links teilen (öffentlich einsehbar) oder zu Gruppen zuordnen (nur für die Gruppe sichtbar).
        """,
        "Wie funktionieren Gruppen?": """
        Nachdem du dich angemeldet hast, kannst du Gruppen erstellen oder ihnen über einen Code beitreten.

        Gruppen, die du erstellst, verwaltest du, kannst also den Einladungscode sehen und erneuern oder Gruppenmitglieder entfernen.
        Außderm musst du einen `Consent Sheet` für die Gruppe erstellen. Du kannst deine Gruppen auch löschen.

        Gruppen, denen du begetreten bist, indem du den Einladungscode eingegeben hast, kannst du verlassen oder ihnen einen `Consent Sheet` zuweisen.

        In einer Gruppe wird automatisch der Konsent Aller gebildet und angezeigt.
        """,
        "Was ist ein Consent Sheet?": """
        Ein Consent Sheet ist eine Liste von Themen, die in einem Rollenspiel vorkommen können mit deinem Level des Wohlfühlens bei diesem Thema.

        Du kannst mehrere Sheets haben, z.B. für verschiedene Gruppen bzw. oder Öffentlichkeit.
        Versuch, es nicht zu übertreiben und nicht mehr als 10 Sheets zu haben. Gib den Sheets passende Namen, damit du sie wiederfindest.
        Da dieses Tool gratis ist, läuft es mit begrenzten Ressourcen, die Ich gerne fair verteilen nutzen möchte.
        Ich behalte mir vor, bei Missbrauch oder Überlastung, die Anzahl der Sheets zu limitieren und zu reduzieren.

        Wenn du einen Sheet öffentlich teilst, erhältst du einen Link und einen QR-Code, den du weitergeben kannst.
        Jeder mit diesem Link (erraten oder geteilt) kann deinen Sheet sehen, dabei werden weder dein Name, noch der Sheetname angezeigt.
        Die Kommentare sind jedoch sichtbar.
        """,
        """Eine Frage oder ein Problem, welches hier nicht beantwortet wird. Was kann ich tun?""": """
        Gib deine Frage unten ein und klick auf `Abschicken`. Ich werde versuchen, dir so schnell wie möglich zu antworten. Und die Frage in die FAQ aufnehmen.

        Wenn du deine Emailadresse oder Discord-ID angibst, kann ich dir auch direkt antworten.
        """,
    }
    with Session(engine) as session:
        session.exec(delete(FAQItem))
        session.commit()
        for question in faqs:
            logging.debug(f"Question: {question[:20]}... -> {faqs[question][:20]}...")
            existing_faq = session.exec(
                select(FAQItem).where(FAQItem.question == question)
            ).first()
            if not existing_faq:
                logging.debug("Creating FAQ")
                session.add(FAQItem(question=question, answer=faqs[question]))
        session.commit()
        all_faqs = session.exec(select(FAQItem)).all()
        logging.debug(f"FAQs: {len(all_faqs)}")


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
