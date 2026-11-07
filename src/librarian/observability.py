"""Traces (OpenTelemetry) and errors (Sentry), both off until configured by environment.

A leaf module like `config` and `log_config`: api, mcp, agent and retrieval may all import it.

Nothing here costs anything when unset. `span()` is a no-op context manager until
`configure_tracing()` has built a provider, and that happens only when
`OTEL_EXPORTER_OTLP_ENDPOINT` is set (or a test passes an exporter). OpenTelemetry and Sentry
are imported lazily, inside the setup functions, so a base install without the `observability`
extra never imports either.

Environment (standard OTel names, no vendor-specific ones):

    OTEL_EXPORTER_OTLP_ENDPOINT   e.g. https://cloud.langfuse.com/api/public/otel
    OTEL_EXPORTER_OTLP_HEADERS    e.g. Authorization=Basic <base64(pk-lf-...:sk-lf-...)>,
                                  x-langfuse-ingestion-version=4
    LIBRARIAN_EXPERIMENT          value of the `experiment` attribute (default empty)
    LIBRARIAN_TRACE_CONTENT       1 to put the query and answer text on `agent.turn` (default off)
    SENTRY_DSN                    enables Sentry; SENTRY_ENVIRONMENT optionally names the env
    LIBRARIAN_RELEASE             the `release` on logs, spans and Sentry events

Span attributes use the GenAI semantic conventions (`gen_ai.*`) where one exists, which is what
Langfuse maps to model, token usage and cost. Every span carries `release` (and
`langfuse.release`) and `experiment`. No prompt or answer text is recorded unless
`LIBRARIAN_TRACE_CONTENT` is set.
"""

from __future__ import annotations

import os
import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

from librarian.config import get_release
from librarian.log_config import get_logger

if TYPE_CHECKING:
    from fastapi import FastAPI

log = get_logger(__name__)

_tracer: Any = None
_provider: Any = None


class NoopSpan:
    """Stands in for a span when tracing is off."""

    def set_attribute(self, key: str, value: object) -> None:
        return None

    def set_attributes(self, attributes: dict[str, object]) -> None:
        return None

    def record_exception(self, exc: BaseException) -> None:
        return None

    def end(self) -> None:
        return None

    def is_recording(self) -> bool:
        return False


_NOOP = NoopSpan()


def end_span(s: Any) -> None:  # noqa: ANN401
    """End a `start_span` span once; safe on a no-op span and on one already ended."""
    if s.is_recording():
        s.end()


def experiment() -> str:
    return os.environ.get("LIBRARIAN_EXPERIMENT", "").strip()


def trace_content_enabled() -> bool:
    return os.environ.get("LIBRARIAN_TRACE_CONTENT", "").strip().lower() in {"1", "true", "yes"}


def tracing_enabled() -> bool:
    return _tracer is not None


def configure_tracing(*, exporter: object | None = None) -> bool:
    """Build the tracer provider if configured; True when tracing is on.

    `exporter` is for tests (an in-memory exporter, flushed synchronously). Otherwise the OTLP
    HTTP exporter is built only when `OTEL_EXPORTER_OTLP_ENDPOINT` is set, and it reads that
    variable and `OTEL_EXPORTER_OTLP_HEADERS` itself. Without the optional packages this logs
    once and stays off.
    """
    global _tracer, _provider
    if _tracer is not None:
        return True
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
    if exporter is None and not endpoint:
        return False
    try:
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import SpanProcessor, TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
    except ImportError:
        log.warning("observability.tracing.unavailable", hint="uv sync --extra observability")
        return False

    release = get_release()

    class _StampProcessor(SpanProcessor):
        """Gives every span, ours or the FastAPI instrumentation's, release and experiment."""

        def on_start(self, span: Any, parent_context: object = None) -> None:  # noqa: ANN401
            span.set_attribute("release", release)
            span.set_attribute("langfuse.release", release)
            span.set_attribute("experiment", experiment())

    provider = TracerProvider(
        resource=Resource.create({"service.name": "librarian", "service.version": release})
    )
    provider.add_span_processor(_StampProcessor())
    if exporter is not None:
        provider.add_span_processor(SimpleSpanProcessor(exporter))  # type: ignore[arg-type]
    else:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(timeout=10)))
    _provider = provider
    _tracer = provider.get_tracer("librarian", release)
    log.info("observability.tracing.on", release=release)
    return True


