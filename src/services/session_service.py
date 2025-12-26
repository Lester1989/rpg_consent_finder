from __future__ import annotations

from collections.abc import Callable, Iterable, MutableMapping
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from datetime import timezone
from secrets import token_urlsafe
from typing import Any

from telemetry import get_metrics_recorder

from fastapi import Request
from nicegui import app, ui
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from settings import get_settings

SESSION_COOKIE_NAME = "rpg_session"
SESSION_TTL = timedelta(days=7)
LOGGER = logging.getLogger(__name__)

_current_session: ContextVar["SessionData | None"] = ContextVar(
    "current_session", default=None
)


_session_listeners: list[Callable[[SessionData], None]] = []
try:
    _metrics_recorder = get_metrics_recorder()
except Exception:
    _metrics_recorder = None
    LOGGER.warning("Failed to initialize metrics recorder", exc_info=True)


def register_session_listener(callback: Callable[[SessionData], None]) -> None:
    _session_listeners.append(callback)


def set_metrics_recorder(recorder) -> None:
    global _metrics_recorder
    _metrics_recorder = recorder


def _notify_listeners(session: SessionData) -> None:
    for listener in _session_listeners:
        try:
            listener(session)
        except Exception:
            LOGGER.exception("Error in session listener")


@dataclass
class SessionData:
    token: str
    user_id: str | None = None
    data: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    dirty: bool = False
    rotate: bool = False
    previous_token: str | None = None

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)


class SessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionData] = {}

    def _generate_token(self) -> str:
        return token_urlsafe(32)

    def _create_session(self) -> SessionData:
        session = SessionData(token=self._generate_token())
        self._sessions[session.token] = session
        return session

    def get(self, token: str | None) -> SessionData | None:
        return self._sessions.get(token) if token else None

    def ensure(self, token: str | None) -> tuple[SessionData, bool]:
        session = self.get(token)
        if session is None:
            LOGGER.debug("SessionManager.ensure: creating session for token %s", token)
            session = self._create_session()
            if _metrics_recorder:
                _metrics_recorder.record_session_created()
            return session, True
        session.touch()
        if session.previous_token:
            old_token = session.previous_token
            if token == old_token:
                # Keep the old token mapping active so late requests still resolve
                session.previous_token = None
        return session, False

    def rotate_token(self, session: SessionData) -> None:
        old_token = session.token
        session.token = self._generate_token()
        session.previous_token = old_token
        self._sessions[session.token] = session
        self._sessions[old_token] = session
        session.dirty = True
        session.rotate = False

    def write_cookie(self, response: Response, session: SessionData) -> None:
        settings = get_settings()
        secure_cookie = settings.base_url.startswith("https://")
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=session.token,
            max_age=int(SESSION_TTL.total_seconds()),
            httponly=True,
            secure=secure_cookie,
            samesite="lax",
            path="/",
        )
        session.dirty = False

    def delete_cookie(self, response: Response) -> None:
        response.delete_cookie(SESSION_COOKIE_NAME, path="/")


session_manager = SessionManager()


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        existing_token = request.cookies.get(SESSION_COOKIE_NAME)
        session, created = session_manager.ensure(existing_token)
        request.state.session = session
        LOGGER.debug(
            "SessionMiddleware dispatch token=%s created=%s user_id=%s",
            existing_token,
            created,
            session.user_id,
        )
        token = _current_session.set(session)
        try:
            response = await call_next(request)
        finally:
            _current_session.reset(token)
        if session.rotate:
            LOGGER.debug("rotating session user_id=%s", session.user_id)
            session_manager.rotate_token(session)
        if created or session.dirty:
            LOGGER.debug(
                "writing cookie token=%s rotate=%s dirty=%s",
                session.token,
                session.rotate,
                session.dirty,
            )
            session_manager.write_cookie(response, session)
        return response


