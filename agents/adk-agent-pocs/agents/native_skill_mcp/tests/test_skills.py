"""Tests for skills.py — SKILL_TOOL_MAP, meta-tools, and tool visibility."""

from langchain_core.tools import BaseTool
from langgraph.types import Command

from langgraph_agents.native_skill_mcp.skills import (
    LAZY_SKILLS,
    META_TOOLS,
    PRELOADED_SKILLS,
    PRELOADED_TOOL_NAMES,
    SKILL_DESCRIPTIONS,
    SKILL_INSTRUCTIONS,
    SKILL_TOOL_MAP,
    _parse_frontmatter,
    build_available_skills_xml,
    build_preloaded_section,
    get_visible_tools,
    list_skills,
    load_skill,
    load_skill_resource,
    run_skill_script,
)


# ── Frontmatter parsing ───────────────────────────────────────────────────────


class TestParseFrontmatter:
    def test_valid_frontmatter(self):
        md = "---\nname: test\ndescription: A test\n---\nBody text."
        fm, body = _parse_frontmatter(md)
        assert fm["name"] == "test"
        assert body == "Body text."

    def test_no_frontmatter(self):
        md = "Just body text."
        fm, body = _parse_frontmatter(md)
        assert fm == {}
        assert body == "Just body text."

    def test_nested_metadata(self):
        md = "---\nname: invoice-skill\nmetadata:\n  adk_additional_tools:\n    - list_invoices\n---\nInstructions."
        fm, body = _parse_frontmatter(md)
        assert fm["metadata"]["adk_additional_tools"] == ["list_invoices"]
        assert body == "Instructions."

    def test_body_stripped(self):
        md = "---\nname: x\n---\n\n\nBody with leading newlines."
        _, body = _parse_frontmatter(md)
        assert not body.startswith("\n")


# ── Skill maps ────────────────────────────────────────────────────────────────


class TestSkillMaps:
    def test_all_skills_present(self):
        expected = {
            "invoice-skill",
            "customer-skill",
            "product-skill",
            "email-skill",
            "invitation-skill",
            "support-skill",
        }
        assert expected == set(SKILL_TOOL_MAP.keys())

    def test_invoice_tools(self):
        assert SKILL_TOOL_MAP["invoice-skill"] == [
            "list_invoices",
            "get_invoice",
            "get_invoice_summary",
            "create_invoice",
            "edit_invoice",
        ]

    def test_customer_tools(self):
        assert SKILL_TOOL_MAP["customer-skill"] == [
            "list_customers",
            "create_customer",
            "edit_customer",
        ]

    def test_support_tools(self):
        assert SKILL_TOOL_MAP["support-skill"] == ["fetch_support_knowledge"]

    def test_email_tools(self):
        assert SKILL_TOOL_MAP["email-skill"] == ["send_invoice_by_email"]

    def test_invitation_tools(self):
        assert SKILL_TOOL_MAP["invitation-skill"] == ["invite_user"]

    def test_product_tools(self):
        assert SKILL_TOOL_MAP["product-skill"] == [
            "list_products",
            "create_product",
            "edit_product",
        ]

    def test_instructions_non_empty(self):
        for skill, instructions in SKILL_INSTRUCTIONS.items():
            assert instructions, f"{skill} has empty instructions"

    def test_descriptions_non_empty(self):
        for skill, desc in SKILL_DESCRIPTIONS.items():
            assert desc, f"{skill} has empty description"
            assert "\n" not in desc, f"{skill} description should be single-line"

    def test_preloaded_skills(self):
        assert PRELOADED_SKILLS == ["support-skill"]

    def test_lazy_skills(self):
        assert set(LAZY_SKILLS) == {
            "invoice-skill",
            "customer-skill",
            "product-skill",
            "email-skill",
            "invitation-skill",
        }

    def test_preloaded_tool_names(self):
        assert PRELOADED_TOOL_NAMES == frozenset({"fetch_support_knowledge"})


# ── get_visible_tools ─────────────────────────────────────────────────────────