def shutdown_tracing() -> None:
    """Flush and drop the provider (tests, and process exit)."""
    global _tracer, _provider
    if _provider is not None:
        _provider.shutdown()
    _tracer = _provider = None


def _parent_context(parent: object) -> Any:  # noqa: ANN401
    """OTel context holding `parent`, or None (use the current context)."""
    if parent is None or isinstance(parent, NoopSpan):
        return None
    from opentelemetry import trace

    return trace.set_span_in_context(parent)  # type: ignore[arg-type]


@contextmanager
def span(name: str, *, parent: object = None, **attributes: object) -> Iterator[Any]:
    """Open a span named `name` with `attributes`; a no-op when tracing is off.

    Records exceptions on the span and re-raises. `None` attribute values are skipped. `parent`
    is a span from `start_span` to nest under (otherwise the current span).
    """
    if _tracer is None:
        yield _NOOP
        return
    with _tracer.start_as_current_span(
        name, context=_parent_context(parent), record_exception=True
    ) as s:
        for key, value in attributes.items():
            if value is not None:
                s.set_attribute(key, value)
        yield s


def start_span(name: str, *, parent: object = None, **attributes: object) -> Any:  # noqa: ANN401
    """Start a span that is not made current; the caller must `end()` it.

    For spans that stay open across a `yield` in an async generator, where attaching a context
    would detach in a different one. Children name it as their `parent`.
    """
    if _tracer is None:
        return _NOOP
    s = _tracer.start_span(name, context=_parent_context(parent))
    for key, value in attributes.items():
        if value is not None:
            s.set_attribute(key, value)
    return s


@contextmanager
def timed(name: str, **attributes: object) -> Iterator[Any]:
    """`span()` that also sets `latency_ms` on exit."""
    started = time.monotonic()
    with span(name, **attributes) as s:
        try:
            yield s
        finally:
            s.set_attribute("latency_ms", round((time.monotonic() - started) * 1000))


def instrument_fastapi(app: FastAPI) -> None:
    """Automatic server spans for every route, when tracing is on and the package is present."""
    if _provider is None:
        return
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    except ImportError:
        log.warning("observability.fastapi.unavailable", hint="uv sync --extra observability")
        return
    FastAPIInstrumentor.instrument_app(
        app, tracer_provider=_provider, excluded_urls="healthz,readyz"
    )


def _scrub_event(event: dict[str, Any], _hint: object) -> dict[str, Any]:
    """Sentry before_send: drop credential headers and cookies."""
    request = event.get("request")
    if isinstance(request, dict):
        headers = request.get("headers")
        if isinstance(headers, dict):
            for key in list(headers):
                if key.lower() in {"authorization", "cookie", "x-api-key"}:
                    headers[key] = "[Filtered]"
        request.pop("cookies", None)
    return event


def init_sentry() -> bool:
    """Start Sentry when `SENTRY_DSN` is set; True when it was started."""
    dsn = os.environ.get("SENTRY_DSN", "").strip()
    if not dsn:
        return False
    try:
        import sentry_sdk
    except ImportError:
        log.warning("observability.sentry.unavailable", hint="uv sync --extra observability")
        return False
    sentry_sdk.init(
        dsn=dsn,
        release=get_release(),
        environment=os.environ.get("SENTRY_ENVIRONMENT") or None,
        send_default_pii=False,
        traces_sample_rate=0.0,  # traces go through OTel, not Sentry
        before_send=_scrub_event,  # type: ignore[arg-type]
    )
    log.info("observability.sentry.on", release=get_release())
    return True


def setup(app: FastAPI | None = None) -> None:
    """Called once at process start: Sentry, then tracing, then the FastAPI instrumentation."""
    init_sentry()
    if configure_tracing() and app is not None:
        instrument_fastapi(app)
