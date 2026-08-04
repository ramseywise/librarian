"""Shared structlog configuration with secret redaction.

Named log_config, not logging: `make api` runs uvicorn with cwd=app/, which puts
this directory on sys.path and would make a module named `logging` shadow the
stdlib for every dependency (structlog imports it and breaks).

Enforces the Buyi invariant "Secrets never committed, never logged" — the logging
clause, which previously held by convention only with no filter behind it.

Usage (per ~/.claude/refs/logging.md):

    from shared.log_config import get_logger, configure_logging

    configure_logging()                  # once, at entry point
    log = get_logger(__name__)           # module level
"""

from __future__ import annotations

import re
from typing import Any

import structlog

REDACTED = "***REDACTED***"

# A field whose NAME matches this is a secret regardless of its value.
SECRET_FIELD_RE = re.compile(
    r"(api[_-]?key|secret|token|password|passwd|credential|authorization|auth[_-]?header|"
    r"access[_-]?key|private[_-]?key|session[_-]?id|bearer|signature)",
    re.IGNORECASE,
)

# A bare "key" field is a secret; "keys", "key_count", "keyword" are not.
_BARE_KEY_RE = re.compile(r"^keys?$", re.IGNORECASE)

# Recognisable secret VALUES, caught even under an innocuous field name.
_VALUE_PATTERNS = (
    re.compile(r"sk-ant-[A-Za-z0-9_\-]{8,}"),  # Anthropic
    re.compile(r"\bsk-[A-Za-z0-9]{16,}"),  # OpenAI-style
    re.compile(r"\bntn_[A-Za-z0-9]{16,}"),  # Notion
    re.compile(r"\bsecret_[A-Za-z0-9]{16,}"),  # Notion (legacy)
    re.compile(r"\blin_api_[A-Za-z0-9]{16,}"),  # Linear
    re.compile(r"\bAIza[A-Za-z0-9_\-]{16,}"),  # Google
    re.compile(r"\bghp_[A-Za-z0-9]{16,}"),  # GitHub
    re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{16,}", re.IGNORECASE),
)


def _is_secret_field(name: str) -> bool:
    return bool(SECRET_FIELD_RE.search(name) or _BARE_KEY_RE.match(name))


def _scrub_value(value: object) -> object:
    """Mask secret-looking substrings inside an otherwise innocuous value."""
    if isinstance(value, str):
        for pattern in _VALUE_PATTERNS:
            value = pattern.sub(REDACTED, value)
        return value
    if isinstance(value, dict):
        return _redact_mapping(value)
    if isinstance(value, list | tuple):
        scrubbed = [_scrub_value(v) for v in value]
        return type(value)(scrubbed) if isinstance(value, tuple) else scrubbed
    return value


def _redact_mapping(data: dict) -> dict:
    out: dict = {}
    for key, value in data.items():
        if isinstance(key, str) and _is_secret_field(key):
            out[key] = REDACTED
        else:
            out[key] = _scrub_value(value)
    return out


def redact_secrets(
    _logger: object,
    _method_name: str,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    """structlog processor: drop values of key/token/secret-named fields.

    Nested dicts and sequences are walked, and recognisable key formats are
    masked even when bound under a harmless field name.
    """
    return _redact_mapping(dict(event_dict))


def configure_logging(*, render_json: bool = False) -> None:
    """Configure structlog once, at process entry point."""
    renderer = (
        structlog.processors.JSONRenderer() if render_json else structlog.dev.ConsoleRenderer()
    )
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            redact_secrets,  # must run before any renderer
            renderer,
        ],
        wrapper_class=structlog.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> Any:  # noqa: ANN401 — structlog BoundLogger is untyped
    return structlog.get_logger(name)
