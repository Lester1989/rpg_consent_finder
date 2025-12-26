from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Tuple


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_headers(value: str | None) -> Tuple[Tuple[str, str], ...]:
    if not value:
        return ()
    parsed: list[Tuple[str, str]] = []
    for pair in value.split(","):
        key, _, val = pair.partition("=")
        if key.strip() and val:
            parsed.append((key.strip(), val.strip()))
    return tuple(parsed)


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
    otel_metrics_enabled: bool = False
    otel_exporter_endpoint: str | None = None
    otel_exporter_headers: Tuple[Tuple[str, str], ...] = ()
    otel_service_name: str = "rpg_consent_finder"
    otel_metrics_export_interval_ms: int = 60000

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
        otel_metrics_enabled=_to_bool(os.getenv("OTEL_METRICS_ENABLED"), False),
        otel_exporter_endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
        otel_exporter_headers=_parse_headers(os.getenv("OTEL_EXPORTER_OTLP_HEADERS")),
        otel_service_name=os.getenv("OTEL_SERVICE_NAME", "rpg_consent_finder"),
        otel_metrics_export_interval_ms=int(
            os.getenv("OTEL_METRICS_EXPORT_INTERVAL_MS", "60000")
        ),
    )
