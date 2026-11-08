"""The three reports: experiment comparison, product metrics, release regression check."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DatabaseError

from librarian.metrics.data import (
    MIN_N,
    Answer,
    group_by,
    load_answers,
    load_ratings,
    mean,
    percentile,
    rate,
)

GROUNDING_DROP = 0.10  # check-release fails on a fall of more than 10 points
DOWN_RATE_RISE = 0.10


@dataclass
class GroupStats:
    """Everything the reports say about one set of answers (a variant or a release)."""

    label: str
    n: int
    grounding_rate: float | None
    n_rated: int
    rating_rate: float | None  # rated answers / answers
    mean_rating: float | None  # mean of +1/-1 over rated answers
    down_rate: float | None  # down-rated answers / answers
    latency_p50_ms: float | None
    latency_p95_ms: float | None
    pages_read_mean: float | None
    cost_per_answer: float | None
    n_cost: int  # answers that logged a cost


def summarize(label: str, answers: list[Answer], ratings: dict[str, int]) -> GroupStats:
    graded = [a.grounded for a in answers if a.grounded is not None]
    rated = [ratings[a.answer_id] for a in answers if a.answer_id and a.answer_id in ratings]
    latencies = [a.latency_ms for a in answers if a.latency_ms is not None]
    costs = [a.cost for a in answers if a.cost is not None]
    return GroupStats(
        label=label,
        n=len(answers),
        grounding_rate=rate(sum(graded), len(graded)),
        n_rated=len(rated),
        rating_rate=rate(len(rated), len(answers)),
        mean_rating=mean(rated),
        down_rate=rate(sum(r == -1 for r in rated), len(answers)),
        latency_p50_ms=percentile(latencies, 50),
        latency_p95_ms=percentile(latencies, 95),
        pages_read_mean=mean(a.pages_read for a in answers),
        cost_per_answer=mean(costs),
        n_cost=len(costs),
    )


def _pct(v: float | None) -> str:
    return "-" if v is None else f"{v * 100:.0f}%"


def _num(v: float | None, fmt: str = "{:.0f}") -> str:
    return "-" if v is None else fmt.format(v)


# -- eval compare -------------------------------------------------------------------------


@dataclass
class Comparison:
    experiment: str
    since: str | None
    variants: list[GroupStats]
    too_few: list[str] = field(default_factory=list)

    @property
    def comparable(self) -> bool:
        return len(self.variants) >= 2 and not self.too_few

    def to_json(self) -> dict[str, Any]:
        return {
            "experiment": self.experiment,
            "since": self.since,
            "min_n": MIN_N,
            "comparable": self.comparable,
            "too_few": self.too_few,
            "variants": [asdict(v) for v in self.variants],
        }

    def render(self) -> str:
        head = [
            "variant",
            "n",
            "grounded",
            "rated",
            "mean",
            "p50 ms",
            "p95 ms",
            "pages",
            "$/answer",
        ]
        rows = [head]
        for v in self.variants:
            rows.append(
                [
                    v.label,
                    str(v.n),
                    _pct(v.grounding_rate),
                    f"{_pct(v.rating_rate)} (n={v.n_rated})",
                    _num(v.mean_rating, "{:+.2f}"),
                    _num(v.latency_p50_ms),
                    _num(v.latency_p95_ms),
                    _num(v.pages_read_mean, "{:.1f}"),
                    "-" if v.cost_per_answer is None else f"{v.cost_per_answer:.4f} (n={v.n_cost})",
                ]
            )
        widths = [max(len(r[i]) for r in rows) for i in range(len(head))]
        lines = [f"experiment: {self.experiment}" + (f"  since {self.since}" if self.since else "")]
        lines += ["  ".join(c.ljust(w) for c, w in zip(r, widths, strict=True)) for r in rows]
        if not self.variants:
            lines.append(f"No answers carry the experiment {self.experiment!r}.")
        elif self.too_few:
            lines.append(
                f"Too few to compare: {', '.join(self.too_few)} below n={MIN_N}. "
                "Read the rows as a count, not a verdict."
            )
        elif len(self.variants) < 2:
            lines.append("Only one variant has answers; nothing to compare it with.")
        else:
            lines.append(f"Every variant has n >= {MIN_N}. Promotion is a config change, by hand.")
        return "\n".join(lines)


def compare(experiment: str, *, engine: Engine, since: datetime | None = None) -> Comparison:
    answers = [a for a in load_answers(since=since) if not a.error]
    ratings = load_ratings(engine, since)
    # Answers made before the experiment existed (no entry for it) are not a variant of it.
    in_experiment = [a for a in answers if experiment in a.experiment]
    variants = [
        summarize(label, group, ratings)
        for label, group in group_by(in_experiment, lambda a: a.variant(experiment))
    ]
    return Comparison(
        experiment=experiment,
        since=since.date().isoformat() if since else None,
        variants=variants,
        too_few=[v.label for v in variants if v.n < MIN_N],
    )


# -- product metrics ----------------------------------------------------------------------


def _distribution(by_user: dict[str, float]) -> dict[str, float | int | None]:
    """Spend per user as a distribution; no user is named."""
    values = list(by_user.values())
    return {
        "users": len(values),
        "median": percentile(values, 50),
        "p90": percentile(values, 90),
        "max": max(values) if values else None,
    }


def study_counts(engine: Engine, since: datetime) -> dict[str, int]:
    """Flashcard reviews, quiz and drill answers, and lessons finished, since `since`."""
    from librarian.db import tables

    out = {"flashcards_reviewed": 0, "quiz_answers": 0, "drill_runs": 0, "lessons_done": 0}
    kinds = {"flashcard": "flashcards_reviewed", "mcq": "quiz_answers", "drill": "drill_runs"}
    try:
        with engine.connect() as conn:
            for kind, count in conn.execute(
                select(tables.attempts.c.kind, func.count())
                .where(tables.attempts.c.ts >= since)
                .group_by(tables.attempts.c.kind)
            ):
                if kind in kinds:
                    out[kinds[kind]] = int(count)
            out["lessons_done"] = int(
                conn.execute(
                    select(func.count()).where(
                        tables.progress.c.state == "done", tables.progress.c.updated_at >= since
                    )
                ).scalar_one()
            )
    except DatabaseError:
        pass
    return out


@dataclass
class ProductReport:
    days: int
    by: str
    groups: list[dict[str, Any]]
    study: dict[str, int]

    def to_json(self) -> dict[str, Any]:
        return {"days": self.days, "by": self.by, "groups": self.groups, "study": self.study}

    def render(self) -> str:
        head = [
            "group",
            "answers",
            "per day",
            "grounded",
            "rated",
            "down",
            "spend/user med/p90/max",
        ]
        rows = [head]
        for g in self.groups:
            d = g["spend_per_user"]
            spend = (
                "-"
                if d["users"] == 0
                else "/".join(_num(d[k], "{:.3f}") for k in ("median", "p90", "max"))
                + f" (users={d['users']})"
            )
            rows.append(
                [
                    g["label"],
                    str(g["n"]),
                    f"{g['answers_per_day']:.1f}",
                    _pct(g["grounding_rate"]),
                    f"{_pct(g['rating_rate'])} (n={g['n_rated']})",
                    _pct(g["down_rate"]),
                    spend,
                ]
            )
        widths = [max(len(r[i]) for r in rows) for i in range(len(head))]
        lines = [f"last {self.days} days, by {self.by}"]
        lines += ["  ".join(c.ljust(w) for c, w in zip(r, widths, strict=True)) for r in rows]
        if not self.groups:
            lines.append("No chat answers in the window.")
        s = self.study
        lines.append(
            f"study (all users, not split by {self.by}): {s['flashcards_reviewed']} cards reviewed, "
            f"{s['quiz_answers']} quiz answers, {s['drill_runs']} drill runs, "
            f"{s['lessons_done']} lessons done"
        )
        return "\n".join(lines)


def product(
    *, engine: Engine, days: int = 30, by: str = "release", now: datetime | None = None
) -> ProductReport:
    now = now or datetime.now(UTC)
    since = now - timedelta(days=days)
    answers = [a for a in load_answers(since=since) if not a.error]
    ratings = load_ratings(engine, since)

    def key(a: Answer) -> str:
        if by == "experiment":
            return ";".join(f"{k}={v}" for k, v in sorted(a.experiment.items())) or "(none)"
        return a.release or "(unknown)"

    groups: list[dict[str, Any]] = []
    for label, group in group_by(answers, key):
        stats = summarize(label, group, ratings)
        spend: dict[str, float] = {}
        for a in group:
            if a.user_id and a.cost is not None:
                spend[a.user_id] = spend.get(a.user_id, 0.0) + a.cost
        groups.append(
            {
                **asdict(stats),
                "answers_per_day": stats.n / max(days, 1),
                "spend_per_user": _distribution(spend),
            }
        )
    return ProductReport(days=days, by=by, groups=groups, study=study_counts(engine, since))


# -- release check ------------------------------------------------------------------------


@dataclass
class ReleaseCheck:
    current: GroupStats | None
    previous: GroupStats | None
    failures: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failures

    def render(self) -> str:
        lines: list[str] = []
        for tag, g in (("previous", self.previous), ("current", self.current)):
            if g:
                lines.append(
                    f"{tag:8} {g.label}: n={g.n}, grounded {_pct(g.grounding_rate)}, "
                    f"down-rated {_pct(g.down_rate)} (rated n={g.n_rated})"
                )
        lines += [f"NOTE: {n}" for n in self.notes]
        lines += [f"FAIL: {f}" for f in self.failures]
        if self.ok and not self.notes:
            lines.append("OK: no drop in grounding or rise in down-ratings after the release.")
        return "\n".join(lines)


def check_release(
    *,
    engine: Engine,
    days: int = 30,
    current: str | None = None,
    previous: str | None = None,
    now: datetime | None = None,
) -> ReleaseCheck:
    """Current release (latest answer, or `current`) against the one before it."""
    now = now or datetime.now(UTC)
    since = now - timedelta(days=days)
    answers = [a for a in load_answers(since=since) if a.release and not a.error]
    ratings = load_ratings(engine, since)
    last_seen: dict[str, datetime] = {}
    for a in answers:
        last_seen[a.release] = max(last_seen.get(a.release, a.ts), a.ts)
    order = sorted(last_seen, key=lambda r: last_seen[r], reverse=True)
    cur = current or (order[0] if order else None)
    prev = previous or next((r for r in order if r != cur), None)
    if cur is None or prev is None:
        return ReleaseCheck(
            None,
            None,
            notes=[
                "need answers from two releases (rows with a `release` field) in the window; "
                f"found {len(order)}."
            ],
        )
    by_release = {r: [a for a in answers if a.release == r] for r in (cur, prev)}
    c = summarize(cur, by_release[cur], ratings)
    p = summarize(prev, by_release[prev], ratings)
    check = ReleaseCheck(current=c, previous=p)
    if min(c.n, p.n) < MIN_N:
        check.notes.append(f"n < {MIN_N} on one side (previous {p.n}, current {c.n}); not judged.")
        return check
    if c.grounding_rate is not None and p.grounding_rate is not None:
        drop = p.grounding_rate - c.grounding_rate
        if drop > GROUNDING_DROP:
            check.failures.append(
                f"grounding fell {drop * 100:.0f} points after {cur} "
                f"({_pct(p.grounding_rate)} -> {_pct(c.grounding_rate)})."
            )
    if c.down_rate is not None and p.down_rate is not None:
        rise = c.down_rate - p.down_rate
        if rise > DOWN_RATE_RISE:
            check.failures.append(
                f"down-rating rate rose {rise * 100:.0f} points after {cur} "
                f"({_pct(p.down_rate)} -> {_pct(c.down_rate)})."
            )
    return check
