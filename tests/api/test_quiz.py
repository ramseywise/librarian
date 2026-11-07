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
    assert set(payload) == {"id", "prompt", "options", "lesson", "lessonTitle"}


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


def test_the_seeded_interview_quiz_passes_the_check() -> None:
    assert check_quiz.main(["interviewing"]) == 0
