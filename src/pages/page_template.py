from nicegui import ui, app

from models.db_models import (
    User,
)
from models.controller import get_user_by_id_name
from localization.language_manager import get_localization, make_localisable


def reload_after(func, *args, **kwargs):
    func(*args, **kwargs)
    content.refresh()


@ui.refreshable
def content(lang: str = "en", **kwargs):
    user: User = get_user_by_id_name(app.storage.user.get("user_id"))
    if not user:
        make_localisable(ui.label(), key="no_user", language=lang)
        return
    ui.notify(get_localization("welcome", lang), type="positive")
    ui.label(user.nickname)
