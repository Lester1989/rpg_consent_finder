from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Tuple


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    google_client_id: str = "..."
    google_client_secret: str = "..."
    discord_client_id: str = "..."
    discord_client_secret: str = "..."
    port: int = 8080
    base_url_env: str | None = None
    seed_on_startup: bool = False
    reload: bool = False
    admins: Tuple[str, ...] = ()
    db_connection_string: str = "-default-"
    log_level: str = "DEBUG"
    storage_secret: str | None = None
    discord_allow_insecure_http: bool = True

    @property
    def base_url(self) -> str:
        return self.base_url_env or f"http://localhost:{self.port}"


@lru_cache()
def get_settings() -> Settings:
    admins = tuple(
        admin.strip() for admin in os.getenv("ADMINS", "").split(",") if admin.strip()
    )
    return Settings(
        google_client_id=os.getenv("GOOGLE_CLIENT_ID", "...") or "...",
        google_client_secret=os.getenv("GOOGLE_CLIENT_SECRET", "...") or "...",
        discord_client_id=os.getenv("DISCORD_CLIENT_ID", "...") or "...",
        discord_client_secret=os.getenv("DISCORD_CLIENT_SECRET", "...") or "...",
        port=int(os.getenv("PORT", "8080")),
        base_url_env=os.getenv("BASE_URL"),
        seed_on_startup=_to_bool(os.getenv("SEED_ON_STARTUP"), False),
        reload=_to_bool(os.getenv("RELOAD"), False),
        admins=admins,
        db_connection_string=os.getenv("DB_CONNECTION_STRING", "-default-"),
        log_level=os.getenv("LOGLEVEL", "DEBUG"),
        storage_secret=os.getenv("STORAGE_SECRET"),
        discord_allow_insecure_http=_to_bool(
            os.getenv("DISCORD_ALLOW_INSECURE_HTTP"), True
        ),
    )
