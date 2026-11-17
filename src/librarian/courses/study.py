"""The study loop over the attempts store: quizzes, drill runs and the study home.

- `quiz_deck(user, id)` and `answer_question(user, id, qid, choice)`: a module's or lesson's
  quiz (multiple choice and worked problems). The key stays on the server; a wrong answer is a miss in the Leitner queue
  (`leitner.py`), the same queue the flashcards use.
- `record_drill(user, lesson_id, result)`: a drill run done in the app.
- `home(user)`: what to do next, from the user's attempts: cards and questions due, the next drill
  for the weakest track, and the lecture for the module being studied.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date
from typing import Any

from librarian.accounts import User
from librarian.courses import attempts, catalog, leitner, quiz, slides

DRILL_ORDER = {"easy": 0, "medium": 1, "hard": 2}


# ── quizzes ────────────────────────────────────────────────────────────────


def _scheduled_quiz(
    qz: dict[str, Any], states: dict[str, leitner.CardState], today: date
) -> dict[str, Any]:
    lessons = catalog.catalog().lessons
    rows = []
    for q in qz["questions"]:
        state = states.get(quiz.question_key(qz["id"], q.id))
        rows.append(
            quiz.public_payload(q, lessons[q.lesson].title if q.lesson in lessons else None)
            | {
                "box": state.box if state else None,
                "dueOn": state.due_on.isoformat() if state else None,
                "status": leitner.status_of(state, today),
            }
        )
    counts = Counter(r["status"] for r in rows)
    return {
        "id": qz["id"],
        "title": qz["title"],
        "course": qz["course"],
        "questions": rows,
        "dueCount": counts["due"],
        "newCount": counts["new"],
    }


def quiz_deck(user: User, quiz_id: str) -> dict[str, Any] | None:
    """A module's (`<course>/<module>`) or lesson's quiz, with `user`'s schedule for each question. No answers."""
    qz = catalog.catalog().quizzes.get(quiz_id)
    if not qz:
        return None
    return _scheduled_quiz(qz, leitner.load_states(user), leitner.today(user))


def answer_question(
    user: User, quiz_id: str, qid: str, choice: str, *, assisted: bool = False
) -> dict[str, Any] | None:
    """Grade one answer and store it. None for an unknown quiz or question.

    `assisted` (a hint or the solution was used first) stores a miss whatever the answer; the
    reply still says whether the answer was right. Raises ValueError when `choice` is not one of
    the question's options, or not a number for a worked problem.
    """
    qz = catalog.catalog().quizzes.get(quiz_id)
    question = next((q for q in qz["questions"] if q.id == qid), None) if qz else None
    if qz is None or question is None:
        return None
    correct = quiz.is_correct(question, choice)
    logged = attempts.record(
        user.id,
        "mcq",
        quiz.question_key(quiz_id, question.id),
        quiz_id,
        "correct" if correct and not assisted else "wrong",
        payload={"choice": choice, "lesson": question.lesson}
        | ({"assisted": True} if assisted else {}),
    )
    return {
        "correct": correct,
        "answer": question.answer,
        "explanation": question.explanation,
        "logged": logged,
    }


def reveal_question(user: User, quiz_id: str, qid: str, what: str) -> dict[str, Any] | None:
    """Give a worked problem's `hint` or its `solution`, and store a miss: help counts as not knowing it.

    None for an unknown quiz or question, or a hint the question does not have. Raises ValueError for
    anything but a hint or the solution, and for a question that is not a worked problem.
    """
    if what not in ("hint", "solution"):
        raise ValueError("what must be 'hint' or 'solution'")
    qz = catalog.catalog().quizzes.get(quiz_id)
    question = next((q for q in qz["questions"] if q.id == qid), None) if qz else None
    if question is None:
        return None
    if not question.worked:
        raise ValueError("only a worked problem has a hint or a solution to show")
    if what == "hint" and not question.hint:
        return None
    logged = attempts.record(
        user.id,
        "mcq",
        quiz.question_key(quiz_id, question.id),
        quiz_id,
        "wrong",
        payload={"revealed": what, "lesson": question.lesson},
    )
    body = (
        {"hint": question.hint}
        if what == "hint"
        else {
            "answer": question.answer,
            "explanation": question.explanation,
        }
    )
    return body | {"logged": logged}


def quizzes_due(user: User) -> list[dict[str, Any]]:
    """Per module quiz: `user`'s questions due and never seen, for those with either."""
    states, today = leitner.load_states(user), leitner.today(user)
    out = []
    for quiz_id, qz in catalog.catalog().quizzes.items():
        if quiz_id.count("/") != 1:
            continue
        counted = _scheduled_quiz(qz, states, today)
        if counted["dueCount"] or counted["newCount"]:
            out.append(
                {
                    "quiz": quiz_id,
                    "title": qz["title"],
                    "due": counted["dueCount"],
                    "new": counted["newCount"],
                }
            )
    out.sort(key=lambda m: (-m["due"], m["quiz"]))
    return out


