"""_quiz.md loading and checking (librarian/courses/quiz.py, checks/check_quiz.py)."""

from __future__ import annotations

from pathlib import Path

import pytest

from librarian.courses import quiz
from librarian.courses.checks import check_quiz

LESSONS = {"c/m/intro"}


def _file(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "_quiz.md"
    path.write_text(f"---\nquestions:\n{body}---\n")
    return path


GOOD = "- {prompt: Why?, options: [a, b], answer: b, explanation: Because., lesson: c/m/intro}\n"


def test_a_well_formed_question_loads_with_a_stable_hash_id(tmp_path: Path) -> None:
    (q,) = quiz.load(_file(tmp_path, GOOD), LESSONS)
    assert (q.prompt, q.options, q.answer, q.lesson) == ("Why?", ("a", "b"), "b", "c/m/intro")
    assert q.id == quiz.prompt_id("Why?") and len(q.id) == quiz.ID_HASH_CHARS


def test_a_given_id_survives_rewording(tmp_path: Path) -> None:
    body = "- {id: q-1, prompt: Reworded?, options: [a, b], answer: a}\n"
    assert quiz.load(_file(tmp_path, body), set())[0].id == "q-1"


def test_question_key_is_shared_by_module_and_lesson_quiz() -> None:
    assert quiz.question_key("c/m", "x") == quiz.question_key("c/m/intro", "x") == "c/m:q:x"


@pytest.mark.parametrize(
    ("raw", "fragment"),
    [
        ("- {options: [a, b], answer: a}\n", "no prompt"),
        ("- {prompt: P, options: [a], answer: a}\n", "options must be"),
        ("- {prompt: P, options: [a, a], answer: a}\n", "duplicate options"),
        ("- {prompt: P, options: [a, b], answer: c}\n", "answer is not one of the options"),
        ("- {id: 'bad id', prompt: P, options: [a, b], answer: a}\n", "characters outside"),
        ("- {prompt: P, options: [a, b], answer: a, lesson: c/m/gone}\n", "not in this module"),
        ("- text\n", "not a mapping"),
        ("- {prompt: P, answer: about six}\n", "needs a number"),
        ("- {prompt: P, answer: '6', tolerance: -1}\n", "tolerance must be"),
    ],
)
def test_strict_check_names_each_problem(tmp_path: Path, raw: str, fragment: str) -> None:
    problems = quiz.problems_in(_file(tmp_path, raw), LESSONS)
    assert any(fragment in p for p in problems), problems


def test_check_reports_repeated_ids_and_an_empty_file(tmp_path: Path) -> None:
    twice = "- {id: x, prompt: A, options: [a, b], answer: a}\n- {id: x, prompt: B, options: [a, b], answer: a}\n"
    assert any("repeats question 1" in p for p in quiz.problems_in(_file(tmp_path, twice), set()))
    empty = tmp_path / "e" / "_quiz.md"
    empty.parent.mkdir()
    empty.write_text("---\ntitle: T\n---\n")
    assert quiz.problems_in(empty, set()) == ["no `questions:` list in the frontmatter"]


def test_the_catalog_loader_drops_bad_questions_and_unknown_lessons(tmp_path: Path) -> None:
    body = (
        "- {prompt: Bad, options: [a], answer: a}\n"
        "- {id: k, prompt: Ok, options: [a, b], answer: a, lesson: c/m/gone}\n"
        "- {id: k, prompt: Dup, options: [a, b], answer: a}\n"
    )
    (q,) = quiz.load(_file(tmp_path, body), LESSONS)
    assert (q.id, q.lesson) == ("k", None)
    assert quiz.load(tmp_path / "missing.md", LESSONS) == []


def test_the_payload_never_carries_the_answer_or_explanation(tmp_path: Path) -> None:
    (q,) = quiz.load(_file(tmp_path, GOOD), LESSONS)
    payload = quiz.public_payload(q, "Intro")
    assert set(payload) == {"id", "prompt", "options", "kind", "hasHint", "lesson", "lessonTitle"}
    assert payload["kind"] == "choice"


def test_a_hint_is_kept_for_worked_problems_only_and_not_sent(tmp_path: Path) -> None:
    raw = "- {id: w, prompt: p, answer: '1', hint: Think of p(1 - p).}\n"
    raw += "- {id: c, prompt: p2, options: [a, b], answer: a, hint: ignored}\n"
    w, c = quiz.load(_file(tmp_path, raw), LESSONS)
    assert (w.hint, c.hint) == ("Think of p(1 - p).", "")
    assert quiz.public_payload(w, None)["hasHint"] is True
    assert "Think of" not in str(quiz.public_payload(w, None))


WORKED = "- {id: w, prompt: Variance of Bernoulli(0.2)?, answer: '0.16', explanation: p(1 - p).}\n"


def test_a_question_with_no_options_is_a_worked_problem_graded_within_tolerance(
    tmp_path: Path,
) -> None:
    (q,) = quiz.load(_file(tmp_path, WORKED), LESSONS)
    assert q.worked and q.tolerance == pytest.approx(0.005)
    assert quiz.public_payload(q, None)["kind"] == "worked"
    assert [quiz.is_correct(q, typed) for typed in ("0.16", " 0.164 ", "4/25", "0.17")] == [
        True,
        True,
        True,
        False,
    ]
    with pytest.raises(ValueError, match="not a number"):
        quiz.is_correct(q, "a sixth")


@pytest.mark.parametrize(
    ("answer", "extra", "right", "wrong"),
    [
        ("6400", "", "6,400", "6401"),  # a whole number is exact
        ("18.7", "", "18.7%", "18.8"),
        ("1068", ", tolerance: 1", "1067", "1070"),
    ],
)
def test_worked_tolerance_follows_the_answer_unless_given(
    tmp_path: Path, answer: str, extra: str, right: str, wrong: str
) -> None:
    (q,) = quiz.load(_file(tmp_path, f"- {{prompt: P, answer: '{answer}'{extra}}}\n"), LESSONS)
    assert quiz.is_correct(q, right)
    assert not quiz.is_correct(q, wrong)


def test_check_quiz_run_reads_module_quizzes_and_their_lessons(tmp_path: Path) -> None:
    module = tmp_path / "c" / "m"
    module.mkdir(parents=True)
    (module / "intro.md").write_text("---\ntitle: I\n---\n")
    _file(module, GOOD)
    files, lines = check_quiz.run(tmp_path, [])
    assert (files, lines) == (1, [])
    (module / "_quiz.md").write_text(
        "---\nquestions:\n- {prompt: P, options: [a, b], answer: z}\n---\n"
    )
    files, lines = check_quiz.run(tmp_path, [])
    assert files == 1 and "c/m/_quiz.md: question 1: answer is not one of the options" in lines
    assert check_quiz.main(["--root", str(tmp_path)]) == 1


def test_depth_subject_and_topic_are_kept_and_never_sent(tmp_path: Path) -> None:
    body = (
        "- {prompt: Tagged?, options: [a, b], answer: a, depth: deep, "
        "subject: programming, topic: hashing}\n"
        "- {prompt: Plain?, options: [a, b], answer: a}\n"
    )
    tagged, plain = quiz.load(_file(tmp_path, body), set())
    assert (tagged.depth, tagged.subject, tagged.topic) == ("deep", "programming", "hashing")
    assert (plain.depth, plain.subject, plain.topic) == ("", "", "")
    assert not {"depth", "subject", "topic"} & set(quiz.public_payload(tagged, None))


def test_an_illegal_depth_or_unknown_subject_is_a_problem(tmp_path: Path) -> None:
    body = (
        "- {prompt: One?, options: [a, b], answer: a, depth: hard}\n"
        "- {prompt: Two?, options: [a, b], answer: a, subject: cooking}\n"
    )
    path = _file(tmp_path, body)
    lines = quiz.problems_in(path, set(), {"programming"})
    assert any("question 1: depth 'hard' is not one of intro, core, deep" in p for p in lines)
    assert any("question 2: subject 'cooking' is not a course" in p for p in lines)
    # Without the course names the subject is not checked, and the lenient loader drops only the bad depth.
    assert not any("subject" in p for p in quiz.problems_in(path, set()))
    assert [q.prompt for q in quiz.load(path, set())] == ["Two?"]


def test_check_quiz_takes_subjects_from_the_public_course_folders(tmp_path: Path) -> None:
    module = tmp_path / "interviewing" / "bank"
    module.mkdir(parents=True)
    (tmp_path / "programming").mkdir()
    (tmp_path / "private" / "secret-course").mkdir(parents=True)
    _file(module, "- {prompt: P?, options: [a, b], answer: a, subject: programming, depth: core}\n")
    assert check_quiz.run(tmp_path, []) == (1, [])
    _file(module, "- {prompt: P?, options: [a, b], answer: a, subject: secret-course}\n")
    _, lines = check_quiz.run(tmp_path, [])
    assert len(lines) == 1 and "is not a course" in lines[0]


def test_the_seeded_interview_quiz_passes_the_check() -> None:
    assert check_quiz.main(["interviewing"]) == 0
