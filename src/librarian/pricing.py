"""Model price table and token-usage cost, in one place.

USD per million tokens, keyed by model id. Source: the claude-api skill's model table
(2026-10-06 snapshot) and its models.md / prompt-caching.md notes. The skill states input and
output prices for every model, cache reads explicitly for Fable 5.1 ($0.25), Fable 5 ($1.00),
Opus 5.5 and Sonnet 5.5 ($0.20), and otherwise "~0.1x input"; cache writes are 1.25x input for
the default 5-minute TTL. Entries marked "derived" apply those multipliers to the stated input
price. The spend cap is an estimate, not a bill: Haiku 5.5 is priced at its up-to-100K-token
rate (prompts above 100K cost $0.50 / $2.50), which a chat turn here does not reach.

A model missing from the table is refused at startup (`librarian.api.startup`); extend the table
rather than adding a price setting.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


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
    "claude-fable-5-1": ModelPrice(10.00, 50.00, 0.25, 12.50),
    "claude-fable-5": ModelPrice(10.00, 50.00, 1.00, 12.50),
    "claude-opus-5-5": ModelPrice(4.00, 20.00, 0.20, 5.00),
    "claude-opus-5": ModelPrice(5.00, 25.00, 0.50, 6.25),  # cache: derived
    "claude-opus-4-8": ModelPrice(5.00, 25.00, 0.50, 6.25),  # cache: derived
    "claude-opus-4-7": ModelPrice(5.00, 25.00, 0.50, 6.25),  # cache: derived
    "claude-opus-4-6": ModelPrice(5.00, 25.00, 0.50, 6.25),  # cache: derived
    "claude-sonnet-5-5": ModelPrice(2.00, 10.00, 0.20, 2.50),
    "claude-sonnet-5": ModelPrice(2.00, 10.00, 0.20, 2.50),  # cache read: derived
    "claude-sonnet-4-6": ModelPrice(3.00, 15.00, 0.30, 3.75),  # cache: derived
    "claude-haiku-5-5": ModelPrice(0.10, 0.50, 0.01, 0.125),  # cache: derived; <=100K prompts
    "claude-haiku-4-5": ModelPrice(1.00, 5.00, 0.10, 1.25),  # cache: derived
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
