"""Grounding eval: metric math, abstention, the report-only gate, dry run, golden file.

Every client is the conftest FakeAnthropic. No test calls the Anthropic API.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evals import run_grounding_eval as rge
from evals.run_grounding_eval import GroundingQuestion, run_grounding_eval
from librarian.retrieval import corpus, embeddings

PAGE = "---\ntitle: {t}\ntags: [rag]\nsummary: s\nupdated: 2026-07-20\n---\n\n# {t}\n\n{b}\n"
BODY = "Split a page at its headings, so each chunk keeps one topic and its heading."


@pytest.fixture()
def wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    wiki_dir = tmp_path / "wiki"
    (wiki_dir / "rag").mkdir(parents=True)
    (wiki_dir / "private").mkdir()
    for name in ("chunking", "reranking", "other"):
        (wiki_dir / "rag" / f"{name}.md").write_text(PAGE.format(t=name.title(), b=BODY))
    monkeypatch.setattr(corpus, "WIKI_DIR", wiki_dir)
    monkeypatch.setattr(corpus, "PRIVATE_DIR", wiki_dir / "private")
    monkeypatch.setattr(corpus, "DB_PATH", tmp_path / ".idx.duckdb")
    monkeypatch.setattr(embeddings, "HAS_EMBEDDINGS", False)
    return wiki_dir


@pytest.mark.unit
async def test_metrics_over_grounded_ungrounded_abstaining_and_invented_answers(
    wiki: Path, fake_anthropic: type, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    t = fake_anthropic
    client = t(
        turns=[
            # q1: reads and cites the expected page; the claim is in the page
            t.tool_turn(("read_page", {"page_id": "chunking"})),
            t.text_turn("Split pages at their headings to keep one topic [page:chunking]."),
            # q2: reads one page, cites it (claim not in the page) and one it never read
            t.tool_turn(("read_page", {"page_id": "other"})),
            t.text_turn(
                "Windows of 512 tokens always win [page:other] and rerank after [page:reranking]."
            ),
            # q3 (unanswerable): abstains
            t.text_turn("The wiki does not cover this."),
            # q4 (unanswerable): cites a page anyway
            t.tool_turn(("read_page", {"page_id": "other"})),
            t.text_turn("Tighten every bolt to five newton metres [page:other]."),
        ]
    )
    qs = [
        GroundingQuestion("q1", "one?", ["chunking"]),
        GroundingQuestion("q2", "two?", ["reranking"]),
        GroundingQuestion("q3", "none?", []),
        GroundingQuestion("q4", "none2?", []),
    ]
    report = await run_grounding_eval(qs, client=client, model="claude-sonnet-5-5")
    r1, r2, r3, r4 = report.results
    assert r1.expected_cited is True and not r1.ungrounded
    assert r2.ungrounded == ["reranking"] and r2.expected_cited is True
    assert r3.cited == [] and r3.expected_cited is None
    assert r4.cited == ["other"] and not r4.answerable

    s = report.summary()
    assert (s["n"], s["n_answerable"], s["n_unanswerable"], s["n_citing"]) == (4, 2, 2, 3)
    assert s["all_citations_read"] == pytest.approx(2 / 3)  # q1 and q4 of the three citing
    assert s["ungrounded_citations"] == pytest.approx(1 / 4) and s["n_citations"] == 4
    assert s["abstention"] == 0.5
    assert s["expected_page_cited"] == 1.0
    # Pairs on read pages: q1 found, q2's [page:other] and q4's not.
    assert s["n_support_checked"] == 3 and s["claim_support"] == pytest.approx(1 / 3)
    assert s["n_judged"] == 0 and client.create_calls == []
    assert "Abstention" in str(report)

    lines = (corpus.LOGS_DIR / "agent.jsonl").read_text().splitlines()
    assert {json.loads(x)["source"] for x in lines} == {"eval"}

    # The baseline keeps counts and page ids, never the answer text.
    dataset = tmp_path / "golden.json"
    dataset.write_text("{}")
    monkeypatch.setattr(rge, "BASELINES", tmp_path / "baselines")
    saved = rge.save_baseline(report, model="m", dataset=dataset, reviewed=False).read_text()
    assert json.loads(saved)["summary"]["abstention"] == 0.5
    assert "newton" not in saved and "512 tokens" not in saved


@pytest.mark.unit
def test_summary_of_a_run_with_no_citations_has_no_rates() -> None:
    s = rge.GroundingReport([]).summary()
    assert s["all_citations_read"] is None and s["abstention"] is None
    assert s["claim_support"] is None and s["cost_usd"] is None


@pytest.mark.unit
def test_gate_is_report_only_until_a_threshold_is_set() -> None:
    # As shipped: no threshold, so nothing can fail.
    assert rge.report_only() and set(rge.THRESHOLDS.values()) == {None}
    bad = {"all_citations_read": 0.0, "ungrounded_citations": 1.0, "abstention": 0.0}
    assert rge.gate_failures(bad) == []

    floors = {"all_citations_read": 0.9, "ungrounded_citations": 0.1, "abstention": None}
    assert not rge.report_only(floors)
    failures = rge.gate_failures(bad, floors)
    assert len(failures) == 2
    assert any("below the floor" in f for f in failures)
    assert any("above the ceiling" in f for f in failures)
    # A metric with no value this run is not a failure.
    assert rge.gate_failures({"all_citations_read": None}, floors) == []


@pytest.mark.unit
def test_dry_run_builds_no_client_and_prints_a_cost(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    import anthropic

    def boom(*a: object, **k: object) -> None:
        raise AssertionError("dry run must not build a client")

    monkeypatch.setattr(anthropic, "AsyncAnthropic", boom)
    assert rge.main(["--dry-run", "--limit", "2", "--model", "claude-sonnet-5-5"]) == 0
    out = capsys.readouterr().out
    assert "DRY RUN" in out and "Would run 2 questions" in out and "typical" in out

    est = rge.estimate_cost(10, "claude-sonnet-5-5")
    assert est["typical"] is not None and est["typical"] < est["ceiling"]
    assert rge.estimate_cost(1, "no-such-model") == {"typical": None, "ceiling": None}


@pytest.mark.unit
def test_golden_file_is_public_only_and_has_unanswerable_questions() -> None:
    questions, reviewed = rge.load_golden()
    assert reviewed is False
    assert len({q.id for q in questions}) == len(questions)
    assert sum(not q.answerable for q in questions) >= 1
    assert sum(q.answerable for q in questions) >= 5
    # Every expected page is one public wiki page; nothing is seeded from private/.
    for q in questions:
        for page_id in q.expected_pages:
            matches = list(corpus.WIKI_DIR.rglob(f"{page_id}.md"))
            assert len(matches) == 1, page_id
            assert not corpus.is_private(matches[0]), q.id
