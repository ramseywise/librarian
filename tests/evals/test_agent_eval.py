"""Agent eval mode: AgentGrader, the LLM judge's parsing, and run_agent_eval end to end.

Every client here is the conftest FakeAnthropic — no test calls the Anthropic API.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.mcp_server import server
from evals.graders import (
    AgentGrader,
    AgentRun,
    GoldenEntry,
    LLMJudgeGrader,
    parse_judge_reply,
)
from evals.run_eval import run_agent_eval


def _entry(
    id: str = "e1",
    query: str = "How should I chunk?",
    source_pages: list[str] | None = None,
) -> GoldenEntry:
    return GoldenEntry(
        id=id,
        category="retrieval",
        query=query,
        expected_answer="Chunk by headings.",
        source_pages=source_pages or ["data/wiki/rag/chunking.md", "data/wiki/rag/Reranking.md"],
        difficulty="easy",
    )


def _run(read: list[str], cited: list[str]) -> AgentRun:
    return AgentRun(
        answer="x",
        pages_read=read,
        cited=cited,
        ungrounded=[c for c in cited if c not in read],
    )


# ---------------------------------------------------------------------------
# AgentGrader
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_agent_grader_full_marks() -> None:
    r = AgentGrader().grade_entry(
        _entry(), _run(["chunking", "reranking"], ["chunking", "reranking"])
    )
    assert r.read_recall == 1.0
    assert r.cited_recall == 1.0
    assert r.grounded and r.has_citation
    assert r.expected_ids == ["chunking", "reranking"]  # stems, lowercased


@pytest.mark.unit
def test_agent_grader_partial_and_ungrounded() -> None:
    r = AgentGrader().grade_entry(_entry(), _run(["chunking"], ["chunking", "reranking"]))
    assert r.read_recall == 0.5
    assert r.cited_recall == 1.0
    assert not r.grounded
    assert r.ungrounded == ["reranking"]


@pytest.mark.unit
def test_agent_grader_no_citations() -> None:
    r = AgentGrader().grade_entry(_entry(), _run(["chunking", "reranking"], []))
    assert r.read_recall == 1.0
    assert r.cited_recall == 0.0
    assert r.grounded  # nothing cited, so nothing ungrounded
    assert not r.has_citation


@pytest.mark.unit
def test_agent_grader_batch_means() -> None:
    entries = [_entry("a"), _entry("b")]
    runs = [
        _run(["chunking", "reranking"], ["chunking"]),
        _run([], ["ghost"]),
    ]
    results, means = AgentGrader().grade_batch(entries, runs)
    assert [r.entry_id for r in results] == ["a", "b"]
    assert means["read_recall"] == pytest.approx(0.5)
    assert means["cited_recall"] == pytest.approx(0.25)
    assert means["grounded_rate"] == pytest.approx(0.5)
    assert means["citation_rate"] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Judge
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    ("reply", "score"),
    [
        ('{"score": 4, "rationale": "close"}', 4),
        ('Here you go:\n```json\n{"score": 5, "rationale": "exact"}\n```', 5),
        ('{"score": 0, "rationale": "x"}', None),
        ('{"score": 6, "rationale": "x"}', None),
        ('{"score": "4", "rationale": "x"}', None),
        ('{"score": true, "rationale": "x"}', None),
        ('{"score": 3.5}', None),
        ("no json at all", None),
        ("{not valid json}", None),
    ],
)
def test_parse_judge_reply(reply: str, score: int | None) -> None:
    got, rationale = parse_judge_reply(reply)
    assert got == score
    if score is None:
        assert rationale == reply.strip()


@pytest.mark.unit
async def test_llm_judge_grader_sends_both_answers(fake_anthropic: type) -> None:
    client = fake_anthropic(replies=['{"score": 3, "rationale": "misses reranking"}'])
    result = await LLMJudgeGrader(client, "judge-model").grade_entry(_entry(), "CANDIDATE")
    assert (result.entry_id, result.score, result.rationale) == ("e1", 3, "misses reranking")
    (call,) = client.create_calls
    assert call["model"] == "judge-model"
    sent = json.dumps(call["messages"])
    assert "CANDIDATE" in sent and "Chunk by headings." in sent


# ---------------------------------------------------------------------------
# run_agent_eval end to end
# ---------------------------------------------------------------------------

PAGE = "---\ntitle: {t}\ntags: [rag]\nsummary: s\nupdated: 2026-07-20\n---\n\n# {t}\n\n{b}\n"


@pytest.fixture()
def wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    wiki_dir = tmp_path / "wiki"
    (wiki_dir / "rag").mkdir(parents=True)
    (wiki_dir / "private").mkdir()
    (wiki_dir / "rag" / "chunking.md").write_text(PAGE.format(t="Chunking", b="By headings."))
    (wiki_dir / "rag" / "reranking.md").write_text(PAGE.format(t="Reranking", b="Rerank."))
    monkeypatch.setattr(server, "WIKI_DIR", wiki_dir)
    monkeypatch.setattr(server, "PRIVATE_DIR", wiki_dir / "private")
    monkeypatch.setattr(server, "DB_PATH", tmp_path / ".idx.duckdb")
    monkeypatch.setattr(server, "HAS_EMBEDDINGS", False)
    return wiki_dir


@pytest.mark.unit
async def test_run_agent_eval_end_to_end(wiki: Path, fake_anthropic: type) -> None:
    t = fake_anthropic
    client = t(
        turns=[
            # entry 1: reads chunking, cites it and an unread page
            t.tool_turn(("read_page", {"page_id": "chunking"})),
            t.text_turn("By headings [page:chunking], then [page:reranking]."),
            # entry 2: answers from nothing
            t.text_turn("No idea."),
        ],
        replies=['{"score": 4, "rationale": "ok"}', "garbled"],
    )
    entries = [_entry("e1"), _entry("e2")]
    judge = LLMJudgeGrader(client, "judge-model")
    report = await run_agent_eval(entries, client=client, model="agent-model", judge=judge)

    assert report.n_entries == 2
    r1, r2 = report.results
    assert r1.pages_read == ["chunking"]
    assert r1.ungrounded == ["reranking"]
    assert r1.read_recall == 0.5 and r1.cited_recall == 1.0
    assert r2.read_recall == 0.0 and not r2.has_citation
    assert report.grounded_rate == 0.5
    assert report.citation_rate == 0.5
    # The unparseable judge reply is excluded from the mean, not scored 0.
    assert report.mean_judge_score == 4.0 and report.n_judged == 1
    assert {c["model"] for c in client.stream_calls} == {"agent-model"}
    # The judge saw the answer the agent actually streamed.
    assert "By headings [page:chunking]" in json.dumps(client.create_calls[0]["messages"])
    assert "no floor" in str(report)

    lines = (server.LOGS_DIR / "agent.jsonl").read_text().splitlines()
    assert [json.loads(x)["source"] for x in lines] == ["eval", "eval"]


@pytest.mark.unit
async def test_run_agent_eval_without_judge(wiki: Path, fake_anthropic: type) -> None:
    client = fake_anthropic(turns=[fake_anthropic.text_turn("x")])
    report = await run_agent_eval([_entry()], client=client)
    assert report.mean_judge_score is None
    assert report.judge_results == []
    assert client.create_calls == []
