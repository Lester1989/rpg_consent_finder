from nicegui import ui, app
import logging
from models.db_models import (
    User,
)
from models.controller import get_user_from_storage
from localization.language_manager import get_localization, make_localisable


def reload_after(func, *args, **kwargs):
    func(*args, **kwargs)
    content.refresh()


@ui.refreshable
def content(lang: str = "en", **kwargs):
    user: User = get_user_from_storage()
    if not user:
        make_localisable(ui.label(), key="no_user", language=lang)
        return
    ui.notify(get_localization("welcome", lang), type="positive")
    logging.debug(user.nickname)
