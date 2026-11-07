"""Tests for the ANTHROPIC_API_KEY guard in librarian.api.agent (GH #54)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from librarian.config import get_settings


@pytest.fixture(autouse=True)
def _fresh_settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Rebuild the cached Settings after each env change, and again once it is undone."""
    get_settings.cache_clear()
    yield
    monkeypatch.undo()
    get_settings.cache_clear()


def test_missing_anthropic_api_key_raises_runtime_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_get_client() must raise RuntimeError (not KeyError) when the key is absent."""
    import librarian.api.agent as agent_module

    # Reset the cached client so the factory runs again
    monkeypatch.setattr(agent_module, "_client", None)
    # An empty env value beats the repo's .env file, so a developer's real key cannot leak in.
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")

    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        agent_module._get_client()


def test_present_anthropic_api_key_does_not_raise(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When ANTHROPIC_API_KEY is set, _get_client() must not raise."""
    import librarian.api.agent as agent_module

    monkeypatch.setattr(agent_module, "_client", None)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key-for-test")

    # AsyncAnthropic.__init__ does not call the network; we only care that
    # RuntimeError / KeyError is NOT raised during the guard check.
    try:
        agent_module._get_client()
    except RuntimeError as exc:
        # Guard raised — unexpected
        pytest.fail(f"_get_client() raised RuntimeError with key set: {exc}")
    finally:
        monkeypatch.setattr(agent_module, "_client", None)
