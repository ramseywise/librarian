"""Placement: the intake's question pool, which block comes next, and the tier a sitting suggests.

A learner is placed per subject on one of three tiers. Each tested subject gets two blocks of
questions: the first at `core` (at `intro` for someone who has never used the subject), the second
chosen by how the first went. The rule is deterministic and its cut-offs come from config (`Cuts`).

Tier is not depth: depth (`librarian.courses.depth`) describes content, tier describes a learner
in one subject. Nothing here touches the database (`librarian.courses.intake` does) and the pool
is built from the public course tree only, so a private quiz can never be served by the intake.
"""

from __future__ import annotations

import random
from collections.abc import Collection, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from librarian.config import Settings
from librarian.courses import quiz
from librarian.courses.depth import TIERS
from librarian.courses.loader import _course_dirs, _module_dirs
from librarian.log_config import get_logger

log = get_logger(__name__)

FOUNDATIONS, PRACTITIONER, SPECIALIST = TIERS

ROLES = ("product", "analyst", "engineer", "ml-engineer", "researcher", "other")
GOALS = ("main-ideas", "do-the-work", "go-deep")
GOAL_TIER: dict[str, str] = dict(zip(GOALS, TIERS, strict=True))
EXPERIENCE = ("never", "read-about", "use-at-work", "could-teach")
NEVER = EXPERIENCE[0]

RESULTS = ("right", "wrong", "dont_know")
RIGHT, WRONG, DONT_KNOW = RESULTS
SOURCES = ("test", "goal", "override")
BLOCKS = (1, 2)

KEY_PREFIX = "placement:"


@dataclass(frozen=True)
class Cuts:
    """Questions per block, and the share of a block that passes it and that fails it."""

    block_size: int
    pass_share: float
    fail_share: float

    @classmethod
    def of(cls, settings: Settings) -> Cuts:
        return cls(
            settings.intake_block_size, settings.intake_pass_share, settings.intake_fail_share
        )


@dataclass(frozen=True)
class PoolQuestion:
    key: str  # `placement:<question id>`: independent of the module, so re-filing keeps its data
    subject: str
    module: str  # `<course>/<module>` the question is filed under
    depth: str
    question: quiz.Question


@dataclass(frozen=True)
class Score:
    """Right answers out of those asked, at one depth of one block."""

    depth: str
    right: int
    asked: int


@dataclass(frozen=True)
class Suggestion:
    tier: str
    borderline_with: str | None = None


Pool = dict[str, dict[str, list[PoolQuestion]]]  # subject → depth → questions


def subjects(settings: Settings) -> list[str]:
    """The subjects the intake offers, in the order configured."""
    return [s.strip() for s in settings.intake_subjects.split(",") if s.strip()]


def build_pool(courses_dir: Path, offered: Collection[str]) -> Pool:
    """Every tagged multiple-choice question of the public tree, by subject and depth.

    A question tests its `subject`, or else the course its file is in. Worked problems and
    untagged questions are left out. A question id seen twice keeps the first and logs the second.
    """
    pool: Pool = {}
    seen: set[str] = set()
    for course, course_dirs in _course_dirs(courses_dir, public=True).items():
        for module, mod_dirs in _module_dirs(course_dirs).items():
            for d in mod_dirs:
                for q in quiz.load(d / quiz.QUIZ_FILE, set()):
                    subject = q.subject or course
                    if q.worked or not q.depth or subject not in offered:
                        continue
                    if q.id in seen:
                        log.error("placement.duplicate_id", id=q.id, module=f"{course}/{module}")
                        continue
                    seen.add(q.id)
                    pool.setdefault(subject, {}).setdefault(q.depth, []).append(
                        PoolQuestion(
                            f"{KEY_PREFIX}{q.id}", subject, f"{course}/{module}", q.depth, q
                        )
                    )
    return pool


def by_key(pool: Pool) -> dict[str, PoolQuestion]:
    return {q.key: q for depths in pool.values() for qs in depths.values() for q in qs}


