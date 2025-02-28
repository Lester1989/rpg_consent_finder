import pathlib

# md_text = pathlib.Path("playfun_explanation_en.md").read_text(encoding="utf-8")
# print(repr(md_text))

raw = {
    "challenge": {
        1: [
            ("Das kurz-vor-knapp-Gewinnen", "Winning just in time"),
            (
                "Das Gewinnen nachdem zuvor ein herber Rückschlag erlitten wurde",
                "Winning after a severe setback",
            ),
            ("Strategieplanung", "Strategy planning"),
            ("Min-Maxen von Charakteren", "Min-maxing characters"),
        ],
        -1: [
            (
                "Verlieren = Erfolg ist mit einem Nachteil",
                "Losing = success that comes with a disadvantage",
            ),
            ("Zu leichte Herausforderungen", "Too easy challenges"),
            ("Zu wenig (Wett-)Kämpfe", "Too few (combat) fights"),
            ("Narrative / World Building RPG", "Narrative / World Building RPG"),
        ],
    },
    "discovery": {
        1: [
            (
                "Entdecken von neuen Dingen, Orten, NPC, etc.",
                "Discovering new things, places, NPCs, etc.",
            ),
            (
                "Finden von Informationen in der Hintergrundsgeschichte der Welt(en)",
                "Finding information in the background story of the world(s)",
            ),
            (
                "Ausfüllen von grauen Flecken auf einer Karte",
                "Filling in grey spots on a map",
            ),
        ],
        -1: [
            ("Das Verharren an einem Ort", "Staying in one place"),
            (
                "Stark eingegrenzte Handlungen (wenig Orte, Personen und Geschehnisse)",
                "Strongly limited actions (few places, people and events)",
            ),
        ],
    },
    "expression": {
        1: [
            (
                "Ausspielen von Teilen und /oder Gegenteilen von einem Selbst",
                "Playing out parts and / or opposites of oneself",
            ),
            (
                "Ausspielen von Aspekten die im Realen Leben nicht gelebt werden können",
                "Playing out aspects that cannot be lived in real life",
            ),
        ],
        -1: [
            (
                "Wenn das Ausspielen von Aspekten verhindert wird",
                "Playing aspects is prevented",
            ),
            (
                "Das Spielen von vorgefertigten, ausgearbeiteten Charakteren",
                "Playing pre-made, elaborated characters",
            ),
            (
                "Das Spielen von reinen Dungeon-Crawl-Charakteren",
                "Playing pure dungeon crawl characters",
            ),
        ],
    },
    "fantasy": {
        1: [
            (
                "Das Kennen der Welt und deren Geschichte",
                "Knowing the world and its history",
            ),
            (
                "Anekdoten erzählen zu Orten, Personen, Geschehnissen, Objekten",
                "Telling anecdotes about places, people, events, objects",
            ),
            (
                "Das Genießen von stimmungsvollen Szenen mit (N)PC",
                "Enjoying atmospheric scenes with (N)PC",
            ),
        ],
        -1: [
            ("Generische Beschreibungen", "Generic descriptions"),
            ("Flache unausgearbeitet Welten", "Flat undeveloped worlds"),
            (
                "Fehlen von Settings-Bücher, Kurzgeschichten oder Roman",
                "Lack of setting books, short stories or novels",
            ),
        ],
    },
    "fellowship": {
        1: [
            (
                "Das Spielen in der Gruppe ist wichtiger als das, was gespielt wird",
                "Playing in the group is more important than what is played",
            ),
            ("Ich schließe mich der Mehrheit an", "I join the majority"),
        ],
        -1: [
            ("Spieler gegen Spieler-Situationen", "Player vs. player situations"),
            (
                "Wenn keine gute Gruppendynamik aufkommt",
                "If no good group dynamics arise",
            ),
            (
                "Ausscheiden von Charakteren durch Tod oder ähnlichem",
                "Characters dropping out due to death or similar",
            ),
        ],
    },
    "narrative": {
        1: [
            (
                "Vollständiges Durchlaufen des ersten, zweiten und dritten Aktes",
                "Complete run through the first, second and third act",
            ),
            (
                "Spielen von Episoden anstelle von Staffeln",
                "Playing episodes instead of seasons",
            ),
            ("Abschluss des Spannungsbogens", "Completion of the suspense arc"),
        ],
        -1: [
            ("Steckenbleiben im 2. Akt", "Stuck in the 2nd act"),
            ("1. und 3. Akt kommen zu kurz", "1st and 3rd act are too short"),
            ("Die Geschichten zieht sich EWIG hin", "The stories drag on FOREVER"),
        ],
    },
    "sensation": {
        1: [
            ("Das Gefühl beim Würfeln", "The feeling when rolling the dice"),
            ("Abgestimmte Musik", "Coordinated music"),
            ("Stimmungsvolles Licht", "Atmospheric light"),
            (
                "Verwendung von Miniaturen / digitalen Tokens",
                "Use of miniatures / digital tokens",
            ),
            ("Reden mit verstellter Stimme", "Talking with a disguised voice"),
        ],
        -1: [
            ("Das Würfeln mit einer App", "Rolling dice with an app"),
            (
                "Das Aufschreiben am Computer anstelle mit Stift und Papier",
                "Writing on the computer instead of with pen and paper",
            ),
            (
                "Ruhige Umgebung / nicht abgestimmte Musik",
                "Quiet environment / uncoordinated music",
            ),
        ],
    },
    "submission": {
        1: [
            ("Sich berieseln lassen", "Letting yourself be entertained"),
            ("Passives Dabei sein", "Passive participation"),
            (
                "Keine großen Leistungen erbringen müssen",
                "Not having to perform great feats",
            ),
        ],
        -1: [
            ("Aktives Zuhören und Mitmachen", "Active listening and participating"),
            ("Eigeninitiative", "Own initiative"),
            ("Kreativität", "Creativity"),
        ],
    },
}


for play_style, values in raw.items():
    file = pathlib.Path("src", "seeding", "playfun", f"{play_style}.md")
    text = f"# {play_style}\n"
    for weight, statements_de_en in values.items():
        text += (f"## {weight}") + "\n"
        for de, en in statements_de_en:
            text += (f"- {de}") + "\n"
        text += "\n"
    text += ("---ENG---\n") + "\n"
    for weight, statements_de_en in values.items():
        text += (f"## {weight}") + "\n"
        for de, en in statements_de_en:
            text += (f"- {en}") + "\n"
        text += "\n"
    file.write_text(text, encoding="utf-8")
