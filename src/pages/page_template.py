from nicegui import ui, app

from models.db_models import (
    User,
)
from models.controller import get_user_by_id_name


def reload_after(func, *args, **kwargs):
    func(*args, **kwargs)
    content.refresh()


@ui.refreshable
def content(**kwargs):
    user: User = get_user_by_id_name(app.storage.user.get("user_id"))
    if not user:
        ui.label("No user found")
        return
    ui.label(user.nickname)