def level_progress(user: User) -> dict[str, dict[str, dict[str, int]]]:
    """`user`'s progress on each module's three levels, from the attempts store.

    `{<course>/<module>: {choice|cards|worked: {total, right, redo}}}`, only for levels the module
    has. An item counts as right when its latest attempt was good and as to redo when its latest was
    not; never attempted is neither, so `right + redo <= total`.
    """
    cat = catalog.catalog()
    good: dict[str, bool] = {}
    for a in attempts.attempts(
        user.id, leitner.SCHEDULED_KINDS
    ):  # oldest first, so the latest wins
        good[a.item] = a.good

    def level(keys: list[str]) -> dict[str, int]:
        seen = [good[k] for k in keys if k in good]
        return {"total": len(keys), "right": sum(seen), "redo": len(seen) - sum(seen)}

    out: dict[str, dict[str, dict[str, int]]] = {}
    for module_id, qz in cat.quizzes.items():
        if module_id.count("/") != 1:
            continue
        keys = lambda worked, qz=qz, module_id=module_id: [  # noqa: E731
            quiz.question_key(module_id, q.id) for q in qz["questions"] if q.worked == worked
        ]
        for name, worked in (("choice", False), ("worked", True)):
            if ks := keys(worked):
                out.setdefault(module_id, {})[name] = level(ks)
    for module_id, deck in cat.decks.items():
        if module_id.count("/") == 1 and deck["cards"]:
            out.setdefault(module_id, {})["cards"] = level(
                [leitner.card_key(module_id, c["front"]) for c in deck["cards"]]
            )
    return out


# ── drills ─────────────────────────────────────────────────────────────────


def record_drill(user: User, lesson_id: str, result: str) -> bool | None:
    """Store one drill run done in the app. None when `lesson_id` is not a drill."""
    rec = catalog.catalog().lessons.get(lesson_id)
    if rec is None or rec.kind != "drill":
        return None
    return attempts.record(
        user.id,
        "drill",
        lesson_id,
        lesson_id,
        result,
        payload={"track": rec.drill.get("track"), "difficulty": rec.drill.get("difficulty")},
    )


def next_drill(user: User) -> dict[str, Any] | None:
    """The drill for `user` to do next: one from the track with the lowest pass rate in their attempts.

    A track's pass rate counts each drill once, by its latest run in the app. Within the track the
    drills last failed or revealed come first, then those never attempted (in the app or in an
    imported drill log), easiest first. With no attempts at all it is the first drill by difficulty.
    """
    cat = catalog.catalog()
    drills = [r for r in cat.lessons.values() if r.kind == "drill"]
    if not drills:
        return None
    latest: dict[str, str] = {}
    for a in attempts.attempts(user.id, ["drill"]):
        latest[a.item] = a.result
    by_track: dict[str, list[bool]] = defaultdict(list)
    for r in drills:
        if r.id in latest:
            by_track[str(r.drill.get("track", ""))].append(latest[r.id] == "pass")
    in_log = set(catalog.drill_history(user))

    def rank(r: catalog.LessonRec) -> tuple[int, int]:
        state = latest.get(r.id)
        if state in ("fail", "revealed"):
            stage = 0
        elif state is None and _slug(r.id) not in in_log:
            stage = 1
        else:
            stage = 2  # passed, or attempted in an imported drill log
        return stage, DRILL_ORDER.get(str(r.drill.get("difficulty")), 3)

    tracks = sorted(by_track, key=lambda t: (sum(by_track[t]) / len(by_track[t]), t))
    for track in [*tracks, None]:
        pool = [r for r in drills if track is None or str(r.drill.get("track", "")) == track]
        pool = [r for r in pool if rank(r)[0] < 2]
        if pool:
            r = min(pool, key=rank)
            return catalog.outline(r) | {
                "course": r.course,
                "track": r.drill.get("track"),
                "reason": "weakest track" if track else "first drill",
            }
    return None


def _slug(lesson_id: str) -> str:
    return lesson_id.rsplit("/", 1)[-1]


# ── the home ───────────────────────────────────────────────────────────────


def _current_module(user: User, modules: dict[str, dict[str, Any]], due: list[str]) -> str | None:
    """The module `user` is studying: where their latest attempt was, else the first with work
    due, else the first module with slides."""
    with_slides = [m for m in modules if slides.module_decks(m)]
    for a in reversed(attempts.attempts(user.id)):
        if a.module in with_slides:
            return a.module
    for m in due:
        if m in with_slides:
            return m
    return with_slides[0] if with_slides else None


def home(user: User) -> dict[str, Any]:
    """`user`'s study queue: what is due, the next drill and the lecture for the current module."""
    cat = catalog.catalog()
    modules = {
        f"{c['id']}/{m['id']}": m | {"course": c["id"]} for c in cat.courses for m in c["modules"]
    }
    cards = catalog.flashcards_due(user)
    questions = quizzes_due(user)
    queue: dict[str, dict[str, Any]] = {}
    for m in cards["modules"]:
        queue.setdefault(m["deck"], _row(m["deck"], m["title"]))["cards"] = {
            "due": m["due"],
            "new": m["new"],
        }
    for m in questions:
        queue.setdefault(m["quiz"], _row(m["quiz"], m["title"]))["questions"] = {
            "due": m["due"],
            "new": m["new"],
        }
    rows = sorted(
        queue.values(),
        key=lambda r: (-(r["cards"]["due"] + r["questions"]["due"]), r["module"]),
    )
    current = _current_module(user, modules, [r["module"] for r in rows])
    decks = slides.module_decks(current) if current else []
    return {
        "today": cards["today"],
        "due": cards["due"] + sum(q["due"] for q in questions),
        "new": cards["new"] + sum(q["new"] for q in questions),
        "modules": rows,
        "nextDrill": next_drill(user),
        "lecture": (
            {"module": current, "title": modules[current]["title"], "decks": decks}
            if current
            else None
        ),
    }


def _row(module: str, title: str) -> dict[str, Any]:
    zero = {"due": 0, "new": 0}
    return {"module": module, "title": title, "cards": dict(zero), "questions": dict(zero)}
