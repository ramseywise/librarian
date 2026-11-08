"""Prometheus metrics: `GET /metrics`, request and chat timing, and scrape-time gauges.

Off unless `LIBRARIAN_METRICS_TOKEN` is set: the route then answers 404 and the middleware passes
requests through untimed. On, `/metrics` needs `Authorization: Bearer <token>` (it is a plain
Starlette route, outside the app-wide `current_user` dependency, like `/readyz`; Caddy also refuses
it from outside, docker/Caddyfile).

With `librarian api --workers N` (N > 1) each worker is a process, and one scrape reaches only one
of them. `prom_env.prepare` then sets PROMETHEUS_MULTIPROC_DIR before the workers start, every
counter and histogram is written to files in it, and a scrape sums them (MultiProcessCollector).
Gauges are not stored per process: they are computed from shared state at scrape time by
`_LiveCollector`, so they need no multiprocess mode and no cleanup of dead workers.

Labels are bounded: the route is the matched template (`/api/courses/lessons/{lesson_id:path}`),
never the raw path, and anything unmatched is `other`.
"""

from __future__ import annotations

import os
import shutil
import time
from collections.abc import Callable, Iterable
from typing import Any

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
    multiprocess,
)
from prometheus_client.core import GaugeMetricFamily, Metric
from prometheus_client.registry import Collector
from sqlalchemy.exc import SQLAlchemyError
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from librarian import release as content_release
from librarian import spend
from librarian.api import prom_env
from librarian.api.security import token_matches
from librarian.config import get_release, get_settings
from librarian.db import get_engine
from librarian.log_config import get_logger

log = get_logger(__name__)

METRICS_PATH = "/metrics"

# Seconds. 0.5 and 4 are the SLO thresholds, so each is a bucket edge and the "good request"
# ratio is exact, not interpolated.
_LATENCY_BUCKETS = (0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 4.0, 10.0, 30.0, 120.0)
_FIRST_TOKEN_BUCKETS = (0.25, 0.5, 1.0, 2.0, 3.0, 4.0, 6.0, 10.0, 20.0, 60.0)

HTTP_LATENCY = Histogram(
    "librarian_http_request_duration_seconds",
    "HTTP request time to the last byte, by method and route template.",
    ["method", "route"],
    buckets=_LATENCY_BUCKETS,
)
HTTP_REQUESTS = Counter(
    "librarian_http_requests",
    "HTTP requests by method, route template and status code.",
    ["method", "route", "status"],
)
SEARCH_LATENCY = Histogram(
    "librarian_search_duration_seconds",
    "Search requests (lesson search and the search_wiki tool): the search latency SLO.",
    buckets=_LATENCY_BUCKETS,
)
CHAT_FIRST_TOKEN = Histogram(
    "librarian_chat_first_token_seconds",
    "Seconds from the chat request arriving to the first `token` event: the chat latency SLO.",
    buckets=_FIRST_TOKEN_BUCKETS,
)
CHAT_STREAMS = Counter(
    "librarian_chat_streams",
    "Chat streams that ended, by outcome: `token` (an answer began) or `no_token`.",
    ["outcome"],
)

# Routes that make up the search SLO. The tool route is one template for every MCP tool, so it
# counts only when the tool is the wiki search.
_SEARCH_ROUTES = frozenset({"/api/courses/search"})
_TOOL_ROUTE = "/api/tools/{name}"
_SEARCH_TOOL = "search_wiki"

_readiness: Callable[[], bool] | None = None


def set_readiness(fn: Callable[[], bool]) -> None:
    """The function behind `librarian_ready` (the same checks as /readyz)."""
    global _readiness
    _readiness = fn


def enabled() -> bool:
    return bool(get_settings().metrics_token)


def _route_label(scope: Scope) -> str:
    route = scope.get("route")
    path = getattr(route, "path", None)
    return path if isinstance(path, str) and path else "other"


def _is_search(scope: Scope, route: str) -> bool:
    if route in _SEARCH_ROUTES:
        return True
    return route == _TOOL_ROUTE and scope.get("path_params", {}).get("name") == _SEARCH_TOOL


