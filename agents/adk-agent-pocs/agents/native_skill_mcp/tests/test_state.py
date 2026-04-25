"""Tests for AgentState and the _merge_skills reducer."""

from langgraph_agents.native_skill_mcp.state import _merge_skills


class TestMergeSkills:
    def test_empty_current_none(self):
        assert _merge_skills(None, ["invoice-skill"]) == ["invoice-skill"]

    def test_empty_current_list(self):
        assert _merge_skills([], ["invoice-skill"]) == ["invoice-skill"]

    def test_appends_new_skill(self):
        result = _merge_skills(["invoice-skill"], ["customer-skill"])
        assert result == ["invoice-skill", "customer-skill"]

    def test_deduplicates_existing(self):
        result = _merge_skills(["invoice-skill"], ["invoice-skill"])
        assert result == ["invoice-skill"]

    def test_adds_only_novel_from_batch(self):
        result = _merge_skills(["invoice-skill"], ["invoice-skill", "customer-skill"])
        assert result == ["invoice-skill", "customer-skill"]

    def test_preserves_order(self):
        result = _merge_skills(["a", "b"], ["c", "d"])
        assert result == ["a", "b", "c", "d"]

    def test_empty_new(self):
        assert _merge_skills(["invoice-skill"], []) == ["invoice-skill"]

    def test_does_not_mutate_input(self):
        current = ["invoice-skill"]
        _merge_skills(current, ["customer-skill"])
        assert current == ["invoice-skill"]
