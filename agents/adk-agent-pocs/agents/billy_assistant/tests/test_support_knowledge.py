"""Tests for the fetch_support_knowledge tool.

Verifies keyword matching, deduplication, result formatting, and edge cases
against the in-memory mock knowledge base.
"""

# pylint: disable=no-self-use,too-few-public-methods
import pytest

from playground.agent_poc.agents.billy_assistant.tools.support_knowledge_stub import (
    fetch_support_knowledge,
)


class TestFetchSupportKnowledge:
    """Tests for `fetch_support_knowledge`."""

    @pytest.mark.parametrize(
        ("queries", "expected_fragment"),
        [
            (["faktura"], "faktura"),
            (["opret faktura"], "faktura"),
            (["e-mail", "send"], "e-mail"),
            (["inviter", "bruger"], "invit"),
            (["produkt"], "produkt"),
            (["moms"], "moms"),
        ],
    )
    def test_returns_relevant_passage(self, queries: list, expected_fragment: str):
        """A relevant query returns a passage containing the expected term."""
        result = fetch_support_knowledge(queries=queries)
        assert expected_fragment.lower() in result.lower()

    def test_no_results_for_unrelated_query(self):
        """An unrelated query that matches nothing returns the no-results message."""
        result = fetch_support_knowledge(queries=["xyzzy123", "foobar456"])
        assert result == "No relevant documentation found."

    def test_result_is_string(self):
        """The function always returns a string."""
        result = fetch_support_knowledge(queries=["faktura"])
        assert isinstance(result, str)

    def test_passage_header_format(self):
        """Each passage in the result begins with [PASSAGE N]."""
        result = fetch_support_knowledge(queries=["faktura"])
        assert "[PASSAGE 1]" in result

    def test_passage_includes_url(self):
        """Passages include a URL line."""
        result = fetch_support_knowledge(queries=["faktura"])
        assert "URL:" in result

    def test_multiple_queries_deduplicate_results(self):
        """Two queries for the same topic do not produce duplicate passages."""
        result = fetch_support_knowledge(queries=["faktura", "opret faktura"])
        # Count occurrences of "[PASSAGE" to measure how many passages were returned
        passage_count = result.count("[PASSAGE")
        # If deduplication works, a URL that matches both queries appears only once
        first_url_occurrences = result.count("help.billy.dk/da/articles/create-invoice")
        assert first_url_occurrences == 1

    def test_returns_at_most_five_passages(self):
        """The result is capped at 5 passages regardless of query count."""
        queries = ["faktura", "moms", "betaling", "produkt", "inviter", "kunde"]
        result = fetch_support_knowledge(queries=queries)
        passage_count = result.count("[PASSAGE")
        assert passage_count <= 5

    def test_score_shown_in_header(self):
        """Each passage header includes a score value."""
        result = fetch_support_knowledge(queries=["faktura"])
        assert "score=" in result

    def test_passage_separator_present(self):
        """Multiple passages are separated by '---'."""
        result = fetch_support_knowledge(queries=["faktura", "moms"])
        if result.count("[PASSAGE") > 1:
            assert "---" in result

    def test_empty_queries_list_returns_no_results(self):
        """An empty queries list returns the no-results message."""
        result = fetch_support_knowledge(queries=[])
        assert result == "No relevant documentation found."
