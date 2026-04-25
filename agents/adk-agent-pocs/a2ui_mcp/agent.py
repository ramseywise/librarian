"""a2ui_mcp — Billy agent with native SkillToolset + adk_additional_tools."""

import importlib
import pathlib
import sys
from datetime import date

from google.adk import Agent
from google.adk.skills._utils import _load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset
from google.genai import types

# Ensure the workspace root precedes agents/ on sys.path so that
# `shared.*` resolves to the top-level shared/ package, not agents/shared/.
_REPO_ROOT = str(pathlib.Path(__file__).parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

_billy_toolset = importlib.import_module("shared.tools.billy_toolset")
_dynamic_skill_tools = importlib.import_module("shared.tools.dynamic_skill_tools")

create_billy_toolset = _billy_toolset.create_billy_toolset
get_billy_toolset = _billy_toolset.get_billy_toolset
build_preloaded_section = _dynamic_skill_tools.build_preloaded_section
make_preloaded_toolset = _dynamic_skill_tools.make_preloaded_toolset

_history_pruning = importlib.import_module("shared.tools.history_pruning")
make_history_prune_callback = _history_pruning.make_history_prune_callback

_tool_response_utils = importlib.import_module("shared.tools.tool_response_utils")
prefer_structured_tool_response = _tool_response_utils.prefer_structured_tool_response

_SKILLS_DIR = pathlib.Path(__file__).parent / "skills"
_PROMPTS_DIR = pathlib.Path(__file__).parent / "prompts"

# Instructions injected directly into the system prompt at load time.
_PRELOADED_SKILLS: list[str] = [
    "support-skill",
    "insights-skill",
]

# Skills loaded lazily via load_skill; tools gated by adk_additional_tools in SKILL.md.
_LAZY_SKILLS: list[str] = [
    "invoice-skill",
    "customer-skill",
    "product-skill",
    "email-skill",
    "invitation-skill",
]

# Always-visible: only the tools from preloaded skills (fetch_support_knowledge).
_preloaded_toolset = make_preloaded_toolset(
    preloaded_skills=_PRELOADED_SKILLS,
    skills_dir=_SKILLS_DIR,
    create_toolset=create_billy_toolset,
)

# Lazy skill tools gated by adk_additional_tools + session state.
# additional_tools provides the full candidate pool; SkillToolset resolves only
# the subset named in each activated skill's adk_additional_tools list.
_skill_toolset = SkillToolset(
    skills=[_load_skill_from_dir(_SKILLS_DIR / name) for name in _LAZY_SKILLS],
    additional_tools=[get_billy_toolset()],
)

# No {lazy_skills_section} — SkillToolset.process_llm_request appends the
# <available_skills> XML block and skill usage instructions automatically.
_instruction = (
    (_PROMPTS_DIR / "root_agent.txt")
    .read_text(encoding="utf-8")
    .replace("{today}", date.today().isoformat())
    .replace(
        "{preloaded_skills_section}",
        build_preloaded_section(_PRELOADED_SKILLS, _SKILLS_DIR),
    )
)

root_agent = Agent(
    model="gemini-3-flash-preview",
    name="a2ui_mcp",
    description="Billy accounting assistant — native SkillToolset pattern",
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
        thinking_config=types.ThinkingConfig(
            thinking_level="LOW",  # Options: MINIMAL, LOW, MEDIUM, HIGH
            include_thoughts=False,
        ),
    ),
    instruction=_instruction,
    tools=[_preloaded_toolset, _skill_toolset],
    after_tool_callback=prefer_structured_tool_response,
    # No sync_loaded_skills needed: SkillToolset uses session state
    # (_adk_activated_skill_a2ui_mcp) which persists across compaction.
    before_model_callback=make_history_prune_callback(
        [
            "fetch_support_knowledge",
            "list_customers",
            "list_products",
            "list_invoices",
            "get_invoice",
            "get_invoice_summary",
            "get_invoice_lines_summary",
        ]
    ),
)