def testable(pool: Pool, subject: str, cuts: Cuts) -> bool:
    """Whether `subject` has a full block at every depth. Without that it is placed from the goal."""
    depths = pool.get(subject, {})
    return all(len(depths.get(d, [])) >= cuts.block_size for d in ("intro", "core", "deep"))


def _band(score: Score, cuts: Cuts) -> str:
    """`pass`, `fail` or `middle` for one score. Nothing asked is a fail."""
    share = score.right / score.asked if score.asked else 0.0
    if share >= cuts.pass_share:
        return "pass"
    return "fail" if share <= cuts.fail_share else "middle"


def first_block(experience: str, cuts: Cuts) -> dict[str, int]:
    """Depth → number of questions for block 1: `intro` for someone who never used the subject."""
    return {"intro" if experience == NEVER else "core": cuts.block_size}


def second_block(first: Score, cuts: Cuts) -> dict[str, int]:
    """Depth → number of questions for block 2, given how block 1 went. {} when there is none:
    a learner who started on `intro` and did not pass it is done."""
    band = _band(first, cuts)
    if first.depth == "intro":
        return {"core": cuts.block_size} if band == "pass" else {}
    if band == "pass":
        return {"deep": cuts.block_size}
    if band == "fail":
        return {"intro": cuts.block_size}
    half = cuts.block_size // 2
    return {"intro": half, "deep": cuts.block_size - half}


def draw(
    questions: Sequence[PoolQuestion], n: int, seen: Collection[str], rng: random.Random
) -> list[PoolQuestion]:
    """`n` questions at random, unseen ones first and spread across modules (one from each
    before a second from any)."""
    by_module: dict[str, list[PoolQuestion]] = {}
    for q in rng.sample(list(questions), len(questions)):
        by_module.setdefault(q.module, []).append(q)
    spread: list[PoolQuestion] = []
    queues = list(by_module.values())
    rng.shuffle(queues)
    while queues:
        spread += [queue.pop(0) for queue in queues]
        queues = [queue for queue in queues if queue]
    fresh = [q for q in spread if q.key not in seen]
    return (fresh + [q for q in spread if q.key in seen])[:n]


def suggest(first: Score, second: Iterable[Score], cuts: Cuts) -> Suggestion:
    """The tier two blocks point at, and the neighbouring tier when the result is close."""
    later = {s.depth: s for s in second}
    band = _band(first, cuts)
    if first.depth == "intro":  # started low: intro, then core only on a pass
        if band != "pass" or "core" not in later:
            return Suggestion(FOUNDATIONS)
        core = _band(later["core"], cuts)
        if core == "pass":
            return Suggestion(PRACTITIONER)
        return Suggestion(FOUNDATIONS, PRACTITIONER if core == "middle" else None)
    if band == "pass":
        deep = _band(later["deep"], cuts) if "deep" in later else "fail"
        if deep == "pass":
            return Suggestion(SPECIALIST)
        return Suggestion(PRACTITIONER, SPECIALIST if deep == "middle" else None)
    if band == "middle":
        intro = later.get("intro")
        missed_intro = intro is not None and intro.right < intro.asked
        return Suggestion(PRACTITIONER, FOUNDATIONS if missed_intro else None)
    intro_band = _band(later["intro"], cuts) if "intro" in later else "fail"
    return Suggestion(FOUNDATIONS, PRACTITIONER if intro_band == "pass" else None)


def from_goal(goal: str) -> Suggestion:
    """The tier for a subject that was not tested: the one the learner's goal names."""
    return Suggestion(GOAL_TIER.get(goal, PRACTITIONER))


def preselected(suggestion: Suggestion, goal: str) -> str:
    """The tier a learner starts on: on a borderline result the lower of the two, unless their
    goal names the higher one."""
    other = suggestion.borderline_with
    if other is None:
        return suggestion.tier
    low, high = sorted((suggestion.tier, other), key=TIERS.index)
    return high if GOAL_TIER.get(goal) == high else low
