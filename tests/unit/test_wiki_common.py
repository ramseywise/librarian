"""Characterization tests for the two colliding slugify variants (LIB-110 Step B2).

Variant A (`wiki_parser._slug`, `relinker._slug`):
    title.lower().strip().replace(" ", "-")
Variant B (`graph_expansion._slug`, inline in `server.py`):
    re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

No prior test pinned either variant on punctuated input (plan R1). These pin
CURRENT behavior so Step B3's unification is a measured change, not a silent
one. When B3 lands, collapse each divergent pair into the single chosen
expectation and assert one slugify for the whole repo.
"""

import pytest

from app.backend.wiki_parser import _slug as slug_a_parser
from app.mcp_server.graph_expansion import _slug as slug_b
from core.relinker import _slug as slug_a_relinker

# (input, variant A output, variant B output)
CASES = [
    ("RAG & Retrieval", "rag-&-retrieval", "rag-retrieval"),
    ("RLHF Pipeline's Cost", "rlhf-pipeline's-cost", "rlhf-pipeline-s-cost"),
    ("", "", ""),
    ("Café Décor", "café-décor", "caf-d-cor"),
    ("Semantic  Cache", "semantic--cache", "semantic-cache"),
    ("  Padded Title  ", "padded-title", "padded-title"),
    ("(Retrieval)", "(retrieval)", "retrieval"),
    ("Trailing!", "trailing!", "trailing"),
    ("Semantic Cache", "semantic-cache", "semantic-cache"),
]


@pytest.mark.parametrize(("text", "expected_a", "_b"), CASES)
def test_variant_a_current_behavior(text: str, expected_a: str, _b: str) -> None:
    assert slug_a_parser(text) == expected_a


@pytest.mark.parametrize(("text", "_a", "expected_b"), CASES)
def test_variant_b_current_behavior(text: str, _a: str, expected_b: str) -> None:
    assert slug_b(text) == expected_b


@pytest.mark.parametrize(("text", "_a", "_b"), CASES)
def test_both_a_sites_agree(text: str, _a: str, _b: str) -> None:
    """relinker and wiki_parser must stay in lockstep until B3 deletes both."""
    assert slug_a_parser(text) == slug_a_relinker(text)
