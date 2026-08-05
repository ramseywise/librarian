"""Pins for the unified slugify (LIB-110 Step B3).

Step B2 characterized the two colliding variants (A: lower+replace-space,
B: regex collapse) and measured blast radius 0 over the live wiki; B3 collapsed
both onto variant B as `core.wiki_common.slugify`. These tests pin the single
semantic and assert every former call site resolves to the same function, so a
local re-definition would fail here rather than silently re-forking resolution.

Out-of-scope variants (presenter filename slug, scrape_* raw-file slug) keep
their own definitions deliberately — see the LIB-110 plan, Out of Scope.
"""

import pytest

from core.wiki_common import slugify

# (input, expected slug) — the divergent cases from B2, now with one answer.
CASES = [
    ("RAG & Retrieval", "rag-retrieval"),
    ("RLHF Pipeline's Cost", "rlhf-pipeline-s-cost"),
    ("", ""),
    ("Café Décor", "caf-d-cor"),
    ("Semantic  Cache", "semantic-cache"),
    ("  Padded Title  ", "padded-title"),
    ("(Retrieval)", "retrieval"),
    ("Trailing!", "trailing"),
    ("Semantic Cache", "semantic-cache"),
    ("CRAG Retry Logic\\", "crag-retry-logic"),
]


@pytest.mark.parametrize(("text", "expected"), CASES)
def test_slugify(text: str, expected: str) -> None:
    assert slugify(text) == expected


def test_single_definition_across_consumers() -> None:
    """All link-resolution modules must share the one slugify."""
    import app.backend.wiki_parser as wiki_parser
    import app.mcp_server.graph_expansion as graph_expansion
    import app.mcp_server.server as server
    import core.relinker as relinker

    for module in (wiki_parser, graph_expansion, server, relinker):
        assert module.slugify is slugify
        assert not hasattr(module, "_slug")
