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
    LocalizedText,
)
from models.model_utils import engine, generate_group_name_id, hash_password
from sqlmodel import Session, select, delete

category_translations = {
    "Horror": "Horror",
    "Romantik": "Romance",
    "Sex": "Sex",
    "Kulturell und Sozial": "Cultural and Social",
    "Gesundheit": "Health",
}
topic_translations = {
    "Blut": "Blood",
    "Gore": "Gore",
    "Verletzen von Tieren": "Hurting Animals",
    "Verletzen von Kindern": "Hurting Children",
    "Verletzen von Hilflosen": "Hurting Helpless",
    "Pädophile": "Pedophiles",
    "Ratten": "Rats",
    "Spinnen": "Spiders",
    "Insekten": "Insects",
    "Hilflosigkeit": "Helplessness",
    "Bedeutungslosigkeit": "Meaninglessness",
    "Schwarzblende": "Fade to Black",
    "Explizit": "Explicit",
    "Zwischen SC und NSC": "Between PC and NPC",
    "Zwischen SCs": "Between PCs",
    "Mit meinem Charakter": "With my Character",
    "Queerfeindlichkeit": "Queerhostility",
    "Rassismus Real": "Real Racism",
    "Rassismus Fiction": "Fictional Racism",
    "Sexismus": "Sexism",
    "reale Religion": "Real Religion",
    "Völkermord": "Genocide",
    "Inzest": "Incest",
    "Mobbing": "Bullying",
    "Dickenfeindlichkeit": "Fatphobia",
    "Behindertenfeindlichkeit": "Ableism",
    "Naturkatastrophen": "Natural Disasters",
    "Tod und Sterben": "Death and Dying",
    "Tödliche Krankheiten": "Deadly Diseases",
    "Psychische Krankheiten": "Mental Illness",
    "Platzangst": "Claustrophobia",
    "Raumangst": "Agoraphobia",
    "Erfrieren": "Freezing",
    "Ersticken": "Suffocation",
    "Verhungern": "Starvation",
    "Verdursten": "Dehydration",
    "Schwangerschaft": "Pregnancy",
    "Fehlgeburt": "Miscarriage",
    "Abtreibung": "Abortion",
    "Polizeigewalt": "Police Violence",
    "Selbstverletzendes Verhalten": "Self-Harm",
    "Suizid/Selbstmord": "Suicide",
    "Sexuelle Gewalt": "Sexual Violence",
    "Psychische Gewalt": "Mental Abuse",
    "Folter": "Torture",
    "Verwahrlosung": "Neglect",
}


