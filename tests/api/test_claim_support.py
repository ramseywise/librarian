"""Claim support: a cited page that was read must also hold the claim beside its citation.

The deterministic quote/overlap check always runs; the judge only behind
`Settings.claim_judge`, and its usage is reported like any other model turn.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from librarian.agent import loop as agent
from librarian.agent import support
from librarian.config import get_settings
from librarian.pricing import TokenUsage
from librarian.retrieval import corpus, embeddings

PAGE = "---\ntitle: {t}\ntags: [rag]\nsummary: s\nupdated: 2026-07-20\n---\n\n# {t}\n\n{b}\n"
CHUNKING = "Split a page at its headings, so each chunk keeps one topic and its heading."
RERANKING = "A cross-encoder scores each query and passage pair together."

GROUNDED = "Split pages at their headings so a chunk keeps one topic [page:chunking]."
UNFOUNDED = "Sentence windows of 512 tokens beat every other splitter [page:chunking]."


@pytest.fixture()
def wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    wiki_dir = tmp_path / "wiki"
    (wiki_dir / "rag").mkdir(parents=True)
    (wiki_dir / "private").mkdir()
    (wiki_dir / "rag" / "chunking.md").write_text(PAGE.format(t="Chunking", b=CHUNKING))
    (wiki_dir / "rag" / "reranking.md").write_text(PAGE.format(t="Reranking", b=RERANKING))
    monkeypatch.setattr(corpus, "WIKI_DIR", wiki_dir)
    monkeypatch.setattr(corpus, "PRIVATE_DIR", wiki_dir / "private")
    monkeypatch.setattr(corpus, "DB_PATH", tmp_path / ".idx.duckdb")
    monkeypatch.setattr(embeddings, "HAS_EMBEDDINGS", False)
    return wiki_dir


@pytest.fixture()
def judge_on(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = get_settings().model_copy(update={"claim_judge": True})
    monkeypatch.setattr(agent, "get_settings", lambda: settings)


async def _grounding(client: object, **kwargs: Any) -> dict[str, Any]:  # noqa: ANN401
    events = [e async for e in agent.run_agent_stream("how to chunk", client=client, **kwargs)]
    (grounding,) = [e for e in events if e["type"] == "grounding"]
    return grounding


def _client(fake_anthropic: type, text: str, *read: str, replies: list[str] | None = None) -> Any:  # noqa: ANN401
    t = fake_anthropic
    return t(
        turns=[*(t.tool_turn(("read_page", {"page_id": p})) for p in read), t.text_turn(text)],
        replies=replies,
    )


# -- the deterministic check ----------------------------------------------------------------


@pytest.mark.unit
def test_split_claims_pairs_each_marker_with_the_statement_before_it() -> None:
    answer = (
        "**Headline.** Chunk by headings to keep topics whole [page:chunking].\n"
        "- Rerank the top results with a cross-encoder [page:reranking] [page:chunking]\n"
        "- Ok [page:other]"
    )
    assert support.split_claims(answer, agent.CITATION_RE) == [
        ("Chunk by headings to keep topics whole", "chunking"),
        ("Rerank the top results with a cross-encoder", "reranking"),
        # Side-by-side markers share the claim.
        ("Rerank the top results with a cross-encoder", "chunking"),
        ("Ok", "other"),
    ]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("claim", "found"),
    [
        ("Splitting pages at headings keeps one topic per chunk", True),  # overlap, stemmed
        ('The page says "each chunk keeps  one topic" outright, nothing else matches', True),
        ("Sentence windows of 512 tokens beat every other splitter", False),
        ('It promises "zero hallucinations forever" for retrieval pipelines', False),
    ],
    ids=["overlap", "quote", "no-overlap", "quote-absent"],
)
def test_supports_by_quote_or_overlap(claim: str, found: bool) -> None:
    assert support.supports(claim, CHUNKING, 0.5) is found


@pytest.mark.unit
def test_check_skips_unread_pages_and_claims_too_short_to_match() -> None:
    answer = "Yes [page:chunking]. Cross-encoders score query passage pairs [page:reranking]."
    # `chunking` was read but "Yes" is no claim; `reranking` was cited without being read.
    assert support.check(answer, {"chunking": CHUNKING}, agent.CITATION_RE, 0.5) == []


# -- in the agent loop ----------------------------------------------------------------------


@pytest.mark.unit
async def test_read_page_without_support_is_flagged_and_logged(
    wiki: Path, fake_anthropic: type
) -> None:
    client = _client(fake_anthropic, f"{GROUNDED} {UNFOUNDED}", "chunking")
    grounding = await _grounding(client)
    # Read, so not ungrounded: the third state.
    assert grounding["ungrounded"] == []
    assert grounding["unsupported"] == ["chunking"]
    assert grounding["support"] == {"checked": 2, "supported": 1, "judge": False}
    assert client.create_calls == []  # the judge is off by default

    line = json.loads((corpus.LOGS_DIR / agent.AGENT_LOG_NAME).read_text().splitlines()[0])
    assert line["unsupported"] == ["chunking"] and line["support"] == grounding["support"]


@pytest.mark.unit
async def test_supported_answer_flags_nothing(wiki: Path, fake_anthropic: type) -> None:
    grounding = await _grounding(_client(fake_anthropic, GROUNDED, "chunking"))
    assert grounding["unsupported"] == []
    assert grounding["support"] == {"checked": 1, "supported": 1, "judge": False}


@pytest.mark.unit
def test_judge_is_off_by_default() -> None:
    assert get_settings().claim_judge is False


@pytest.mark.unit
async def test_judge_clears_a_paraphrase_and_its_usage_is_billed(
    wiki: Path, fake_anthropic: type, judge_on: None
) -> None:
    client = _client(fake_anthropic, UNFOUNDED, "chunking")

    async def create(**kwargs: Any) -> SimpleNamespace:  # noqa: ANN401
        client.create_calls.append(kwargs)
        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text='{"supported": [true]}')],
            usage=SimpleNamespace(input_tokens=900, output_tokens=12),
        )

    client.messages.create = create
    billed: list[TokenUsage] = []
    grounding = await _grounding(client, on_usage=billed.append)

    assert grounding["unsupported"] == []
    assert grounding["support"] == {"checked": 1, "supported": 1, "judge": True}
    # The judge saw the failing claim and the page text, and its tokens went to on_usage, which
    # is what the chat route records against chat_usage.
    sent = client.create_calls[0]["messages"][0]["content"]
    assert "512 tokens" in sent and "Split a page at its headings" in sent
    assert billed[-1] == TokenUsage(input=900, output=12)
    line = json.loads((corpus.LOGS_DIR / agent.AGENT_LOG_NAME).read_text().splitlines()[0])
    assert line["usage"]["input"] == 900 and line["support"]["judge"] is True


@pytest.mark.unit
@pytest.mark.parametrize("reply", ['{"supported": [false]}', "garbled", '{"supported": []}'])
async def test_judge_that_disagrees_or_cannot_be_read_leaves_the_flag(
    wiki: Path, fake_anthropic: type, judge_on: None, reply: str
) -> None:
    client = _client(fake_anthropic, UNFOUNDED, "chunking", replies=[reply])
    grounding = await _grounding(client)
    assert grounding["unsupported"] == ["chunking"]
    assert grounding["support"]["judge"] is (reply == '{"supported": [false]}')


@pytest.mark.unit
async def test_judge_failure_does_not_break_the_answer(
    wiki: Path, fake_anthropic: type, judge_on: None
) -> None:
    # No scripted reply: the judge call raises. Grounding still arrives, from the check.
    grounding = await _grounding(_client(fake_anthropic, UNFOUNDED, "chunking"))
    assert grounding["unsupported"] == ["chunking"] and grounding["support"]["judge"] is False


@pytest.mark.unit
async def test_judge_is_not_called_when_every_pair_passes(
    wiki: Path, fake_anthropic: type, judge_on: None
) -> None:
    client = _client(fake_anthropic, GROUNDED, "chunking")
    await _grounding(client)
    assert client.create_calls == []
