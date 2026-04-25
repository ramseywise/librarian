"""Skill management for the native_skill_mcp LangGraph agent.

Parses SKILL.md frontmatter at import time to build:
- SKILL_TOOL_MAP: skill_name → list of MCP tool names gated behind it
- SKILL_INSTRUCTIONS: skill_name → body text returned by load_skill
- SKILL_DESCRIPTIONS: skill_name → one-line description for the available_skills block

Also defines the four meta-tools always present in the visible tool list:
  load_skill, list_skills, load_skill_resource, run_skill_script
"""

from __future__ import annotations

import logging
import pathlib
from typing import Annotated

logger = logging.getLogger(__name__)

import yaml
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.types import Command

SKILLS_DIR = pathlib.Path(__file__).parent / "skills"

# ── Frontmatter parsing ───────────────────────────────────────────────────────


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split YAML frontmatter from body. Returns (frontmatter_dict, body_text)."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    return yaml.safe_load(parts[1]) or {}, parts[2].strip()


# ── Build skill maps at import time ──────────────────────────────────────────

SKILL_TOOL_MAP: dict[str, list[str]] = {}  # skill_name → MCP tool names
SKILL_INSTRUCTIONS: dict[str, str] = {}  # skill_name → body text
SKILL_DESCRIPTIONS: dict[str, str] = {}  # skill_name → one-line description

for _skill_dir in sorted(SKILLS_DIR.iterdir()):
    _md_path = _skill_dir / "SKILL.md"
    if not _md_path.exists():
        continue
    _fm, _body = _parse_frontmatter(_md_path.read_text(encoding="utf-8"))
    _name: str = _fm.get("name", _skill_dir.name)
    # Lazy skills use adk_additional_tools; preloaded support-skill uses tools
    _tools: list[str] = (
        _fm.get("metadata", {}).get("adk_additional_tools")
        or _fm.get("metadata", {}).get("tools")
        or []
    )
    SKILL_TOOL_MAP[_name] = _tools
    SKILL_INSTRUCTIONS[_name] = _body
    _desc = _fm.get("description", "")
    # description may be a multi-line scalar; normalise to single line
    SKILL_DESCRIPTIONS[_name] = " ".join(str(_desc).split())

# ── Preloaded vs. lazy split ──────────────────────────────────────────────────

PRELOADED_SKILLS: list[str] = ["support-skill"]
LAZY_SKILLS: list[str] = [
    "invoice-skill",
    "customer-skill",
    "product-skill",
    "email-skill",
    "invitation-skill",
]

PRELOADED_TOOL_NAMES: frozenset[str] = frozenset(
    t for s in PRELOADED_SKILLS for t in SKILL_TOOL_MAP.get(s, [])
)


# ── Tool visibility helper ────────────────────────────────────────────────────


def get_visible_tools(
    all_billy_tools: dict,
    activated_skills: list[str],
    meta_tools: list,
) -> list:
    """Return the tool list the model should see on this turn.

    Starts with meta-tools + preloaded tools, then adds MCP tools for each
    activated lazy skill.
    """
    visible_names = set(PRELOADED_TOOL_NAMES)
    for skill_name in activated_skills:
        visible_names.update(SKILL_TOOL_MAP.get(skill_name, []))
    billy_visible = [t for name, t in all_billy_tools.items() if name in visible_names]
    return list(meta_tools) + billy_visible


# ── System-prompt helpers ─────────────────────────────────────────────────────


def build_preloaded_section(preloaded_skill_names: list[str]) -> str:
    """Format preloaded skill instructions for inline injection into the system prompt."""
    lines = ["## Preloaded Skills\n\nThe following skills are always active:\n"]
    for name in preloaded_skill_names:
        body = SKILL_INSTRUCTIONS.get(name, "")
        lines.append(f"### {name}\n{body}\n")
    return "\n".join(lines)


def build_available_skills_xml(lazy_skill_names: list[str]) -> str:
    """Build the <available_skills> XML block appended to the system prompt each turn.

    Equivalent to SkillToolset.process_llm_request in the ADK implementation.
    """
    items = "\n".join(
        f'  <skill name="{name}" description="{SKILL_DESCRIPTIONS.get(name, "")}" />'
        for name in lazy_skill_names
        if name in SKILL_DESCRIPTIONS
    )
    return f"<available_skills>\n{items}\n</available_skills>"


# ── Meta-tools ────────────────────────────────────────────────────────────────


@tool
def load_skill(
    skill_name: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Load a skill to activate its tools and retrieve its step-by-step instructions.

    Call this before using any tool from a lazy skill domain (invoice, customer,
    product, email, invitation). Pass the skill name with or without '-skill' suffix.
    """
    canonical = skill_name if skill_name.endswith("-skill") else f"{skill_name}-skill"
    logger.info("load_skill: %s", canonical)
    if canonical not in SKILL_INSTRUCTIONS:
        available = sorted(SKILL_INSTRUCTIONS.keys())
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=(
                            f"Unknown skill '{skill_name}'. "
                            f"Available skills: {available}"
                        ),
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )
    instructions = SKILL_INSTRUCTIONS[canonical]
    # activated_skills uses _merge_skills reducer — returning [canonical] is safe.
    return Command(
        update={
            "activated_skills": [canonical],
            "messages": [ToolMessage(content=instructions, tool_call_id=tool_call_id)],
        }
    )


@tool
def list_skills() -> str:
    """List all available skills and their one-line descriptions."""
    lines = [
        f"- {name}: {SKILL_DESCRIPTIONS.get(name, '')}"
        for name in sorted(SKILL_INSTRUCTIONS.keys())
    ]
    return "\n".join(lines)


@tool
def load_skill_resource(skill_name: str, resource_name: str) -> str:
    """Load a resource file from a skill directory."""
    canonical = skill_name if skill_name.endswith("-skill") else f"{skill_name}-skill"
    skill_dir = SKILLS_DIR / canonical
    if not skill_dir.is_dir():
        return f"Skill '{canonical}' not found."
    resource_path = skill_dir / resource_name
    if not resource_path.exists():
        return f"Resource '{resource_name}' not found in skill '{canonical}'."
    return resource_path.read_text(encoding="utf-8")


@tool
def run_skill_script(skill_name: str, script_name: str) -> str:
    """Run a script from a skill directory. (Not supported in this LangGraph port.)"""
    return "run_skill_script is not supported in this implementation."


# Ordered list of all meta-tools — always visible regardless of activated_skills.
META_TOOLS: list = [load_skill, list_skills, load_skill_resource, run_skill_script]
