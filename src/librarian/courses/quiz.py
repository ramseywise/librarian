"""Multiple-choice questions: the `_quiz.md` file of a module, loaded and checked.

Same shape as `_flashcards.md`: frontmatter `questions: [{prompt, options, answer, explanation,
lesson?, id?}, ...]` in `<course>/<module>/_quiz.md`. `answer` is the text of one of `options`
(so the viewer may shuffle them), `lesson` is a lesson id in the module, and `id` is optional:
without it the id is a hash of the prompt, so rewording a prompt makes a new question. Give an
`id` to a question whose prompt you expect to edit; ids are what attempts and the Leitner queue
are keyed on.

The catalog loads leniently (a malformed question is dropped, with a warning, so one typo cannot
hide a module's quiz); `check` is strict and is what `librarian courses check quiz` reports.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import frontmatter

from librarian.log_config import get_logger

log = get_logger(__name__)

QUIZ_FILE = "_quiz.md"
ID_HASH_CHARS = 10
MIN_OPTIONS = 2
_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


@dataclass(frozen=True)
class Question:
    id: str
    prompt: str
    options: tuple[str, ...]
    answer: str
    explanation: str = ""
    lesson: str | None = None


def prompt_id(prompt: str) -> str:
    return hashlib.sha256(prompt.strip().encode("utf-8")).hexdigest()[:ID_HASH_CHARS]


def question_key(quiz_id: str, qid: str) -> str:
    """Identity of a question in the attempts store and the Leitner queue.

    Built from the module (first two segments of the quiz id, as card keys are), so the module
    quiz and a lesson's quiz share one schedule. A `private/` prefix is ignored.
    """
    return f"{'/'.join(quiz_id.removeprefix('private/').split('/')[:2])}:q:{qid}"


def _text(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def parse_question(
    raw: object, lessons: set[str] | None = None
) -> tuple[Question | None, list[str]]:
    """One entry of `questions:` as a Question, and the problems found. No Question when unusable.

    With `lessons` given, a `lesson` outside it is a problem; without it the field is not checked.
    """
    if not isinstance(raw, dict):
        return None, ["not a mapping"]
    problems: list[str] = []
    prompt = _text(raw.get("prompt"))
    if not prompt:
        problems.append("no prompt")
    options_raw = raw.get("options")
    options = [_text(o) for o in options_raw] if isinstance(options_raw, list) else []
    if len(options) < MIN_OPTIONS or not all(options):
        problems.append(f"options must be {MIN_OPTIONS}+ non-empty strings")
    elif len(set(options)) != len(options):
        problems.append("duplicate options")
    answer = _text(raw.get("answer"))
    if options and answer not in options:
        problems.append("answer is not one of the options")
    qid = _text(raw.get("id")) or (prompt_id(prompt) if prompt else "")
    if qid and not _ID_RE.match(qid):
        problems.append(f"id {qid!r} has characters outside A-Z a-z 0-9 . _ -")
    lesson = _text(raw.get("lesson")) or None
    if lesson and lessons is not None and lesson not in lessons:
        problems.append(f"lesson {lesson!r} is not in this module")
    if problems:
        return None, problems
    return Question(qid, prompt, tuple(options), answer, _text(raw.get("explanation")), lesson), []


def _raw_questions(path: Path) -> list[object]:
    if not path.is_file():
        return []
    try:
        raw = frontmatter.load(path).metadata.get("questions")
    except (OSError, ValueError) as e:  # ValueError covers YAML errors
        log.warning("quiz.unreadable", file=path.name, error=str(e))
        return []
    return raw if isinstance(raw, list) else []


def load(path: Path, lessons: set[str]) -> list[Question]:
    """The well-formed questions of one `_quiz.md`. A `lesson` not in this module falls back to the
    module quiz, as a flashcard's does; a repeated id keeps the first question."""
    out: list[Question] = []
    seen: set[str] = set()
    for i, raw in enumerate(_raw_questions(path)):
        q, problems = parse_question(raw, None)
        if q is None:
            log.warning("quiz.question_skipped", file=path.name, index=i, problems=problems)
            continue
        if q.id in seen:
            log.warning("quiz.duplicate_id", file=path.name, index=i, id=q.id)
            continue
        seen.add(q.id)
        out.append(q if not q.lesson or q.lesson in lessons else replace(q, lesson=None))
    return out


def problems_in(path: Path, lessons: set[str]) -> list[str]:
    """Every problem in one `_quiz.md`, as 'question N (id): problem' lines."""
    raw = _raw_questions(path)
    if path.is_file() and not raw:
        return ["no `questions:` list in the frontmatter"]
    out: list[str] = []
    seen: dict[str, int] = {}
    for i, item in enumerate(raw, 1):
        q, found = parse_question(item, lessons)
        out += [f"question {i}: {p}" for p in found]
        if q is not None:
            if q.id in seen:
                out.append(f"question {i}: id {q.id!r} repeats question {seen[q.id]}")
            seen.setdefault(q.id, i)
    return out


def public_payload(q: Question, lesson_title: str | None) -> dict[str, Any]:
    """What a quiz sends the client: the question, never the key or the explanation."""
    return {
        "id": q.id,
        "prompt": q.prompt,
        "options": list(q.options),
        "lesson": q.lesson,
        "lessonTitle": lesson_title,
    }