class TestGetVisibleTools:
    """get_visible_tools returns meta-tools + preloaded tools + activated-skill tools."""

    def _make_billy_tools(self, names: list[str]) -> dict:
        """Build a minimal fake billy-tools dict."""
        from unittest.mock import MagicMock

        tools = {}
        for name in names:
            t = MagicMock(spec=BaseTool)
            t.name = name
            tools[name] = t
        return tools

    def test_no_activated_skills_returns_meta_plus_preloaded(self):
        all_billy = self._make_billy_tools(["fetch_support_knowledge", "list_invoices"])
        visible = get_visible_tools(
            all_billy, activated_skills=[], meta_tools=META_TOOLS
        )
        names = [t.name for t in visible]
        assert "load_skill" in names
        assert "list_skills" in names
        assert "fetch_support_knowledge" in names
        assert "list_invoices" not in names

    def test_activated_invoice_skill_adds_invoice_tools(self):
        all_tools = [
            "fetch_support_knowledge",
            "list_invoices",
            "get_invoice",
            "get_invoice_summary",
            "create_invoice",
            "edit_invoice",
        ]
        all_billy = self._make_billy_tools(all_tools)
        visible = get_visible_tools(
            all_billy,
            activated_skills=["invoice-skill"],
            meta_tools=META_TOOLS,
        )
        names = {t.name for t in visible}
        assert {"list_invoices", "get_invoice", "create_invoice"} <= names
        assert "fetch_support_knowledge" in names  # preloaded always present

    def test_activated_two_skills(self):
        all_tools = [
            "fetch_support_knowledge",
            "list_invoices",
            "create_invoice",
            "list_customers",
        ]
        all_billy = self._make_billy_tools(all_tools)
        visible = get_visible_tools(
            all_billy,
            activated_skills=["invoice-skill", "customer-skill"],
            meta_tools=META_TOOLS,
        )
        names = {t.name for t in visible}
        assert "list_invoices" in names
        assert "list_customers" in names

    def test_meta_tools_always_present(self):
        visible = get_visible_tools({}, activated_skills=[], meta_tools=META_TOOLS)
        meta_names = {t.name for t in META_TOOLS}
        visible_names = {t.name for t in visible}
        assert meta_names <= visible_names

    def test_unknown_activated_skill_ignored(self):
        """Activating a non-existent skill should not crash and adds no tools."""
        all_billy = self._make_billy_tools(["fetch_support_knowledge"])
        visible = get_visible_tools(
            all_billy,
            activated_skills=["nonexistent-skill"],
            meta_tools=META_TOOLS,
        )
        names = {t.name for t in visible}
        assert "fetch_support_knowledge" in names


# ── System-prompt builders ────────────────────────────────────────────────────


class TestSystemPromptBuilders:
    def test_preloaded_section_contains_support_content(self):
        section = build_preloaded_section(["support-skill"])
        assert "support-skill" in section
        assert "fetch_support_knowledge" in section  # from SKILL.md body

    def test_available_skills_xml_contains_all_lazy_skills(self):
        xml = build_available_skills_xml(LAZY_SKILLS)
        assert "<available_skills>" in xml
        for skill in LAZY_SKILLS:
            assert f'name="{skill}"' in xml

    def test_available_skills_xml_descriptions_single_line(self):
        xml = build_available_skills_xml(LAZY_SKILLS)
        # Each description attribute should not span lines
        for line in xml.splitlines():
            if 'description="' in line:
                assert line.count('"') >= 2


# ── Meta-tools ────────────────────────────────────────────────────────────────


class TestMetaTools:
    def _tool_call(self, name: str, args: dict, call_id: str = "tc-1") -> dict:
        return {"name": name, "args": args, "type": "tool_call", "id": call_id}

    def test_load_skill_known_returns_command(self):
        result = load_skill.invoke(
            self._tool_call("load_skill", {"skill_name": "invoice"})
        )
        assert isinstance(result, Command)
        assert result.update["activated_skills"] == ["invoice-skill"]

    def test_load_skill_accepts_full_suffix(self):
        result = load_skill.invoke(
            self._tool_call("load_skill", {"skill_name": "invoice-skill"})
        )
        assert result.update["activated_skills"] == ["invoice-skill"]

    def test_load_skill_returns_tool_message_with_instructions(self):
        result = load_skill.invoke(
            self._tool_call("load_skill", {"skill_name": "invoice"}, call_id="tc-99")
        )
        msgs = result.update["messages"]
        assert len(msgs) == 1
        assert msgs[0].tool_call_id == "tc-99"
        assert "Invoice Operations" in msgs[0].content  # from SKILL.md body

    def test_load_skill_unknown_returns_error_command(self):
        result = load_skill.invoke(
            self._tool_call("load_skill", {"skill_name": "dragons"})
        )
        assert isinstance(result, Command)
        assert "activated_skills" not in result.update
        assert "Unknown skill" in result.update["messages"][0].content

    def test_list_skills_returns_all_skills(self):
        output = list_skills.invoke({})
        for skill in SKILL_TOOL_MAP.keys():
            assert skill in output

    def test_load_skill_resource_unknown_skill(self):
        result = load_skill_resource.invoke(
            {"skill_name": "dragons", "resource_name": "SKILL.md"}
        )
        assert "not found" in result.lower()

    def test_load_skill_resource_unknown_resource(self):
        result = load_skill_resource.invoke(
            {"skill_name": "invoice", "resource_name": "nonexistent.txt"}
        )
        assert "not found" in result.lower()

    def test_load_skill_resource_returns_skill_md(self):
        result = load_skill_resource.invoke(
            {"skill_name": "invoice", "resource_name": "SKILL.md"}
        )
        assert "invoice-skill" in result  # SKILL.md frontmatter name

    def test_run_skill_script_not_supported(self):
        result = run_skill_script.invoke(
            {"skill_name": "invoice", "script_name": "anything.sh"}
        )
        assert "not supported" in result.lower()

    def test_meta_tools_list_has_four_entries(self):
        assert len(META_TOOLS) == 4
        names = [t.name for t in META_TOOLS]
        assert names == [
            "load_skill",
            "list_skills",
            "load_skill_resource",
            "run_skill_script",
        ]
