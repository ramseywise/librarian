"""skill_assistant_mcp — Billy accounting agent using McpToolset + SkillToolset."""

import pathlib
import sys

# Ensure the workspace root precedes agents/ on sys.path so that
# `shared.*` resolves to the top-level shared/ package, not agents/shared/.
_REPO_ROOT = str(pathlib.Path(__file__).parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import yaml
from google.adk import Agent
from google.adk.skills import Frontmatter, Skill
from google.adk.tools.skill_toolset import SkillToolset
from google.genai import types

from playground.agent_poc.shared.tools.billy_toolset import (
    get_billy_toolset as _get_billy_toolset,
)

_SKILLS_DIR = pathlib.Path(__file__).parent / "skills"
_PROMPTS_DIR = pathlib.Path(__file__).parent / "prompts"

# Skills listed here are injected directly into the system prompt at load time.
# Add a skill directory name to preload its instructions without requiring load_skill.
_PRELOADED_SKILLS = [
    "support-skill",
]

# Skills listed here are loaded lazily at runtime via load_skill.
# The agent calls load_skill when it first needs a domain.
_LAZY_LOADED_SKILLS = [
    "invoice-skill",
    "customer-skill",
    "product-skill",
    "email-skill",
    "invitation-skill",
]


def _load_skill_from_dir(skill_dir: pathlib.Path) -> Skill:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    _, fm_block, body = text.split("---", 2)
    fm = yaml.safe_load(fm_block)
    return Skill(frontmatter=Frontmatter(**fm), instructions=body.strip())


def _build_instruction() -> str:
    """Load root_agent.txt and inline all _PRELOADED_SKILLS at the placeholder."""
    blocks = []
    for name in _PRELOADED_SKILLS:
        text = (_SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")
        _, fm_block, body = text.split("---", 2)
        fm = yaml.safe_load(fm_block)
        blocks.append(
            f"## Built-in Capability: {fm['name']}\n\n_{fm['description'].strip()}_\n\n{body.strip()}"
        )
    preloaded = "\n\n".join(blocks)
    template = (_PROMPTS_DIR / "root_agent.txt").read_text(encoding="utf-8")
    instruction = template.replace("<!-- PRELOADED_SKILLS -->", preloaded)
    return instruction


_skill_toolset = SkillToolset(
    skills=[_load_skill_from_dir(_SKILLS_DIR / name) for name in _LAZY_LOADED_SKILLS]
)


_billy_toolset = _get_billy_toolset()

root_agent = Agent(
    model="gemini-3-flash-preview",
    name="skill_assistant_mcp",
    description="Billy accounting assistant (MCP tools edition)",
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
        thinking_config=types.ThinkingConfig(
            thinking_budget=8000, include_thoughts=False
        ),
    ),
    instruction=_build_instruction(),
    tools=[
        _billy_toolset,
        _skill_toolset,
    ],
)