def seed_consent_questioneer():
    topics = {
        "Horror-Blut": (
            "Das Beschreiben von Blut oder blutigen Szenen.\n\n Dabei ist auch das Zeigen von Blut oder blutigen Bildern und das Beschreiben von Geschmack, Geruch oder anderen Eigenschaften gemeint.",
            "Describing blood or gory scenes.\n\n This includes showing blood or gory images and describing the taste, smell or other characteristics.",
        ),
        "Horror-Gore": (
            "Gewalt oder Brutalität mit Blutvergießen oder Verstümmelung oder ernsthafte Verletzungen",
            "Violence or brutality involving bloodshed or mutilation or serious injury",
        ),
        "Horror-Verletzen von Tieren": (
            "Verletzen oder Töten von Tieren. Das kann auch das Zeigen von Tierkadavern oder das Beschreiben von Tierquälerei sein. Es geht vor allen um Säugetiere, Vögel, Reptilien, Fische und Amphibien. Insekten, Spinnen oder Würmer sollten im Kommentarfeld genannt werden, falls sie für dich relevant sind.",
            "Harming or killing animals. This can also include showing animal carcasses or describing cruelty to animals. It is mainly about mammals, birds, reptiles, fish and amphibians. Insects, spiders or worms should be mentioned in the comment field if they are relevant to you.",
        ),
        "Horror-Verletzen von Kindern": (
            "Gewalt oder Missbrauch an Kindern. Hier sind sowohl physische als auch psychische Gewalt gemeint. Jugendliche sind mitgemeint, die Grenze ist in etwa 18 Jahre, geht aber vor allem bei Kindlicher Darstellung auch darüber hinaus.",
            "Violence or abuse against children. This includes both physical and psychological violence. Adolescents are included, the limit is around 18 years, but also goes beyond this, especially in the case of depictions of children.",
        ),
        "Horror-Pädophile": (
            "Das Zeigen oder Beschreiben von Pädophilen oder deren Überlebenden. ",
            "Showing or describing paedophiles or their survivors. ",
        ),
        "Horror-Verletzen von Hilflosen": (
            "Gewalt oder Missbrauch an Personen, die sich nicht wehren können. Das kann auch das Zeigen von Hilflosigkeit oder das Ausnutzen von Hilflosigkeit sein. Physische und psychische Gewalt sind gleichermaßen gemeint.",
            "Violence or abuse against people who are unable to defend themselves. This can also be the showing of helplessness or the exploitation of helplessness. Physical and psychological violence are meant equally.",
        ),
        "Horror-Ratten": (
            "Ratten oder andere Nagetiere(bitte als Kommentar angeben), die in einem Horror-Kontext auftreten. Das kann auch das Zeigen von Ratten oder das Beschreiben von Ratten sein.",
            "Rats or other rodents (please specify as a comment) that appear in a horror context. This can also be showing rats or describing rats.",
        ),
        "Horror-Spinnen": (
            "Spinnen die in einem Horror-Kontext auftreten. Das kann auch das Zeigen von Spinnen oder das Beschreiben von Spinnen sein.",
            "Spiders that appear in a horror context. This can also include showing spiders or describing spiders.",
        ),
        "Horror-Insekten": (
            "Insekten, die in einem Horror-Kontext auftreten. Das kann auch das Zeigen von Insekten oder das Beschreiben von Insekten sein.",
            "Insects that appear in a horror context. This can also include showing insects or describing insects.",
        ),
        "Horror-Zähne": (
            "Das Zeigen oder Beschreiben von Zähnen in einem Horrorkontext. Das könnte die Beschreibung von Zahnverletzungen, Zahnverlust oder Zahnverfall sein. Auch Szenen beim Zahnarzt oder Ähnlichem können gemeint sein.",
            "Showing or describing teeth in a horror context. This could be the description of tooth injuries, tooth loss or tooth decay. Scenes at the dentist or similar could also be meant.",
        ),
        "Horror-Hilflosigkeit": (
            "Hilflosigkeit oder Ausgeliefertsein in einem Horror-Kontext.",
            "Helplessness or being at the mercy of others in a horror context.",
        ),
        "Horror-Bedeutungslosigkeit": (
            "Das Gefühl, dass das eigene Leben oder das Leben anderer keine Bedeutung hat. Alles was SCs wie unbedeutende Mikroben wirken lässt oder mit echter Unendlichkeit spielt.",
            "The feeling that your own life or the lives of others have no meaning. Anything that makes SCs seem like insignificant microbes or plays with real infinity.",
        ),
        "Romantik-Schwarzblende": (
            "Romantik, die nicht explizit beschrieben wird, sondern nur angedeutet und z.B. durch eine Schwarzblende/Zeitsprung übersprungen wird.",
            "Romance that is not explicitly described, but only hinted at and skipped over e.g. by a fade to black/time jump.",
        ),
        "Romantik-Explizit": (
            "Das explizite Beschreiben von romantischen Szenen.",
            "The explicit description of romantic scenes.",
        ),
        "Romantik-Zwischen SC und NSC": (
            "Romantik, die zwischen einem SC und einem NSC stattfindet.",
            "Romance that takes place between an SC and an NPC.",
        ),
        "Romantik-Zwischen SCs": (
            "Romantik, die zwischen zwei SCs stattfindet.",
            "Romance that takes place between two SCs.",
        ),
        "Romantik-Mit meinem Charakter": (
            "Romantik, die mit dem eigenen Charakter.",
            "Romance that takes place with your own character.",
        ),
        "Sex-Schwarzblende": (
            "Sex, der nicht explizit beschrieben wird, sondern nur angedeutet und z.B. durch eine Schwarzblende/Zeitsprung übersprungen wird.",
            "Sex that is not explicitly described, but only hinted at and e.g. skipped by a fade to black/time jump.",
        ),
        "Sex-Explizit": (
            "Das explizite Beschreiben von Sexszenen.",
            "The explicit description of sex scenes.",
        ),
        "Sex-Zwischen SC und NSC": (
            "Sex, der zwischen einem SC und einem NSC stattfindet.",
            "Sex that takes place between an SC and an NPC.",
        ),
        "Sex-Zwischen SCs": (
            "Sex, der zwischen zwei SCs stattfindet.",
            "Sex that takes place between two SCs.",
        ),
        "Sex-Mit meinem Charakter": (
            "Sex, der mit dem eigenen Charakter stattfindet.",
            "Sex that takes place with your own character.",
        ),
        "Kulturell und Sozial-Queerfeindlichkeit": (
            "Vorurteile, Diskriminierung oder Gewalt gegenüber queeren Menschen. Dabei sind auch herabsetzende Bemerkungen, Witze oder das Verwenden von Schimpfwörtern gemeint.",
            "Prejudice, discrimination or violence towards queer people. This also includes derogatory remarks, jokes or the use of swear words.",
        ),
        "Kulturell und Sozial-Rassismus Real": (
            "Vorurteile, Diskriminierung oder Gewalt gegenüber Menschen aufgrund ihrer Hautfarbe oder Herkunft. Dabei sind auch herabsetzende Bemerkungen, Witze oder das Verwenden von Schimpfwörtern gemeint.",
            "Prejudice, discrimination or violence against people based on their skin color or origin. This also includes derogatory remarks, jokes or the use of swear words.",
        ),
        "Kulturell und Sozial-Rassismus Fiction": (
            "Vorurteile, Diskriminierung oder Gewalt gegenüber Lebensformen mit Bewusstsein aufgrund ihrer Hautfarbe oder Herkunft. Dabei sind auch herabsetzende Bemerkungen, Witze oder das Verwenden von Schimpfwörtern gemeint. Z.b. Orks, Ferengi oder andere fiktive Rassen.\n\n (Bedenke Grundsätzlich, dass viele fiktive Völker stark von realen rassistischen Vorurteilen beeinflusst sind) ",
            "Prejudice, discrimination or violence against conscious people because of their skin color or origin. This also includes derogatory remarks, jokes or the use of swear words. E.g. Orcs, Ferengi or other fictional races.\n\n (Please note that many fictional races are strongly influenced by real racial prejudices) ",
        ),
        "Kulturell und Sozial-Sexismus": (
            "Vorurteile, Diskriminierung oder Gewalt gegenüber Menschen aufgrund ihres Geschlechts. Dabei sind auch herabsetzende Bemerkungen, Witze oder das Verwenden von Schimpfwörtern gemeint.",
            "Prejudice, discrimination or violence against people based on their gender. This also includes derogatory remarks, jokes or the use of swear words.",
        ),
        "Kulturell und Sozial-reale Religion": (
            "Das Darstellen von realen Religionen oder religiösen Praktiken. Dabei ist auch das Verwenden von religiösen Symbolen oder das Beschreiben von religiösen Ritualen gemeint.",
            "The depiction of real religions or religious practices. This also includes the use of religious symbols or the description of religious rituals.",
        ),
        "Kulturell und Sozial-Völkermord": (
            "Das Darstellen von Völkermord oder Genozid.",
            "Depicting genocide or genocide.",
        ),
        "Kulturell und Sozial-Inzest": (
            "Das Darstellen von Inzest oder sexuellen Beziehungen zwischen Verwandten.",
            "Depicting incest or sexual relationships between relatives.",
        ),
        "Kulturell und Sozial-Mobbing": (
            "Gruppenbezogene Menschenfeindlichkeit, die sich in Form von Mobbing oder Ausgrenzung äußert.",
            "Group-related misanthropy that manifests itself in the form of bullying or exclusion.",
        ),
        "Kulturell und Sozial-Dickenfeindlichkeit": (
            "Vorurteile, Diskriminierung oder Gewalt gegenüber dicken Menschen. Dabei sind auch herabsetzende Bemerkungen, Witze oder das Verwenden von Schimpfwörtern gemeint.",
            "Prejudice, discrimination or violence against fat people. This also includes derogatory remarks, jokes or the use of swear words.",
        ),
        "Kulturell und Sozial-Behindertenfeindlichkeit": (
            "Vorurteile, Diskriminierung oder Gewalt gegenüber Menschen mit Behinderungen. Dabei sind auch herabsetzende Bemerkungen, Witze oder das Verwenden von Schimpfwörtern gemeint.",
            "Prejudice, discrimination or violence against people with disabilities. This also includes derogatory remarks, jokes or the use of swear words.",
        ),
        "Kulturell und Sozial-Naturkatastrophen": (
            "Das Darstellen von Naturkatastrophen oder Umweltkatastrophen.",
            "Depicting natural disasters or environmental catastrophes.",
        ),
        "Gesundheit-Tod und Sterben": (
            "Das Darstellen von Tod oder Sterben. Dabei sind sowohl natürliche als auch unnatürliche Tode gemeint. Auch das Auslöschen von Bewusstsein (Löschen von KI, Zerstören von fühlenden Robotern, vernichten von Untoten) ist gemeint.",
            "The depiction of death or dying. This includes both natural and unnatural deaths. The extinguishing of consciousness (deleting AI, destroying sentient robots, destroying the undead) is also meant.",
        ),
        "Gesundheit-Tödliche Krankheiten": (
            "Das Darstellen von tödlichen Krankheiten oder Epidemien.",
            "The representation of deadly diseases or epidemics.",
        ),
        "Gesundheit-Psychische Krankheiten": (
            "Das Darstellen von psychischen Erkrankungen.",
            "The representation of mental illness.",
        ),
        "Gesundheit-Platzangst": (
            "Das Darstellen von Platzangst oder klaustrophobischen Situationen.",
            "Representing claustrophobic situations.",
        ),
        "Gesundheit-Raumangst": (
            "Das Darstellen von Raumangst oder agoraphobischen Situationen.",
            "Representing agoraphobic situations.",
        ),
        "Gesundheit-Erfrieren": (
            "Das Darstellen von Erfrieren oder Erfrierung.",
            "The representation of freezing or frostbite.",
        ),
        "Gesundheit-Ersticken": (
            "Das Darstellen von Ersticken oder Atemnot.",
            "Representing suffocation or shortness of breath.",
        ),
        "Gesundheit-Verhungern": (
            "Das Darstellen von Verhungern oder Unterernährung.",
            "Representing starvation or malnutrition.",
        ),
        "Gesundheit-Verdursten": (
            "Das Darstellen von Verdursten oder Dehydrierung.",
            "The representation of dying of thirst or dehydration.",
        ),
        "Gesundheit-Schwangerschaft": (
            "Das Darstellen von Schwangerschaft oder Geburt.",
            "Depicting pregnancy or childbirth.",
        ),
        "Gesundheit-Fehlgeburt": (
            "Das Darstellen von Fehlgeburt oder Totgeburt.",
            "Depicting miscarriage or stillbirth.",
        ),
        "Gesundheit-Abtreibung": (
            "Das Darstellen von Abtreibung oder Schwangerschaftsabbruch.",
            "The depiction of abortion or termination of pregnancy.",
        ),
        "Gesundheit-Polizeigewalt": (
            "Szenen, in denen Polizeigewalt oder Gewalt durch Sicherheitskräfte/Militär dargestellt wird.",
            "Scenes depicting police violence or violence by security forces/military.",
        ),
        "Gesundheit-Selbstverletzendes Verhalten": (
            "Beschreibungen oder Darstellungen von selbstverletzendem Verhalten oder der Folgen davon.",
            "Descriptions or depictions of self-harming behavior or the consequences thereof.",
        ),
        "Gesundheit-Suizid/Selbstmord": (
            "Beschreibungen oder Darstellungen von Selbstmord. Dabei ist der Versuch oder die Absicht mit gemeint",
            "Descriptions or depictions of suicide. This includes the attempt or intention",
        ),
        "Gesundheit-Sexuelle Gewalt": (
            "Gewalt oder Missbrauch in sexueller Form. Dabei sind sowohl physische als auch psychische Gewalt gemeint.",
            "Violence or abuse in a sexual form. This includes both physical and psychological violence.",
        ),
        "Gesundheit-Psychische Gewalt": (
            "Gewalt oder Missbrauch in psychischer Form. Dabei sind sowohl verbal als auch online Gewalt gemeint.",
            "Violence or abuse in a psychological form. This includes both verbal and online violence.",
        ),
        "Gesundheit-Folter": (
            "Gewalt oder Missbrauch in Form von Folter. Dabei sind alle Formen Gewalt gemeint: Emotional, physisch, psychisch, sexuell.",
            "Violence or abuse in the form of torture. This refers to all forms of violence: emotional, physical, psychological, sexual.",
        ),
        "Gesundheit-Verwahrlosung": (
            "Das Darstellen von Verwahrlosung oder Vernachlässigung.",
            "The depiction of neglect or abandonment.",
        ),
    }
    with Session(engine) as session:
        existing_templates = session.exec(select(ConsentTemplate)).all()
        category_cache: dict[str, LocalizedText] = {}
        for raw_topic in topics:
            logging.debug(f"Topic: {raw_topic}")
            category, topic = (
                raw_topic.split("-") if "-" in raw_topic else (raw_topic, None)
            )
            if not topic:
                continue
            existing_template = any(
                template.topic_local.text_de == topic for template in existing_templates
            )
            if not existing_template:
                logging.debug(f"Creating template for topic:{topic}")
                local_topic = LocalizedText(
                    text_en=topic_translations[topic], text_de=topic
                )
                local_category = category_cache.get(
                    category,
                    LocalizedText(
                        text_en=category_translations[category], text_de=category
                    ),
                )
                category_cache[category] = local_category
                local_explanation = LocalizedText(
                    text_en=topics[raw_topic][1], text_de=topics[raw_topic][0]
                )
                session.add_all([local_topic, local_category, local_explanation])
                session.commit()
                session.refresh(local_topic)
                session.refresh(local_category)
                session.refresh(local_explanation)
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