class SessionStorage(MutableMapping[str, Any]):
    def _current(self) -> SessionData | None:
        return _resolve_session()

    def _require_session(self) -> SessionData:
        session = self._current()
        if session is None:
            raise RuntimeError("session storage accessed outside of request context")
        return session

    def __getitem__(self, key: str) -> Any:
        session = self._require_session()
        if key == "user_id":
            if session.user_id is None:
                raise KeyError(key)
            return session.user_id
        return session.data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        session = self._require_session()
        if key == "user_id":
            session.user_id = value
            session.dirty = True
        else:
            session.data[key] = value
            session.dirty = True
        session.touch()
        _notify_listeners(session)

    def __delitem__(self, key: str) -> None:
        session = self._require_session()
        if key == "user_id":
            session.user_id = None
            session.dirty = True
        else:
            if key in session.data:
                del session.data[key]
                session.dirty = True
            else:
                raise KeyError(key)
        session.touch()
        _notify_listeners(session)

    def __iter__(self) -> Iterable[str]:
        session = self._current()
        if session is None:
            return
        if session.user_id is not None:
            yield "user_id"
        yield from session.data.keys()

    def __len__(self) -> int:
        session = self._current()
        if session is None:
            return 0
        return len(session.data) + (1 if session.user_id is not None else 0)

    def get(self, key: str, default: Any | None = None) -> Any | None:
        session = self._current()
        if session is None:
            return default
        if key == "user_id":
            return session.user_id if session.user_id is not None else default
        return session.data.get(key, default)

    def clear(self) -> None:  # type: ignore[override]
        session = self._current()
        if session is None:
            return
        session.data.clear()
        session.user_id = None
        session.dirty = True
        session.touch()
        _notify_listeners(session)


session_storage: MutableMapping[str, Any] = SessionStorage()


def ensure_session_middleware() -> None:
    LOGGER.debug(
        "ensure_session_middleware called app_id=%s middleware=%s",
        id(app),
        getattr(app, "user_middleware", None),
    )
    for middleware in getattr(app, "user_middleware", []):
        if getattr(middleware, "cls", None) is SessionMiddleware:
            return
    LOGGER.debug("installing session middleware on app id=%s", id(app))
    app.add_middleware(SessionMiddleware)


def get_session_stats() -> dict[str, int]:
    unique_sessions = len(
        {id(session) for session in session_manager._sessions.values()}
    )
    return {"active": unique_sessions}


def _resolve_session() -> SessionData | None:
    ensure_session_middleware()
    session = _current_session.get()
    if session is not None:
        return session
    client = getattr(ui.context, "client", None)
    if client is None:
        return None
    request = getattr(client, "request", None)
    if request is None:
        return None
    shared = getattr(client, "shared", None)
    session = getattr(request.state, "session", None)
    if session is not None:
        if shared is not None:
            shared[SESSION_COOKIE_NAME] = session.token
            if session.user_id is not None:
                shared["user_id"] = session.user_id
            elif "user_id" in shared:
                shared.pop("user_id", None)
        return session
    token = None
    try:
        token = request.cookies.get(SESSION_COOKIE_NAME)
    except AttributeError:
        token = None
    if not token and shared is not None:
        token = shared.get(SESSION_COOKIE_NAME)
    session, created = session_manager.ensure(token)
    request.state.session = session
    if shared is not None:
        shared[SESSION_COOKIE_NAME] = session.token
        if session.user_id is None and "user_id" in shared:
            session.user_id = shared["user_id"]
            session.dirty = True
        elif session.user_id is not None:
            shared["user_id"] = session.user_id
    if created:
        session.dirty = True
        LOGGER.debug("created session during resolve: token=%s", session.token)
    else:
        LOGGER.debug(
            "resolved existing session: token=%s user_id=%s",
            session.token,
            session.user_id,
        )
    return session


def get_current_session() -> SessionData:
    session = _resolve_session()
    if session is None:
        raise RuntimeError("session not available in current context")
    return session


def get_current_user_id() -> str | None:
    return get_current_session().user_id


def begin_user_session(user_id: str) -> None:
    session = get_current_session()
    session.user_id = user_id
    session.rotate = True
    session.dirty = True
    client = getattr(ui.context, "client", None)
    shared = getattr(client, "shared", None)
    if shared is not None:
        shared["user_id"] = user_id
    LOGGER.info(
        "begin_user_session token=%s previous=%s user_id=%s",
        session.token,
        session.previous_token,
        session.user_id,
    )
    session.touch()
    _notify_listeners(session)


def end_user_session() -> None:
    session = get_current_session()
    session.user_id = None
    session.data.clear()
    session.rotate = True
    session.dirty = True
    client = getattr(ui.context, "client", None)
    shared = getattr(client, "shared", None)
    if shared is not None:
        shared.pop("user_id", None)
    session.touch()
    _notify_listeners(session)


def require_user_id() -> str:
    user_id = get_current_user_id()
    if user_id is None:
        raise RuntimeError("user session not initialised")
    return user_id


def get_request() -> Request:
    client = getattr(ui.context, "client", None)
    if client is None:
        raise RuntimeError("no active client")
    return client.request  # type: ignore[return-value]