class MetricsMiddleware:
    """Times every HTTP request to its last byte and counts it by status.

    A response that never started (the client left, an exception) counts as 500, the same rule
    as the request log. `/metrics` itself is not counted.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["path"] == METRICS_PATH or not enabled():
            await self.app(scope, receive, send)
            return
        started = time.perf_counter()
        status = 500

        async def send_wrapper(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            elapsed = time.perf_counter() - started
            route = _route_label(scope)  # set by the router while the app ran
            method = scope["method"]
            HTTP_LATENCY.labels(method, route).observe(elapsed)
            HTTP_REQUESTS.labels(method, route, str(status)).inc()
            if status < 500 and _is_search(scope, route):
                SEARCH_LATENCY.observe(elapsed)


def observe_first_token(started: float) -> None:
    """Record the first-token latency of one chat stream (`started` is a perf_counter value)."""
    if enabled():
        CHAT_FIRST_TOKEN.observe(time.perf_counter() - started)
        CHAT_STREAMS.labels("token").inc()


def note_no_token() -> None:
    if enabled():
        CHAT_STREAMS.labels("no_token").inc()


class _LiveCollector(Collector):
    """Gauges read at scrape time from state every worker shares."""

    def collect(self) -> Iterable[Metric]:
        settings = get_settings()
        ready = GaugeMetricFamily("librarian_ready", "1 when /readyz would answer 200.")
        try:
            ready.add_metric([], 1.0 if _readiness is None or _readiness() else 0.0)
        except Exception as e:  # a probe must not break the scrape
            log.warning("metrics.readiness_failed", error=str(e))
            ready.add_metric([], 0.0)
        yield ready

        info = GaugeMetricFamily(
            "librarian_release_info",
            "Always 1; the labels name the image and content release.",
            labels=["release", "content"],
        )
        info.add_metric([get_release(), content_release.current_name() or ""], 1.0)
        yield info

        yield from self._spend(settings)
        yield from self._disk(settings)

    @staticmethod
    def _spend(settings: Any) -> Iterable[Metric]:  # noqa: ANN401 - Settings
        try:
            tot = spend.totals(get_engine())
        except SQLAlchemyError as e:
            log.warning("metrics.spend_failed", error=str(e))
            return
        used = GaugeMetricFamily(
            "librarian_chat_spend_usd", "Estimated chat spend in USD, all users.", labels=["window"]
        )
        used.add_metric(["today"], tot.today_usd)
        used.add_metric(["30d"], tot.last_30d_usd)
        yield used
        cap = GaugeMetricFamily(
            "librarian_chat_spend_cap_usd",
            "Configured daily chat spend caps in USD; 0 means no cap.",
            labels=["scope"],
        )
        cap.add_metric(["global_daily"], settings.chat_daily_budget_usd)
        cap.add_metric(["user_daily"], settings.chat_user_daily_budget_usd)
        yield cap

    @staticmethod
    def _disk(settings: Any) -> Iterable[Metric]:  # noqa: ANN401 - Settings
        path = settings.var_dir
        while not path.exists() and path != path.parent:
            path = path.parent
        try:
            usage = shutil.disk_usage(path)
        except OSError as e:
            log.warning("metrics.disk_failed", error=str(e))
            return
        free = GaugeMetricFamily(
            "librarian_state_disk_free_ratio", "Free fraction of the disk holding var/ (state)."
        )
        free.add_metric([], usage.free / usage.total if usage.total else 0.0)
        yield free
        free_b = GaugeMetricFamily(
            "librarian_state_disk_free_bytes", "Free bytes on the disk holding var/ (state)."
        )
        free_b.add_metric([], float(usage.free))
        yield free_b


_live = _LiveCollector()
REGISTRY.register(_live)


def render() -> bytes:
    """The exposition text: summed across workers in multiprocess mode, else this process."""
    if os.environ.get(prom_env.ENV_VAR):
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        registry.register(_live)
        return generate_latest(registry)
    return generate_latest(REGISTRY)


def metrics_endpoint(request: Request) -> Response:
    """GET /metrics: 404 when no token is configured, 401 on a wrong one."""
    token = get_settings().metrics_token
    if not token:
        return PlainTextResponse("Not Found", status_code=404)
    header = request.headers.get("authorization", "")
    scheme, _, supplied = header.partition(" ")
    if scheme.lower() != "bearer" or not token_matches(supplied.strip() or None, token):
        return PlainTextResponse(
            "Missing or invalid metrics token.",
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Response(render(), media_type=CONTENT_TYPE_LATEST)
