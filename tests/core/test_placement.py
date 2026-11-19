"""The placement rule: which block comes next, the tier two blocks suggest, the pool and the draw."""

from __future__ import annotations

import random
from pathlib import Path

import pytest

from librarian.courses import placement, quiz
from librarian.courses.placement import (
    FOUNDATIONS,
    PRACTITIONER,
    SPECIALIST,
    Cuts,
    PoolQuestion,
    Score,
    Suggestion,
)

CUTS = Cuts(block_size=4, pass_share=0.75, fail_share=0.25)


def _quiz(root: Path, module: str, rows: list[str]) -> None:
    path = root / module / quiz.QUIZ_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\nquestions:\n" + "".join(f"- {{{r}}}\n" for r in rows) + "---\n")


def _q(prompt: str, extra: str = "depth: core") -> str:
    return f"prompt: {prompt}?, options: [a, b], answer: a, {extra}"


def test_the_first_block_is_core_or_intro_for_someone_new() -> None:
    assert placement.first_block("use-at-work", CUTS) == {"core": 4}
    assert placement.first_block("never", CUTS) == {"intro": 4}


@pytest.mark.parametrize(
    ("right", "expected"),
    [
        (4, {"deep": 4}),
        (3, {"deep": 4}),
        (2, {"intro": 2, "deep": 2}),
        (1, {"intro": 4}),
        (0, {"intro": 4}),
    ],
)
def test_the_second_block_follows_the_core_score(right: int, expected: dict[str, int]) -> None:
    assert placement.second_block(Score("core", right, 4), CUTS) == expected


def test_an_intro_start_goes_on_to_core_only_on_a_pass() -> None:
    assert placement.second_block(Score("intro", 3, 4), CUTS) == {"core": 4}
    assert placement.second_block(Score("intro", 2, 4), CUTS) == {}


@pytest.mark.parametrize(
    ("first", "second", "expected"),
    [
        # core passed, then deep
        (Score("core", 4, 4), [Score("deep", 3, 4)], Suggestion(SPECIALIST)),
        (Score("core", 3, 4), [Score("deep", 2, 4)], Suggestion(PRACTITIONER, SPECIALIST)),
        (Score("core", 3, 4), [Score("deep", 1, 4)], Suggestion(PRACTITIONER)),
        # core in the middle, then two intro and two deep
        (
            Score("core", 2, 4),
            [Score("intro", 2, 2), Score("deep", 0, 2)],
            Suggestion(PRACTITIONER),
        ),
        (
            Score("core", 2, 4),
            [Score("intro", 1, 2), Score("deep", 2, 2)],
            Suggestion(PRACTITIONER, FOUNDATIONS),
        ),
        # core failed, then intro
        (Score("core", 1, 4), [Score("intro", 4, 4)], Suggestion(FOUNDATIONS, PRACTITIONER)),
        (Score("core", 0, 4), [Score("intro", 2, 4)], Suggestion(FOUNDATIONS)),
        # started on intro
        (Score("intro", 1, 4), [], Suggestion(FOUNDATIONS)),
        (Score("intro", 4, 4), [Score("core", 3, 4)], Suggestion(PRACTITIONER)),
        (Score("intro", 4, 4), [Score("core", 2, 4)], Suggestion(FOUNDATIONS, PRACTITIONER)),
        (Score("intro", 4, 4), [Score("core", 0, 4)], Suggestion(FOUNDATIONS)),
    ],
)
def test_the_suggested_tier(first: Score, second: list[Score], expected: Suggestion) -> None:
    assert placement.suggest(first, second, CUTS) == expected


def test_a_borderline_result_starts_low_unless_the_goal_names_the_higher_tier() -> None:
    close = Suggestion(PRACTITIONER, SPECIALIST)
    assert placement.preselected(close, "do-the-work") == PRACTITIONER
    assert placement.preselected(close, "go-deep") == SPECIALIST
    assert placement.preselected(Suggestion(PRACTITIONER, FOUNDATIONS), "go-deep") == FOUNDATIONS
    assert placement.preselected(Suggestion(SPECIALIST), "main-ideas") == SPECIALIST


def test_an_untested_subject_is_placed_from_the_goal() -> None:
    assert placement.from_goal("main-ideas") == Suggestion(FOUNDATIONS)
    assert placement.from_goal("go-deep") == Suggestion(SPECIALIST)


def test_the_pool_holds_tagged_public_multiple_choice_only(tmp_path: Path) -> None:
    _quiz(
        tmp_path,
        "ds/01-stats",
        [
            _q("Tagged"),
            "prompt: Untagged?, options: [a, b], answer: a",
            "prompt: Worked?, answer: '3', depth: core",
            _q("Elsewhere", "depth: deep, subject: da"),
            _q("Not offered", "depth: core, subject: cooking"),
        ],
    )
    _quiz(tmp_path, "private/ds/01-stats", [_q("Private overlay")])
    _quiz(tmp_path, "private/secret/01-x", [_q("Private course", "depth: core, subject: ds")])
    pool = placement.build_pool(tmp_path, ["ds", "da"])
    prompts = {q.question.prompt for q in placement.by_key(pool).values()}
    assert prompts == {"Tagged?", "Elsewhere?"}
    assert [q.module for q in pool["da"]["deep"]] == ["ds/01-stats"]
    assert all(k.startswith(placement.KEY_PREFIX) for k in placement.by_key(pool))


def test_a_question_filed_twice_is_served_once(tmp_path: Path) -> None:
    _quiz(tmp_path, "ds/01-stats", [_q("Same")])
    _quiz(tmp_path, "ds/02-ml", [_q("Same")])
    pool = placement.build_pool(tmp_path, ["ds"])
    assert len(pool["ds"]["core"]) == 1


def test_a_subject_is_testable_with_a_full_block_at_every_depth(tmp_path: Path) -> None:
    def rows(course: str) -> list[str]:
        return [
            _q(f"{course} {d}{i}", f"depth: {d}")
            for d in ("intro", "core", "deep")
            for i in range(4)
        ]

    _quiz(tmp_path, "ds/01-stats", rows("ds"))
    _quiz(tmp_path, "da/01-sql", rows("da")[:-1])
    pool = placement.build_pool(tmp_path, ["ds", "da"])
    assert placement.testable(pool, "ds", CUTS)
    assert not placement.testable(pool, "da", CUTS)
    assert not placement.testable(pool, "absent", CUTS)


def _pq(n: int, module: str) -> PoolQuestion:
    q = quiz.Question(id=f"q{n}", prompt=f"Q{n}?", options=("a", "b"), answer="a")
    return PoolQuestion(f"placement:q{n}", "ds", module, "core", q)


def test_the_draw_spreads_across_modules_and_takes_unseen_first() -> None:
    questions = [_pq(n, f"ds/m{n % 4}") for n in range(12)]
    for seed in range(20):
        drawn = placement.draw(questions, 4, set(), random.Random(seed))
        assert len({q.module for q in drawn}) == 4
    seen = {q.key for q in questions[:9]}
    drawn = placement.draw(questions, 4, seen, random.Random(1))
    assert [q.key in seen for q in drawn] == [False, False, False, True]
    assert len(placement.draw(questions[:2], 4, set(), random.Random(1))) == 2
