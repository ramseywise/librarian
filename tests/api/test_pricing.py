"""The model price table, the spend cap built on it, and the startup refusal of unknown models."""

from __future__ import annotations

import pytest

from librarian.api.security import ChatLimiter
from librarian.api.startup import find_model_problems
from librarian.config import Settings
from librarian.pricing import DEFAULT_CHAT_MODEL, PRICES, TokenUsage, cost_usd, price_for


def test_default_model_is_in_the_table() -> None:
    assert DEFAULT_CHAT_MODEL == "claude-sonnet-5-5"
    assert price_for(DEFAULT_CHAT_MODEL) is not None


def test_every_price_is_positive_and_cache_read_is_cheaper_than_input() -> None:
    for model, p in PRICES.items():
        assert 0 < p.cache_read < p.input < p.output, model
        assert p.cache_write >= p.input, model


def test_cost_counts_each_token_class_at_its_own_rate() -> None:
    # Sonnet 5.5: $2 in, $10 out, $0.20 cache read, $2.50 cache write per MTok.
    usage = TokenUsage(
        input=1_000_000, output=1_000_000, cache_read=1_000_000, cache_write=1_000_000
    )
    assert cost_usd("claude-sonnet-5-5", usage) == pytest.approx(2 + 10 + 0.20 + 2.50)


def test_cost_of_an_unknown_model_raises() -> None:
    with pytest.raises(KeyError):
        cost_usd("claude-nope", TokenUsage(input=1))


def test_dated_snapshot_ids_price_as_their_alias() -> None:
    assert price_for("claude-haiku-4-5-20251001") == price_for("claude-haiku-4-5")
    assert price_for("claude-nope-20251001") is None


def test_token_usage_adds() -> None:
    assert TokenUsage(1, 2, 3, 4) + TokenUsage(10, 20, 30, 40) == TokenUsage(11, 22, 33, 44)


def test_limiter_prices_cache_reads_below_input() -> None:
    s = Settings(_env_file=None, anthropic_model="claude-sonnet-5-5")
    limiter = ChatLimiter()
    limiter.record_usage(s, TokenUsage(cache_read=1_000_000))
    assert limiter.spent_usd() == pytest.approx(0.20)
    limiter.record_usage(s, TokenUsage(input=1_000_000))
    assert limiter.spent_usd() == pytest.approx(2.20)


def test_limiter_errs_high_for_an_unknown_model() -> None:
    s = Settings(_env_file=None, anthropic_model="claude-nope")
    limiter = ChatLimiter()
    limiter.record_usage(s, TokenUsage(output=1_000_000))
    assert limiter.spent_usd() == pytest.approx(max(p.output for p in PRICES.values()))


def test_startup_refuses_an_unknown_model_and_names_the_known_ones() -> None:
    (error,) = find_model_problems(Settings(_env_file=None, anthropic_model="claude-nope"))
    assert "claude-nope" in error and "claude-sonnet-5-5" in error


def test_startup_accepts_a_known_model() -> None:
    assert find_model_problems(Settings(_env_file=None, anthropic_model="claude-haiku-4-5")) == []
