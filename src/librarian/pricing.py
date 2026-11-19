"""Model price table and token-usage cost, in one place.

USD per million tokens, keyed by model id. Source: the published pricing page
(platform.claude.com/docs/en/about-claude/pricing, read 2026-11-19), every column taken from it.
Cache reads are 0.1x input except Fable 5.1 / 5.2 (0.025x) and Opus 5.5 / Sonnet 5.5 (0.05x);
cache writes are the 5-minute TTL rate (1.25x input). The spend cap is an estimate, not a bill:
Haiku 5.5 is priced at its up-to-100K-token rate (prompts above 100K cost $0.50 / $2.50), which a
chat turn here does not reach, and the 1.1x US-only `inference_geo` multiplier is not applied.

A model missing from the table is refused at startup (`librarian.api.startup`); extend the table
rather than adding a price setting.

The table is reviewed monthly. `PRICES_REVIEWED` is the date someone last compared it with the
published prices and the claude-api skill's table; `librarian pricing check` prints it and exits 1
once it is more than `MAX_AGE_DAYS` old. Bump the date only after that comparison.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime

# Last time the table below was compared with the published prices.
PRICES_REVIEWED = date(2026, 11, 19)
MAX_AGE_DAYS = 35  # a monthly review plus a few days' slack


@dataclass(frozen=True)
class ModelPrice:
    input: float
    output: float
    cache_read: float
    cache_write: float  # 5-minute TTL


@dataclass(frozen=True)
class TokenUsage:
    """Tokens one model call billed, split by rate. `input` is the uncached remainder only."""

    input: int = 0
    output: int = 0
    cache_read: int = 0
    cache_write: int = 0

    def __add__(self, other: TokenUsage) -> TokenUsage:
        return TokenUsage(
            self.input + other.input,
            self.output + other.output,
            self.cache_read + other.cache_read,
            self.cache_write + other.cache_write,
        )


PRICES: dict[str, ModelPrice] = {
    "claude-fable-5-2": ModelPrice(8.00, 40.00, 0.20, 10.00),
    "claude-fable-5-1": ModelPrice(10.00, 50.00, 0.25, 12.50),
    "claude-fable-5": ModelPrice(10.00, 50.00, 1.00, 12.50),
    "claude-opus-5-5": ModelPrice(4.00, 20.00, 0.20, 5.00),
    "claude-opus-5": ModelPrice(5.00, 25.00, 0.50, 6.25),
    "claude-opus-4-8": ModelPrice(5.00, 25.00, 0.50, 6.25),
    "claude-opus-4-7": ModelPrice(5.00, 25.00, 0.50, 6.25),
    "claude-opus-4-6": ModelPrice(5.00, 25.00, 0.50, 6.25),
    "claude-sonnet-5-5": ModelPrice(2.00, 10.00, 0.10, 2.50),
    "claude-sonnet-5": ModelPrice(2.00, 10.00, 0.20, 2.50),
    "claude-sonnet-4-6": ModelPrice(3.00, 15.00, 0.30, 3.75),
    "claude-haiku-5-5": ModelPrice(0.10, 0.50, 0.01, 0.125),  # <=100K prompts
    "claude-haiku-4-5": ModelPrice(1.00, 5.00, 0.10, 1.25),
    # Gemini (LIBRARIAN_CHAT_PROVIDER=gemini), paid-tier rates from ai.google.dev/gemini-api/docs/pricing;
    # the free tier bills nothing, so the cap overestimates there. Gemini has no cache-write
    # charge, so that column is the input rate.
    "gemini-2.5-flash-lite": ModelPrice(0.10, 0.40, 0.01, 0.10),
    "gemini-2.5-flash": ModelPrice(0.30, 2.50, 0.03, 0.30),
}

# The chat agent's default model: the current Sonnet-class model.
DEFAULT_CHAT_MODEL = "claude-sonnet-5-5"


_SNAPSHOT_SUFFIX = re.compile(r"-\d{8}$")


def price_for(model: str) -> ModelPrice | None:
    """The price of `model`; a dated snapshot id (`claude-haiku-4-5-20251001`) prices as its alias."""
    return PRICES.get(model) or PRICES.get(_SNAPSHOT_SUFFIX.sub("", model))


def cost_usd(model: str, usage: TokenUsage) -> float:
    """Dollar cost of `usage` on `model`. Raises KeyError for a model not in the table."""
    p = price_for(model)
    if p is None:
        raise KeyError(model)
    return (
        usage.input * p.input
        + usage.output * p.output
        + usage.cache_read * p.cache_read
        + usage.cache_write * p.cache_write
    ) / 1_000_000


def review_age_days(today: date | None = None) -> int:
    return ((today or datetime.now(UTC).date()) - PRICES_REVIEWED).days


def main(argv: Sequence[str] | None = None) -> int:
    """`librarian pricing check`: print the table and its review date; exit 1 when it is stale."""
    parser = argparse.ArgumentParser(prog="librarian pricing")
    sub = parser.add_subparsers(dest="verb", required=True)
    sub.add_parser("check", help="print the price table; exit 1 if not reviewed in 35 days")
    parser.parse_args(list(argv) if argv is not None else sys.argv[1:])

    from librarian.config import get_settings

    print(
        f"{'model':<20} {'input':>8} {'output':>8} {'cache read':>11} {'cache write':>12}  (USD / 1M tokens)"
    )
    for model, p in PRICES.items():
        print(
            f"{model:<20} {p.input:>8.3f} {p.output:>8.3f} {p.cache_read:>11.3f} {p.cache_write:>12.3f}"
        )
    age = review_age_days()
    print(f"\nlast reviewed: {PRICES_REVIEWED.isoformat()} ({age} days ago; limit {MAX_AGE_DAYS})")
    configured = get_settings().chat_model
    if price_for(configured) is None:
        print(f"FAIL: the configured model {configured!r} is not in the table", file=sys.stderr)
        return 1
    if age > MAX_AGE_DAYS:
        print(
            f"FAIL: the price table was last reviewed {age} days ago. Compare it with the "
            "published prices, then update PRICES_REVIEWED in src/librarian/pricing.py.",
            file=sys.stderr,
        )
        return 1
    return 0