def seed_faq():
    faqs = {
        ("Was ist das hier?", "What is this Website's Purpose?"): (
            """
        Das ist ein Tool, um einen Konsent über Inhalte für Rollenspiele zu verwalten.

        Dabei ist es egal, ob es sich um ein Pen&Paper-Rollenspiel, ein LARP oder ein Computerspiel handelt.
        Das Tool hilft dabei, die Grenzen und Wünsche der Spieler:innen zu klären und zu dokumentieren.

        """,
            """
        This is a tool for managing a content consensus for role-playing games.

        It doesn't matter whether it's a pen & paper role-playing game, a LARP or a computer game.
        The tool helps to clarify and document the boundaries and wishes of the players.

        """,
        ),
        ("Was sind Inhalte/Content?", "What is a Content?"): (
            """
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
            """
        Content includes all things that can occur in a role-playing game and are stressful for some people.

        This could be violence, sex, horror, illness, discrimination or other topics, for example.

        Each person has different limits and wishes as to what they want to experience in a role-playing game.

        That's why it's important that all players talk about this and agree on what is and isn't allowed in the game.
        For a list, look at the top of the menu bar under 'Content Triggers'.

        For each content there are 4 classifications, a comment function and a “❔”->“not answered”.
        To form a consensus as accurately as possible, please select a rating.
        You can set the rating in a category for all content at the same time by clicking on the rating in the header.
        This will change the classification from “❔” to the selected classification. Content that already has a classification will not be changed.
        """,
        ),
        (
            "Bei den Inhalten fehlt etwas oder ist falsch. Was kann ich tun?",
            "Something is missing or incorrect in the contents. What can I do?",
        ): (
            """
        Unten auf der `Content`-Seite findest du ein Formular, in dem du deine Frage oder dein Problem eingeben kannst.

        Bedenke, dass dieses Tool ein Hobbyprojekt von einem Vater mit Kleinkind ist und Antworten ein paar Tage dauern können.
        """,
            """
        At the bottom of the `Content` page you will find a form where you can enter your question or problem.

        Keep in mind that this tool is a hobby project of a father with a toddler and answers may take a few days.
        """,
        ),
        ("Was ist ein Konsent?", "What is a Consensus?"): (
            """
        Ein Konsent ist eine Einigung zwischen Beteiligten, bei der sich alle wohlfühlen.

        Nicht zu verwechseln mit einem Kompromiss, bei dem sich irgendwo in der Mitte getroffen.

        Ein Konsent ist also eine klare und eindeutige Zustimmung zu etwas.
        """,
            """
        A consensus is an agreement between those involved in which everyone feels comfortable.

        Not to be confused with a compromise, where they meet somewhere in the middle.

        A consensus is therefore a clear and unambiguous agreement on something.
        """,
        ),
        ("Was kann ich hier machen?", "What can I do here?"): (
            """
        Du kannst hier deine eigenen Grenzen für ein Rollenspiel festlegen und dokumentieren. Du kannst dazu `Consent Sheets` erstellen und pflegen.

        Diese Sheets kannst du entweder über einen Links teilen (öffentlich einsehbar) oder zu Gruppen zuordnen (nur für die Gruppe sichtbar).
        """,
            """
        You can define and document your own boundaries for a role play here. You can create and maintain `Consent Sheets` for this purpose.

        You can either share these sheets via a link (publicly visible) or assign them to groups (only visible to the group).
        """,
        ),
        ("Wie funktionieren Gruppen?", "How do groups work?"): (
            """
        Nachdem du dich angemeldet hast, kannst du Gruppen erstellen oder ihnen über einen Code beitreten.

        Gruppen, die du erstellst, verwaltest du, kannst also den Einladungscode sehen und erneuern oder Gruppenmitglieder entfernen.
        Außderm musst du einen `Consent Sheet` für die Gruppe erstellen. Du kannst deine Gruppen auch löschen.

        Gruppen, denen du begetreten bist, indem du den Einladungscode eingegeben hast, kannst du verlassen oder ihnen einen `Consent Sheet` zuweisen.

        In einer Gruppe wird automatisch der Konsent Aller gebildet und angezeigt.
        """,
            """
        Once you have logged in, you can create groups or join them using a code.

        You manage the groups you create, so you can view and renew the invitation code or remove group members.
        You must also create a 'Consent Sheet' for the group. You can also delete your groups.

        Groups that you have joined by entering the invitation code can be left or assigned a 'Consent Sheet'.

        The Consent Aller is automatically created and displayed in a group.
        """,
        ),
        ("Was ist ein Consent Sheet?", "What is a Consent Sheet"): (
            """
        Ein Consent Sheet ist eine Liste von Themen, die in einem Rollenspiel vorkommen können mit deinem Level des Wohlfühlens bei diesem Thema.

        Du kannst mehrere Sheets haben, z.B. für verschiedene Gruppen bzw. oder Öffentlichkeit.
        Versuch, es nicht zu übertreiben und nicht mehr als 10 Sheets zu haben. Gib den Sheets passende Namen, damit du sie wiederfindest.
        Da dieses Tool gratis ist, läuft es mit begrenzten Ressourcen, die Ich gerne fair verteilen nutzen möchte.
        Ich behalte mir vor, bei Missbrauch oder Überlastung, die Anzahl der Sheets zu limitieren und zu reduzieren.

        Wenn du einen Sheet öffentlich teilst, erhältst du einen Link und einen QR-Code, den du weitergeben kannst.
        Jeder mit diesem Link (erraten oder geteilt) kann deinen Sheet sehen, dabei werden weder dein Name, noch der Sheetname angezeigt.
        Die Kommentare sind jedoch sichtbar.
        """,
            """
        A Consent Sheet is a list of topics that can occur in a roleplay with your level of comfort with that topic.

        You can have multiple sheets, e.g. for different groups and/or publics.
        Try not to overdo it and have no more than 10 sheets. Give the sheets suitable names so that you can find them again.
        Since this tool is free, it runs on limited resources that I would like to share fairly.
        I may limit and reduce the number of sheets in case of abuse or overload.

        If you share a sheet publicly, you will receive a link and a QR code that you can pass on.
        Anyone with this link (guessed or shared) can see your sheet, but neither your name nor the sheet name will be displayed.
        However, the comments are visible.
        """,
        ),
        (
            "Eine Frage oder ein Problem, welches hier nicht beantwortet wird. Was kann ich tun?",
            "A question or problem that is not answered here. What can I do?",
        ): (
            """
        Gib deine Frage unten ein und klick auf `Abschicken`. Ich werde versuchen, dir so schnell wie möglich zu antworten. Und die Frage in die FAQ aufnehmen.

        Wenn du deine Emailadresse oder Discord-ID angibst, kann ich dir auch direkt antworten.
        """,
            """
        Enter your question below and click on 'Send'. I will try to answer you as soon as possible. And add the question to the FAQ.

        If you enter your e-mail address or Discord ID, I can also answer you directly.
        """,
        ),
        ("Welche Features sind geplant?", "What features are planned?"): (
            """
            * Gruppenerstellung mit vorhandenem Sheet
            * Login ohne SSO
            * Anonyme Public Sheets -> Sheet mit Passcode und ohne jegliche Kommentare
            * ausführliches Tutorial
            * Gruppen aus public Sheets
            """,
            """
            * Group creation with existing sheet
            * Login without SSO
            * Anonymous Public Sheets -> Sheet with Passcode and without any comments
            * detailed tutorial
            * Groups from public sheets
            """,
        ),
        (
            "Wie finde ich mit meiner Gruppe einen Konsent zu den Themen?",
            "How do I find a consensus with my group on the topics?",
        ): (
            """
Dafür ist die Gruppenfunktion gedacht, dazu gehst du/ihr wie folgt vor:
1. Alle melden sich hier an.
2. Du bist SL und erstellst eine Gruppe. Denk an einen passenden Namen, damit du und die Aanderen sie wiedererkennen.
3. Du gibst den Einladungs-Code an alle in deiner Gruppe weiter.
4. Die anderen geben den Code ein und treten der Gruppe bei.
5. Du erstellst den GM-Sheet für die Gruppe.
6. Alle Anderen füllen einen Sheet aus und weisen ihn der Gruppe zu.

Nun könnt ihr alle in der Gruppe den gebildeten Konsent sehen.
""",
            """
This is what the group function is for, here's how you/you proceed:
1. Everyone signs up here.
2. You are the GM and create a group. Think of a suitable name so that you and the others can recognize it.
3. You pass the invite-code on to everyone in your group.
4. The others enter the code and join the group.
5. You create the GM-Sheet for the group.
6. Everyone else fills out a sheet and assigns it to the group.

Now everyone in the group can see the consensus formed.
""",
        ),
    }
    with Session(engine) as session:
        session.exec(delete(FAQItem))
        session.commit()
        for question_de, question_en in faqs.keys():
            logging.debug(f"Question: {question_de[:20]}...")
            existing_question = session.exec(
                select(LocalizedText).where(
                    LocalizedText.text_de == question_de,
                    LocalizedText.text_en == question_en,
                )
            ).first()
            existing_answer = session.exec(
                select(LocalizedText).where(
                    LocalizedText.text_de == faqs[(question_de, question_en)][0],
                    LocalizedText.text_en == faqs[(question_de, question_en)][1],
                )
            ).first()

            local_question = existing_question or LocalizedText(
                text_en=question_en, text_de=question_de
            )
            local_answer = existing_answer or LocalizedText(
                text_en=faqs[(question_de, question_en)][1],
                text_de=faqs[(question_de, question_en)][0],
            )
            if local_question.id:
                session.merge(local_question)
                session.commit()
            else:
                session.add(local_question)
                session.commit()
                session.refresh(local_question)
            if local_answer.id:
                session.merge(local_answer)
                session.commit()
            else:
                session.add(local_answer)
                session.commit()
                session.refresh(local_answer)

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
