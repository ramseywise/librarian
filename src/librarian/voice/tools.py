"""What a voice agent may call. `record_grade` is the only write; the rest come from the shared
tool registry (`librarian.agent.tools`), a subset of its LEARNING_TOOLS. `search_lessons` and
`read_page` are left out on purpose: they return lesson and page bodies, solutions included, which
the model has no business fetching mid-drill.

`record_grade` isn't strict, as strict schemas can't express the 0 to 1 bounds: `grades.parse_grade`
checks them. Tools stream eagerly, so a parsed input can be truncated: it's validated all the same.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from librarian.agent.tools import CHAT, LEARNING_TOOLS, ToolContext
from librarian.agent.tools import tools_for as registry_tools
from librarian.log_config import get_logger

from .policy import Mode

log = get_logger(__name__)

RECORD_GRADE = "record_grade"
READ_ONLY_TOOLS: dict[Mode, tuple[str, ...]] = {
    "flashcard": ("concept_status",),
    "approach": ("concept_status", "learning_next"),
    "interview": ("concept_status", "learning_next"),
}

_RECORD_GRADE_TOOL: dict[str, Any] = {
    "name": RECORD_GRADE,
    "description": (
        "Record a score for the answer just given, for its content only. Call once per answer, "
        "after your spoken reaction. Do not call when there was no answer to judge."
    ),
    "input_schema": {
        "type": "object",
        "properties": {"score": {"type": "number", "description": "From 0 to 1"}},
        "required": ["score"],
        "additionalProperties": False,
    },
}


@dataclass(frozen=True)
class ToolOutcome:
    text: str
    is_error: bool = False


def tools_for(mode: Mode) -> list[dict[str, Any]]:
    names = READ_ONLY_TOOLS[mode]
    # The registry is the one source of truth; a name outside LEARNING_TOOLS is a code error here.
    assert set(names) <= LEARNING_TOOLS, names
    specs = [t.anthropic_spec() for t in registry_tools(CHAT, names)]
    return [{**tool, "eager_input_streaming": True} for tool in [_RECORD_GRADE_TOOL, *specs]]


async def run_read_only(
    name: str, args: object, mode: Mode, user_id: str | None = None
) -> ToolOutcome:
    """Refuses anything not offered to this mode, whatever the model asks for. Off the event
    loop: the tools read the catalog and the attempts store."""
    if name not in READ_ONLY_TOOLS[mode] or not isinstance(args, dict):
        return ToolOutcome(f"{name} is not available here.", is_error=True)
    (tool,) = registry_tools(CHAT, (name,))
    ctx = ToolContext(surface=CHAT, user_id=user_id)
    try:
        text = await asyncio.to_thread(tool.run, args, ctx)
    except Exception as exc:
        log.warning("voice.tool.failed", tool=name, error=type(exc).__name__)
        return ToolOutcome(f"{name} failed.", is_error=True)
    return ToolOutcome(text)
