from nicegui import ui
import logging
import pathlib
from services.session_service import session_storage


def load_news() -> list[tuple[str, dict[str, str]]]:
    files = pathlib.Path("src", "seeding", "news").glob("*.md")
    loaded = []
    for file in files:
        version = file.stem
        content = file.read_text(encoding="utf-8")
        de_md, en_md = content.split("---ENG---")
        loaded.append((version, {"de": de_md.strip(), "en": en_md.strip()}))
        logging.getLogger("content_consent_finder").debug(f"loaded news for {version}")
    return loaded


news: list[tuple[str, dict[str, str]]] = load_news()


def content(**kwargs):
    if not news:
        ui.markdown("No news available")
        return
    lang = session_storage.get("lang", "en")
    for news_point in sorted(news, key=lambda x: x[0], reverse=True):
        _, news_dict = news_point
        ui.markdown(news_dict[lang])
        ui.separator()
