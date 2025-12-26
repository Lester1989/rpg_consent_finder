from __future__ import annotations

import logging
from time import perf_counter
from typing import Any, Callable, Mapping, Tuple, TYPE_CHECKING

from a_logger_setup import LOGGER_NAME
from settings import Settings

if TYPE_CHECKING:  # pragma: no cover - import only for typing
    from opentelemetry.metrics import CallbackOptions, Observation
else:
    CallbackOptions = Any
    Observation = Any

LOGGER = logging.getLogger(LOGGER_NAME)
metrics_recorder: "MetricsRecorder | None" = None


class MetricsRecorder:
    """Recorder for core application metrics."""

    def __init__(
        self,
        *,
        request_counter,
        request_duration,
        active_requests,
        session_created,
        login_attempts,
        startup_duration,
    ) -> None:
        self._request_counter = request_counter
        self._request_duration = request_duration
        self._active_requests = active_requests
        self._session_created = session_created
        self._login_attempts = login_attempts
        self._startup_duration = startup_duration
        self._session_stats_provider: Callable[[], dict[str, int]] | None = None

    # ----- HTTP metrics -----
    def record_request(
        self, method: str, route: str, status_code: int, duration_ms: float
    ) -> None:
        attributes = {
            "http.method": method,
            "http.route": route,
            "http.status_code": status_code,
        }
        self._request_counter.add(1, attributes)
        self._request_duration.record(duration_ms, attributes)

    def middleware(self):
        async def _middleware(request, call_next):
            start = perf_counter()
            route = getattr(request.scope.get("route"), "path", request.url.path)
            attributes = {
                "http.method": request.method,
                "http.route": route,
            }
            self._active_requests.add(1, attributes)
            response = None
            try:
                response = await call_next(request)
                return response
            finally:
                duration_ms = (perf_counter() - start) * 1000
                status_code = getattr(response, "status_code", 500)
                self.record_request(request.method, route, status_code, duration_ms)
                self._active_requests.add(-1, attributes)

        return _middleware

    # ----- Session metrics -----
    def set_session_stats_provider(
        self, provider: Callable[[], dict[str, int]]
    ) -> None:
        self._session_stats_provider = provider

    def session_active_callback(self, _: CallbackOptions) -> list[Observation]:
        if not self._session_stats_provider:
            return []
        stats = self._session_stats_provider() or {}
        try:
            active = int(stats.get("active", 0))
        except (ValueError, TypeError):
            active = 0
        return [Observation(active, {})]

    def record_session_created(self) -> None:
        self._session_created.add(1)

    # ----- Authentication metrics -----
    def record_login_attempt(self, provider: str, status: str) -> None:
        self._login_attempts.add(1, {"provider": provider, "status": status})

    # ----- Startup metrics -----
    def record_startup_duration(self, duration_ms: float) -> None:
        self._startup_duration.record(duration_ms)


def get_metrics_recorder() -> MetricsRecorder | None:
    return metrics_recorder


def _headers_from_settings(headers: Tuple[Tuple[str, str], ...]) -> Mapping[str, str]:
    return {key: value for key, value in headers}


def setup_metrics(
    settings: Settings,
) -> MetricsRecorder | None:
    if not settings.otel_metrics_enabled:
        LOGGER.info("OpenTelemetry metrics disabled")
        return None

    try:
        from opentelemetry import metrics
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
            OTLPMetricExporter,
        )
        from opentelemetry.metrics import CallbackOptions, Observation
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.sdk.resources import Resource
    except ImportError:
        LOGGER.warning(
            "OpenTelemetry packages are missing; metrics will stay disabled. "
            "Run 'poetry install' or ensure opentelemetry-* dependencies are present."
        )
        return None

    if not settings.otel_exporter_endpoint:
        LOGGER.warning(
            "OpenTelemetry metrics enabled but OTEL_EXPORTER_OTLP_ENDPOINT is missing"
        )
        return None

    resource = Resource.create({"service.name": settings.otel_service_name})
    exporter = OTLPMetricExporter(
        endpoint=settings.otel_exporter_endpoint,
        headers=_headers_from_settings(settings.otel_exporter_headers),
    )

    metric_reader = PeriodicExportingMetricReader(
        exporter=exporter,
        export_interval_millis=settings.otel_metrics_export_interval_ms,
    )
    provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(provider)

    meter = metrics.get_meter(settings.otel_service_name)
    request_counter = meter.create_counter(
        name="http.server.request.count",
        description="Number of HTTP requests received.",
        unit="1",
    )
    request_duration = meter.create_histogram(
        name="http.server.request.duration",
        description="Duration of HTTP requests in milliseconds.",
        unit="ms",
    )
    active_requests = meter.create_up_down_counter(
        name="http.server.active_requests",
        description="In-flight HTTP requests.",
        unit="1",
    )
    session_created = meter.create_counter(
        name="session.created.count",
        description="Sessions created.",
        unit="1",
    )
    login_attempts = meter.create_counter(
        name="auth.login.attempts",
        description="Authentication attempts by provider and status.",
        unit="1",
    )
    startup_duration = meter.create_histogram(
        name="app.startup.duration",
        description="Application startup duration in milliseconds.",
        unit="ms",
    )

    recorder = MetricsRecorder(
        request_counter=request_counter,
        request_duration=request_duration,
        active_requests=active_requests,
        session_created=session_created,
        login_attempts=login_attempts,
        startup_duration=startup_duration,
    )

    meter.create_observable_gauge(
        name="session.active.count",
        description="Active sessions.",
        unit="1",
        callbacks=[recorder.session_active_callback],
    )

    LOGGER.info(
        "OpenTelemetry metrics configured: endpoint=%s, service.name=%s, interval_ms=%s",
        settings.otel_exporter_endpoint,
        settings.otel_service_name,
        settings.otel_metrics_export_interval_ms,
    )

    global metrics_recorder
    metrics_recorder = recorder

    return recorder
