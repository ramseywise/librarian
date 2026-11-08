"""Chat-answer eval: judge parsing, grading math, the no-answer case, dry run, golden file.

Every client is the conftest FakeAnthropic. No test calls the Anthropic API.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evals import run_chat_eval as rce
from evals.run_chat_eval import ChatQuestion, parse_rubric_reply, run_chat_eval
from librarian.retrieval import corpus, embeddings

PAGE = "---\ntitle: {t}\ntags: [rag]\nsummary: s\nupdated: 2026-07-20\n---\n\n# {t}\n\n{b}\n"


@pytest.fixture()
def wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    wiki_dir = tmp_path / "wiki"
    (wiki_dir / "rag").mkdir(parents=True)
    (wiki_dir / "private").mkdir()
    for name in ("chunking", "reranking", "other"):
        (wiki_dir / "rag" / f"{name}.md").write_text(PAGE.format(t=name.title(), b="Body."))
    monkeypatch.setattr(corpus, "WIKI_DIR", wiki_dir)
    monkeypatch.setattr(corpus, "PRIVATE_DIR", wiki_dir / "private")
    monkeypatch.setattr(corpus, "DB_PATH", tmp_path / ".idx.duckdb")
    monkeypatch.setattr(embeddings, "HAS_EMBEDDINGS", False)
    return wiki_dir


@pytest.mark.unit
@pytest.mark.parametrize(
    ("reply", "ok"),
    [
        ('{"scores": [1, 0.5], "rationale": "r"}', True),
        ('```json\n{"scores": [0, 1]}\n```', True),
        ('{"scores": [1]}', False),  # wrong length
        ('{"scores": [1, 2]}', False),  # out of range
        ('{"scores": [true, 1]}', False),
        ('{"scores": "1,1"}', False),
        ("nothing", False),
    ],
)
def test_parse_rubric_reply(reply: str, ok: bool) -> None:
    scores, _ = parse_rubric_reply(reply, 2)
    assert (scores is not None) is ok


@pytest.mark.unit
async def test_grading_math_precision_no_answer_and_unparsed_judge(
    wiki: Path, fake_anthropic: type
) -> None:
    t = fake_anthropic
    client = t(
        turns=[
            # q1: reads chunking and other, cites both; only chunking is expected
            t.tool_turn(
                ("read_page", {"page_id": "chunking"}), ("read_page", {"page_id": "other"})
            ),
            t.text_turn("A [page:chunking] and [page:other]."),
            # q2: cites a page it never read (ungrounded)
            t.text_turn("B [page:reranking]."),
            # q3 (no answer): abstains
            t.text_turn("The wiki does not cover this."),
            # q4 (no answer): invents a citation after reading
            t.tool_turn(("read_page", {"page_id": "other"})),
            t.text_turn("Made up [page:other]."),
        ],
        replies=[
            '{"scores": [1, 0.5], "rationale": "ok"}',
            '{"scores": [0, 0], "rationale": "bad"}',
            '{"scores": [1, 1], "rationale": "abstained"}',
            "garbled",
        ],
    )
    qs = [
        ChatQuestion("q1", "one?", ["chunking"], ["l1", "l2"]),
        ChatQuestion("q2", "two?", ["reranking"], ["l1", "l2"]),
        ChatQuestion("q3", "none?", [], ["says it is uncovered", "no invention"]),
        ChatQuestion("q4", "none2?", [], ["says it is uncovered", "no invention"]),
    ]
    report = await run_chat_eval(
        qs, client=client, model="claude-sonnet-5-5", judge_model="claude-sonnet-5-5"
    )
    r1, r2, r3, r4 = report.results
    assert r1.citation_precision == 0.5 and r1.cited_recall == 1.0 and r1.grounded
    assert r2.citation_precision == 1.0 and not r2.grounded and r2.ungrounded == ["reranking"]
    assert r3.citation_precision is None and r3.cited_recall is None and not r3.cited
    assert r4.citation_precision is None and r4.cited == ["other"]
    assert r1.rubric_score == 0.75 and r4.rubric_score is None

    s = report.summary()
    assert s["n"] == 4 and s["n_answerable"] == 2 and s["n_no_answer"] == 2
    assert s["grounding"] == 0.75
    assert s["citation_precision"] == pytest.approx(0.75) and s["n_precision"] == 2
    assert s["cited_recall"] == pytest.approx(1.0)
    assert s["rubric_score"] == pytest.approx((0.75 + 0 + 1) / 3) and s["n_judged"] == 3
    assert s["no_answer_clean"] == 0.5
    assert "Grounding" in str(report)
    assert {c["model"] for c in client.stream_calls} == {"claude-sonnet-5-5"}
    # The judge saw the streamed answer and the numbered rubric.
    sent = json.dumps(client.create_calls[0]["messages"])
    assert "A [page:chunking]" in sent and "1. l1" in sent
    lines = (corpus.LOGS_DIR / "agent.jsonl").read_text().splitlines()
    assert {json.loads(x)["source"] for x in lines} == {"eval"}


@pytest.mark.unit
def test_dry_run_makes_no_client_and_no_api_calls(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    import anthropic

    def boom(*a: object, **k: object) -> None:
        raise AssertionError("dry run must not build a client")

    monkeypatch.setattr(anthropic, "AsyncAnthropic", boom)
    monkeypatch.setattr(rce, "BASELINES", tmp_path / "baselines")
    assert rce.main(["--dry-run", "--limit", "3"]) == 0
    out = capsys.readouterr().out
    assert "DRY RUN" in out and "Would run 3 questions" in out and "estimated cost" in out
    assert not (tmp_path / "baselines").exists()


@pytest.mark.unit
def test_estimate_cost_scales_with_questions_and_orders_typical_below_ceiling() -> None:
    one = rce.estimate_cost(1, "claude-sonnet-5-5", "claude-sonnet-5-5")
    forty = rce.estimate_cost(40, "claude-sonnet-5-5", "claude-sonnet-5-5")
    assert forty["typical"] == pytest.approx(40 * one["typical"])
    assert 0 < one["typical"] < one["ceiling"]
    assert rce.estimate_cost(1, "no-such-model", "claude-sonnet-5-5")["typical"] is None


@pytest.mark.unit
def test_warnings_are_warn_only_and_compare_with_baseline() -> None:
    s = {"grounding": 0.7, "citation_precision": 0.9, "cited_recall": None, "rubric_score": 0.8}
    base = {"summary": {"grounding": 0.95, "citation_precision": 0.9, "rubric_score": 0.8}}
    w = rce.warnings(s, base, reviewed=False)
    assert any("grounding fell" in x for x in w) and any("not human-reviewed" in x for x in w)
    assert not any("rubric_score" in x for x in w)
    assert any("no earlier" in x for x in rce.warnings(s, None, reviewed=True))


@pytest.mark.unit
async def test_main_saves_baseline_without_answer_text(
    wiki: Path, fake_anthropic: type, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import anthropic

    t = fake_anthropic
    client = t(
        turns=[
            t.tool_turn(("read_page", {"page_id": "chunking"})),
            t.text_turn("SECRET-ANSWER [page:chunking]"),
        ],
        replies=['{"scores": [1], "rationale": "ok"}'],
    )
    qs = [ChatQuestion("q1", "one?", ["chunking"], ["l1"])]
    report = await run_chat_eval(
        qs, client=client, model="claude-sonnet-5-5", judge_model="claude-sonnet-5-5"
    )
    monkeypatch.setattr(rce, "BASELINES", tmp_path / "baselines")
    path = rce.save_baseline(
        report, model="m", judge_model="j", dataset=rce.DEFAULT_DATASET, reviewed=False
    )
    text = path.read_text()
    assert "SECRET-ANSWER" not in text and json.loads(text)["golden_reviewed"] is False
    assert rce.latest_baseline(tmp_path / "baselines")["summary"]["n"] == 1
    assert anthropic  # imported only to prove nothing here needed the network


@pytest.mark.unit
def test_golden_chat_file_shape() -> None:
    questions, reviewed = rce.load_chat_golden()
    assert reviewed is False and 35 <= len(questions) <= 45
    assert len({q.id for q in questions}) == len(questions)
    assert any(not q.answerable for q in questions)
    assert any(len(q.expected_pages) > 1 for q in questions)
    assert all(q.rubric for q in questions)
    stems: dict[str, str] = {}
    for f in Path("data/wiki").rglob("*.md"):
        if "private" not in f.parts:
            stems[f.stem] = f.read_text(encoding="utf-8")[:800]
    for q in questions:
        for p in q.expected_pages:
            assert p in stems, f"{q.id}: {p} is not a public page"
            assert "tombstone" not in stems[p].split("---")[1], f"{q.id}: {p} is a tombstone"
