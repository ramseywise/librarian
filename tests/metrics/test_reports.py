"""Experiment comparison, product metrics and the release check, over a temp log and database."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import Engine, create_engine, insert

from librarian.db import tables
from librarian.metrics import cli, reports
from librarian.metrics.data import feedback_table, parse_experiment
from librarian.retrieval import corpus

NOW = datetime(2026, 11, 8, 12, 0, tzinfo=UTC)


@pytest.fixture()
def engine(tmp_path: Path) -> Engine:
    eng = create_engine(f"sqlite:///{tmp_path / 'm.db'}")
    tables.metadata.create_all(eng)
    feedback_table().create(eng, checkfirst=True)
    return eng


def _write_log(rows: list[dict]) -> None:
    corpus.LOGS_DIR.mkdir(exist_ok=True)
    (corpus.LOGS_DIR / "agent.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))


def _row(
    i: int,
    *,
    exp: str = "",
    release: str = "r1",
    user: str = "u1",
    grounded: bool = True,
    latency: int = 1000,
    cost: float | None = 0.01,
    age_days: float = 1.0,
    **extra: object,
) -> dict:
    row: dict = {
        "ts": (NOW - timedelta(days=age_days, seconds=i)).isoformat(),
        "answer_id": f"a{i}",
        "experiment": exp,
        "release": release,
        "user_id": user,
        "pages_read": ["p1", "p2"],
        "cited": ["p1"],
        "ungrounded": [] if grounded else ["ghost"],
        "latency_ms": latency,
        "source": "chat",
        **extra,
    }
    if cost is not None:
        row["cost_usd"] = cost
    return row


def _rate(engine: Engine, answer_id: str, rating: int) -> None:
    with engine.begin() as conn:
        conn.execute(
            insert(feedback_table()).values(
                id=uuid.uuid4().hex,
                user_id="u1",
                ts=NOW,
                kind="answer",
                target=answer_id,
                rating=rating,
            )
        )


def test_parse_experiment() -> None:
    assert parse_experiment("ranking=hybrid-union;prompt=v2") == {
        "ranking": "hybrid-union",
        "prompt": "v2",
    }
    assert parse_experiment("") == {} and parse_experiment(None) == {}


def test_compare_per_variant_with_n_and_too_few_note(engine: Engine) -> None:
    rows = [_row(i, exp="ranking=base", latency=100 * (i + 1)) for i in range(40)]
    rows += [_row(100 + i, exp="ranking=hybrid-union", grounded=i % 2 == 0) for i in range(5)]
    rows += [_row(200, exp="prompt=v2")]  # other experiment: not a variant of ranking
    rows += [{k: v for k, v in _row(300).items() if k not in ("experiment", "release")}]  # old row
    _write_log(rows)
    for i in range(10):
        _rate(engine, f"a{i}", 1 if i < 8 else -1)

    cmp = reports.compare("ranking", engine=engine)
    base, hybrid = cmp.variants
    assert (base.label, base.n) == ("base", 40)
    assert (hybrid.label, hybrid.n) == ("hybrid-union", 5)
    assert base.grounding_rate == 1.0 and hybrid.grounding_rate == pytest.approx(0.6)
    assert base.n_rated == 10 and base.rating_rate == pytest.approx(0.25)
    assert base.mean_rating == pytest.approx(0.6)
    assert base.latency_p50_ms == pytest.approx(2050)
    assert base.pages_read_mean == 2 and base.cost_per_answer == pytest.approx(0.01)
    assert cmp.too_few == ["hybrid-union"] and not cmp.comparable
    text = cmp.render()
    assert "Too few to compare" in text and "hybrid-union" in text
    assert cmp.to_json()["comparable"] is False


def test_compare_is_comparable_at_thirty_each(engine: Engine) -> None:
    _write_log(
        [_row(i, exp="ranking=a") for i in range(30)]
        + [_row(50 + i, exp="ranking=b") for i in range(30)]
    )
    cmp = reports.compare("ranking", engine=engine)
    assert cmp.comparable and "Too few" not in cmp.render()


def test_compare_since_and_eval_traffic_excluded(engine: Engine) -> None:
    _write_log(
        [
            _row(1, exp="ranking=a", age_days=40),
            _row(2, exp="ranking=a"),
            _row(3, exp="ranking=a", source="eval"),
        ]
    )
    cmp = reports.compare("ranking", engine=engine, since=NOW - timedelta(days=7))
    assert cmp.variants[0].n == 1


def test_missing_feedback_table_reads_as_no_ratings(tmp_path: Path) -> None:
    bare = create_engine(f"sqlite:///{tmp_path / 'bare.db'}")
    _write_log([_row(1, exp="ranking=a")])
    cmp = reports.compare("ranking", engine=bare)
    assert cmp.variants[0].n_rated == 0 and cmp.variants[0].rating_rate == 0


def test_cost_computed_from_usage_when_not_logged(engine: Engine) -> None:
    row = _row(
        1,
        exp="ranking=a",
        cost=None,
        model="claude-sonnet-5-5",
        usage={"input": 1_000_000, "output": 0},
    )
    _write_log([row])
    assert reports.compare("ranking", engine=engine).variants[0].cost_per_answer == pytest.approx(
        2.0
    )


def test_product_groups_and_spend_distribution_names_nobody(engine: Engine) -> None:
    rows = [_row(i, release="r1", user=f"user-{i % 3}", cost=0.01 * (i % 3 + 1)) for i in range(9)]
    rows += [_row(50, release="r2", age_days=60)]  # outside the window
    _write_log(rows)
    with engine.begin() as conn:
        conn.execute(
            insert(tables.attempts),
            [
                {
                    "user_id": "u",
                    "ts": NOW - timedelta(days=1),
                    "kind": "flashcard",
                    "item": f"c{i}",
                    "scope": "s",
                    "result": "knew",
                    "event_key": f"k{i}",
                }
                for i in range(3)
            ],
        )
        conn.execute(
            insert(tables.progress),
            [
                {
                    "user_id": "u",
                    "lesson_id": "l1",
                    "state": "done",
                    "updated_at": NOW - timedelta(days=2),
                },
                {"user_id": "u", "lesson_id": "l2", "state": "opened", "updated_at": NOW},
            ],
        )
    rep = reports.product(engine=engine, days=30, by="release", now=NOW)
    (g,) = rep.groups
    assert g["label"] == "r1" and g["n"] == 9
    assert g["answers_per_day"] == pytest.approx(0.3)
    assert g["spend_per_user"]["users"] == 3
    assert g["spend_per_user"]["max"] == pytest.approx(0.09)
    assert rep.study["flashcards_reviewed"] == 3 and rep.study["lessons_done"] == 1
    assert "user-0" not in json.dumps(rep.to_json()) and "user-0" not in rep.render()


def test_product_by_experiment(engine: Engine) -> None:
    _write_log([_row(1, exp="ranking=a"), _row(2, exp="")])
    labels = [g["label"] for g in reports.product(engine=engine, by="experiment", now=NOW).groups]
    assert labels == ["(none)", "ranking=a"]


def _two_releases(prev_grounded: float, cur_grounded: float, n: int = 40) -> list[dict]:
    rows = []
    for i in range(n):
        rows.append(_row(i, release="old", age_days=5, grounded=i < prev_grounded * n))
        rows.append(_row(1000 + i, release="new", age_days=1, grounded=i < cur_grounded * n))
    return rows


def test_check_release_fails_on_grounding_drop(engine: Engine) -> None:
    _write_log(_two_releases(0.9, 0.7))
    chk = reports.check_release(engine=engine, now=NOW)
    assert not chk.ok and "grounding fell 20 points" in chk.failures[0]


def test_check_release_fails_on_down_rating_rise(engine: Engine) -> None:
    _write_log(_two_releases(0.9, 0.9))
    for i in range(40):
        _rate(engine, f"a{1000 + i}", -1 if i < 20 else 1)
        _rate(engine, f"a{i}", 1)
    chk = reports.check_release(engine=engine, now=NOW)
    assert not chk.ok and "down-rating rate rose 50 points" in chk.failures[0]


def test_check_release_ok_and_small_n_not_judged(engine: Engine) -> None:
    _write_log(_two_releases(0.9, 0.85))
    assert reports.check_release(engine=engine, now=NOW).ok
    _write_log(_two_releases(0.9, 0.1, n=10))
    chk = reports.check_release(engine=engine, now=NOW)
    assert chk.ok and "not judged" in chk.notes[0]


def test_check_release_cli_exit_code(
    engine: Engine, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli, "get_engine", lambda: engine)
    now = datetime.now(UTC)
    rows = _two_releases(0.9, 0.5)
    shift = now - NOW
    for r in rows:
        r["ts"] = (datetime.fromisoformat(r["ts"]) + shift).isoformat()
    _write_log(rows)
    assert cli.main(["metrics", "check-release"]) == 1
    assert "FAIL" in capsys.readouterr().out
    assert cli.main(["eval", "compare", "--experiment", "ranking", "--json"]) == 0
