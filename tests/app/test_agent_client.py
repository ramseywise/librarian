"""Tests for the ANTHROPIC_API_KEY guard in apps.api.agent (GH #54)."""

from __future__ import annotations

import pytest


def test_missing_anthropic_api_key_raises_runtime_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_get_client() must raise RuntimeError (not KeyError) when the key is absent."""
    import apps.api.agent as agent_module

    # Reset the cached client so the factory runs again
    monkeypatch.setattr(agent_module, "_client", None)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        agent_module._get_client()


def test_present_anthropic_api_key_does_not_raise(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When ANTHROPIC_API_KEY is set, _get_client() must not raise."""
    import apps.api.agent as agent_module

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
