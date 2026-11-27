"""What stops an open tab from billing forever: an idle limit, a hard maximum, and caps on turns
and tokens. Time comes in as an argument, so tests move it without sleeping."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

EndReason = Literal["idle", "max_duration", "turn_cap", "token_cap"]

END_MESSAGES: dict[str, str] = {
    "idle": "The session ended after a long silence.",
    "max_duration": "The session reached its maximum length.",
    "turn_cap": "The session reached its limit on turns.",
    "token_cap": "The session reached its limit on model usage.",
}


@dataclass
class SessionLimits:
    started: float
    idle_timeout_s: float
    max_duration_s: float
    max_turns: int
    max_tokens: int
    last_activity: float = 0.0
    turns: int = 0
    tokens: int = 0

    def __post_init__(self) -> None:
        self.last_activity = self.started

    def touch(self, now: float) -> None:
        self.last_activity = max(self.last_activity, now)

    def add_turn(self) -> None:
        self.turns += 1

    def add_tokens(self, count: int) -> None:
        self.tokens += max(count, 0)

    def over_budget(self) -> EndReason | None:
        if self.turns >= self.max_turns:
            return "turn_cap"
        if self.tokens >= self.max_tokens:
            return "token_cap"
        return None

    def expired(self, now: float) -> EndReason | None:
        if now - self.started >= self.max_duration_s:
            return "max_duration"
        if now - self.last_activity >= self.idle_timeout_s:
            return "idle"
        return self.over_budget()
