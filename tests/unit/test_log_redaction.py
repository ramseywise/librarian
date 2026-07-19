"""Evidence for Buyi "Secrets never committed, never logged" — the logging clause.

Cures the BY-4 debt record: no log redaction filter existed; the invariant held
by convention only. redact_secrets drops values for key/token/secret-named
fields before any renderer sees the event.
"""

from __future__ import annotations

import json

import pytest
import structlog

from app.log_config import REDACTED, configure_logging, redact_secrets

FAKE_ANTHROPIC = "sk-ant-api03-AAAAAAAABBBBBBBBCCCCCCCCDDDDDDDD"
FAKE_NOTION = "ntn_AAAAAAAABBBBBBBBCCCCCCCC"
FAKE_LINEAR = "lin_api_AAAAAAAABBBBBBBBCCCCCCCC"
FAKE_GOOGLE = "AIzaAAAAAAAABBBBBBBBCCCCCCCCDDDD"


def scrub(**fields: object) -> dict:
    return redact_secrets(None, "info", {"event": "test", **fields})


def test_redacts_api_key_field() -> None:
    assert scrub(api_key=FAKE_ANTHROPIC)["api_key"] == REDACTED


def test_redacts_common_secret_field_names() -> None:
    for name in (
        "key",
        "api_key",
        "apiKey",
        "ANTHROPIC_API_KEY",
        "token",
        "access_token",
        "secret",
        "client_secret",
        "password",
        "credential",
        "authorization",
        "private_key",
    ):
        out = scrub(**{name: "some-sensitive-value"})
        assert out[name] == REDACTED, f"{name} must be redacted"


def test_leaves_innocuous_fields_intact() -> None:
    out = scrub(n_results=3, query="crag", keyword="rag", key_count=7, monkey="business")
    assert out["n_results"] == 3
    assert out["query"] == "crag"
    assert out["keyword"] == "rag"
    assert out["key_count"] == 7
    assert out["monkey"] == "business"


def test_redacts_nested_dict_values() -> None:
    out = scrub(config={"model": "claude-opus-4-8", "api_key": FAKE_ANTHROPIC})
    assert out["config"]["model"] == "claude-opus-4-8"
    assert out["config"]["api_key"] == REDACTED


def test_redacts_key_shaped_value_under_innocuous_field_name() -> None:
    """The dangerous case: a real key bound to a field named something harmless."""
    for fake in (FAKE_ANTHROPIC, FAKE_NOTION, FAKE_LINEAR, FAKE_GOOGLE):
        out = scrub(error=f"auth failed for {fake}")
        assert fake not in out["error"], f"{fake[:12]}... leaked in an error string"
        assert REDACTED in out["error"]


def test_redacts_inside_lists() -> None:
    out = scrub(args=["--key", FAKE_ANTHROPIC])
    assert FAKE_ANTHROPIC not in json.dumps(out)


def test_end_to_end_rendered_output_has_no_key(capsys: pytest.CaptureFixture[str]) -> None:
    """The processor runs in the real configured pipeline, before the renderer."""
    configure_logging(render_json=True)
    log = structlog.get_logger("test")
    log.info("etl.auth", api_key=FAKE_ANTHROPIC, note=f"used {FAKE_NOTION}")

    out = capsys.readouterr().out
    assert FAKE_ANTHROPIC not in out
    assert FAKE_NOTION not in out
    assert REDACTED in out
