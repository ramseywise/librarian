"""Reusable load_skill / execute_mcp_action tool pair for the Universal Proxy Pattern.

Usage
-----
Call `make_skill_tools(skill_map, skills_dir, get_toolset)` once at module level
and unpack the three returned async functions:

    load_skill, execute_mcp_action, sync_loaded_skills = make_skill_tools(
        skill_map=SKILL_MAP,
        skills_dir=_SKILLS_DIR,
        get_toolset=_get_billy_toolset,
    )

    root_agent = Agent(
        ...
        tools=[load_skill, execute_mcp_action],
        before_model_callback=sync_loaded_skills,
    )

``sync_loaded_skills`` is a ``before_model_callback`` that detects history
compaction and clears ``loaded_skills`` state for any dynamic skill whose
``load_skill`` event is no longer in history, forcing the model to reload.
"""

import copy
import functools
import json
import logging
import pathlib
import re
import traceback
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)

import jsonschema
import yaml
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.tools import ToolContext
from google.adk.tools.mcp_tool import McpToolset

from .tool_response_utils import extract_structured_content


@functools.lru_cache(maxsize=None)
def _read_skill(skill_dir: pathlib.Path) -> tuple[dict[str, Any], str]:
    """Load a skill directory, returning (frontmatter_dict, instructions_text).

    Reads SKILL.md for the full skill definition: YAML frontmatter (name, description,
    and metadata.tools) plus the prose body.
    Results are cached per directory for the lifetime of the process, so repeated
    calls (e.g. every execute_mcp_action invocation) incur no disk I/O.
    """
    skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    fm: dict[str, Any] = {}
    body = skill_md
    if skill_md.startswith("---\n"):
        end_idx = skill_md.index("\n---\n", 4)
        fm = yaml.safe_load(skill_md[4:end_idx]) or {}
        body = skill_md[end_idx + 5 :]
    fm["tools"] = (fm.get("metadata") or {}).get("tools", [])
    return fm, body


def _parse_args_section(description: str) -> dict[str, str]:
    """Parse a Google-style 'Args:' section into {param_name: description}."""
    match = re.search(
        r"\nArgs:\n(.*?)(?:\n(?:Returns|Raises|Note|Yields|Example|See Also):|\Z)",
        description,
        re.DOTALL,
    )
    if not match:
        return {}

    args_block = match.group(1)
    # Auto-detect the base indentation of the first param line.
    base_indent: int | None = None
    for line in args_block.splitlines():
        if line.strip():
            base_indent = len(line) - len(line.lstrip())
            break
    if base_indent is None:
        return {}

    result: dict[str, str] = {}
    current_param: str | None = None
    lines: list[str] = []
    for line in args_block.splitlines():
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        content = line.strip()
        if indent == base_indent:
            if current_param is not None:
                result[current_param] = " ".join(lines).strip()
            colon_idx = content.find(":")
            if colon_idx > 0:
                name_part = content[:colon_idx].strip()
                # Strip optional type annotation: "param_name (int)" → "param_name"
                current_param = re.sub(r"\s*\(.*?\)\s*$", "", name_part)
                first = content[colon_idx + 1 :].strip()
                lines = [first] if first else []
            else:
                current_param = content
                lines = []
        elif indent > base_indent and current_param is not None:
            lines.append(content)
    if current_param is not None:
        result[current_param] = " ".join(lines).strip()
    return result


def _enrich_schema_with_descriptions(
    description: str, input_schema: dict[str, Any]
) -> dict[str, Any]:
    """Add per-property 'description' fields parsed from a Google-style docstring."""
    param_docs = _parse_args_section(description)
    if not param_docs:
        return input_schema
    schema = copy.deepcopy(input_schema)
    for prop_name, prop_schema in schema.get("properties", {}).items():
        if prop_name in param_docs and "description" not in prop_schema:
            prop_schema["description"] = param_docs[prop_name]
    return schema


def _skill_name(skill_dir_name: str) -> str:
    """Derive the agent-facing skill name from a directory name by stripping the '-skill' suffix."""
    return skill_dir_name.removesuffix("-skill")


def make_preloaded_toolset(
    preloaded_skills: list[str],
    skills_dir: pathlib.Path,
    create_toolset: Callable[[list[str] | None], McpToolset],
) -> McpToolset:
    """Create a McpToolset filtered to only the tools from preloaded skills.

    Args:
        preloaded_skills: Skill directory names to include.
        skills_dir: Path to the directory containing skill subdirectories.
        create_toolset: Factory that accepts an optional tool_filter list and
                        returns a McpToolset (e.g. create_billy_toolset).
    """
    tool_names: list[str] = []
    for s in preloaded_skills:
        fm, _ = _read_skill(skills_dir / s)
        tool_names.extend(fm.get("tools", []))
    return create_toolset(tool_names or None)


def build_preloaded_section(
    preloaded_skills: list[str],
    skills_dir: pathlib.Path,
) -> str:
    """Build the prompt section for skills whose instructions are embedded at load time.

    Returns a string with a header and the full instructions.md body for each
    preloaded skill, ready to be injected into the system prompt via
    ``{preloaded_skills_section}``.  Returns an empty string when the list is empty.
    """
    if not preloaded_skills:
        return ""
    lines: list[str] = [
        "## Preloaded Skills",
        "",
        "The following skills are always active — their tools are available immediately "
        "without calling `load_skill`.",
        "",
    ]
    for skill_dir_name in preloaded_skills:
        fm, body = _read_skill(skills_dir / skill_dir_name)
        lines.append(f"### {_skill_name(skill_dir_name)}")
        lines.append("")
        lines.append(body.strip())
        lines.append("")
    return "\n".join(lines)


def build_skills_section(
    skills: list[str],
    skills_dir: pathlib.Path,
) -> str:
    """Build the full '## Available Skills' prompt section from SKILL.md frontmatter.

    Returns a ready-to-inject string including the section header and an
    <available_skills> XML block.  Drop ``{available_skills_section}`` in any
    prompt template and replace it with the return value of this function.
    """
    lines: list[str] = [
        "## Available Skills",
        "",
        "Call `load_skill` with the `skill_name` that matches the user's request:",
        "",
    ]
    for skill_dir_name in skills:
        fm, _ = _read_skill(skills_dir / skill_dir_name)
        description: str = fm.get("description", "").strip()
        lines.append(f"- **{_skill_name(skill_dir_name)}** — {description}")
    return "\n".join(lines)


_JSON_TO_GEMINI_TYPE: dict[str, str] = {
    "string": "STRING",
    "number": "NUMBER",
    "integer": "INTEGER",
    "boolean": "BOOLEAN",
    "array": "ARRAY",
    "object": "OBJECT",
    "null": "STRING",  # fallback; should not appear as a top-level type
}

# Fields that can be forwarded as-is from JSON Schema to Gemini Schema.
_PASSTHROUGH_FIELDS = (
    "description",
    "nullable",
    "enum",
    "default",
    "minimum",
    "maximum",
    "minLength",
    "maxLength",
    "pattern",
    "minItems",
    "maxItems",
)


def _convert_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Recursively convert a JSON Schema dict to Gemini Schema format (uppercase types)."""
    result: dict[str, Any] = {}

    # Handle anyOf with a null variant → nullable + unwrapped type.
    # Note: only the first non-null variant is used; multi-type unions (rare in
    # MCP tools) are not representable in Gemini Schema and are silently narrowed.
    if "anyOf" in schema:
        variants = schema["anyOf"]
        non_null = [v for v in variants if v.get("type") != "null"]
        if non_null:
            result = _convert_schema(non_null[0])
            result["nullable"] = True
            if "description" in schema:
                result.setdefault("description", schema["description"])
            return result

    if "type" in schema:
        result["type"] = _JSON_TO_GEMINI_TYPE.get(
            schema["type"], schema["type"].upper()
        )

    for key in _PASSTHROUGH_FIELDS:
        if key in schema:
            result[key] = schema[key]

    if "properties" in schema:
        result["properties"] = {
            k: _convert_schema(v) for k, v in schema["properties"].items()
        }

    if "items" in schema:
        result["items"] = _convert_schema(schema["items"])

    if "required" in schema:
        result["required"] = schema["required"]

    return result


def make_skill_tools(
    preloaded_skills: list[str],
    lazy_skills: list[str],
    skills_dir: pathlib.Path,
    get_toolset: Callable[[], McpToolset],
) -> tuple[Any, Any, Any]:
    """Create the (load_skill, execute_mcp_action, sync_loaded_skills) triple.

    Args:
        preloaded_skills: Skill directory names whose instructions are embedded in the
                          system prompt. Their tools are always allowed in
                          execute_mcp_action without requiring a load_skill call.
        lazy_skills: Skill directory names loaded on demand via load_skill.
                     The agent-facing name is derived by stripping the "-skill" suffix.
        skills_dir: Path to the directory containing skill subdirectories.
        get_toolset: Zero-argument callable that returns the McpToolset to use.
                     Called lazily on first tool invocation.

    Returns:
        A three-tuple ``(load_skill, execute_mcp_action, sync_loaded_skills)``:

        **load_skill(skill_name, tool_context)**
            Agent-callable tool. Reads the named lazy skill's SKILL.md, fetches
            the matching MCP tool descriptors, and returns a payload containing
            the skill instructions and full JSON schemas for every tool in that
            skill. Also appends ``skill_name`` to ``state["loaded_skills"]`` so
            that ``execute_mcp_action`` will permit those tools going forward.
            Must be called before ``execute_mcp_action`` for any lazy skill.

        **execute_mcp_action(action_name, arguments, tool_context)**
            Agent-callable tool. Dispatches a single MCP tool call by name.
            Enforces a two-tier allowlist: tools belonging to preloaded skills
            are always permitted; tools belonging to lazy skills are only
            permitted after ``load_skill`` has been called for that skill
            (tracked via ``state["loaded_skills"]``). Validates ``arguments``
            against the tool's JSON Schema before dispatching and returns the
            result as a JSON string.

        **sync_loaded_skills(callback_context, llm_request)**
            ``before_model_callback``. On every model turn it scans
            ``session.events`` for ``load_skill`` function-call parts and
            removes from ``state["loaded_skills"]`` any skill whose call is no
            longer present. After history compaction the load_skill events are
            replaced by a summary, so this callback detects that and clears the
            stale entries — forcing the model to call ``load_skill`` again and
            bring the tool schemas back into context before using those tools.
    """
    # Tools from preloaded skills are always allowed — computed once at startup.
    _preloaded_tools: set[str] = set()
    for _sdir in preloaded_skills:
        _fm, _ = _read_skill(skills_dir / _sdir)
        _preloaded_tools.update(_fm.get("tools", []))

    # Map agent-facing name → directory name for lazy skills only.
    _skill_map: dict[str, str] = {_skill_name(s): s for s in lazy_skills}

    # Build skill_name parameter description from each lazy skill's frontmatter.
    _skill_options: list[str] = []
    for _sname, _sdir in _skill_map.items():
        _fm, _ = _read_skill(skills_dir / _sdir)
        _skill_options.append(f"{_sname}: {_fm.get('description', '').strip()}")
    _skill_name_doc = "One of the following:\n            " + "\n            ".join(
        _skill_options
    )

    async def load_skill(skill_name: str, tool_context: ToolContext) -> dict[str, Any]:
        """Load a skill and its tool schemas into the conversation.

        Call this before using any skill-specific tools. The returned dict
        contains the skill instructions and the JSON schemas for every tool
        in that skill — read them carefully before calling execute_mcp_action.

        Args:
            skill_name: {skill_name_doc}
        """
        logger.info(
            "load_skill called: skill_name=%s loaded_skills=%s",
            skill_name,
            tool_context.state.get("loaded_skills", []),
        )
        if skill_name not in _skill_map:
            valid = ", ".join(sorted(_skill_map))
            return {"error": f"Unknown skill '{skill_name}'. Valid skills: {valid}."}

        fm, body = _read_skill(skills_dir / _skill_map[skill_name])
        tool_names: list[str] = fm.get("tools", [])
        skill_display_name: str = fm.get("name", skill_name)
        skill_desc: str = fm.get("description", "").strip()

        all_mcp_tools = await get_toolset().get_tools()
        tool_declarations: list[dict[str, Any]] = []
        for mcp_tool in all_mcp_tools:
            if mcp_tool.name in tool_names:
                raw_tool = mcp_tool.raw_mcp_tool
                raw_schema = raw_tool.inputSchema if raw_tool.inputSchema else {}
                description = mcp_tool.description or ""
                enriched = _enrich_schema_with_descriptions(description, raw_schema)
                tool_declarations.append(
                    {
                        "name": mcp_tool.name,
                        "description": description,
                        "parameters": _convert_schema(enriched),
                    }
                )

        resolved_names = [t["name"] for t in tool_declarations]
        missing = [n for n in tool_names if n not in resolved_names]
        logger.info(
            "load_skill '%s': resolved tools=%s%s",
            skill_name,
            resolved_names,
            f"  MISSING_FROM_MCP={missing}" if missing else "",
        )

        payload = {
            "skill_name": skill_display_name,
            "description": skill_desc,
            "instructions": body.strip(),
            "tool_schemas": tool_declarations,
        }

        loaded: list[str] = tool_context.state.get("loaded_skills", [])
        if skill_name not in loaded:
            loaded.append(skill_name)
        tool_context.state["loaded_skills"] = loaded

        return payload

    assert "{skill_name_doc}" in (load_skill.__doc__ or ""), (
        "load_skill docstring must contain the '{skill_name_doc}' placeholder"
    )
    load_skill.__doc__ = (load_skill.__doc__ or "").replace(
        "{skill_name_doc}", _skill_name_doc
    )

    async def execute_mcp_action(
        action_name: str,
        arguments: dict[str, Any],
        tool_context: ToolContext,
    ) -> str:
        """Execute a Billy MCP tool by name with the given arguments.

        Only call this after load_skill has loaded the relevant skill. Use the
        exact tool name and argument keys from the schema returned by load_skill.

        Args:
            action_name: Exact MCP tool name (e.g. 'create_invoice', 'list_customers').
            arguments: Dict of arguments matching the tool's input schema.
        """
        logger.info(
            "execute_mcp_action called: action=%s args=%s", action_name, arguments
        )
        # Security: allow tools from preloaded skills (always) and lazy-loaded skills
        # (only after load_skill has been called for that skill).
        # SKILL.md reads are served from the lru_cache — no disk I/O per call.
        allowed_tools: set[str] = set(_preloaded_tools)
        loaded: list[str] = tool_context.state.get("loaded_skills", [])
        for sname in loaded:
            fm, _ = _read_skill(skills_dir / _skill_map[sname])
            allowed_tools.update(fm.get("tools", []))

        logger.info(
            "execute_mcp_action '%s': loaded_skills=%s allowed_tools=%s",
            action_name,
            loaded,
            sorted(allowed_tools),
        )

        if action_name not in allowed_tools:
            for sname, sdir in _skill_map.items():
                fm, _ = _read_skill(skills_dir / sdir)
                if action_name in fm.get("tools", []):
                    msg = (
                        f"Skill '{sname}' is not loaded. "
                        f"Call load_skill('{sname}') first to get the instructions and tool schemas, "
                        f"then retry execute_mcp_action('{action_name}', ...)."
                    )
                    logger.warning(
                        "execute_mcp_action: skill not loaded for tool '%s' → %s",
                        action_name,
                        msg,
                    )
                    return msg
            msg = (
                f"Tool '{action_name}' not found in any known skill. "
                f"Valid skills: {', '.join(sorted(_skill_map))}."
            )
            logger.warning(msg)
            return msg

        all_mcp_tools = await get_toolset().get_tools()
        target = next((t for t in all_mcp_tools if t.name == action_name), None)
        if target is None:
            return f"ERROR: Tool '{action_name}' not found in the MCP server."

        input_schema = target.raw_mcp_tool.inputSchema or {}
        try:
            jsonschema.validate(instance=arguments, schema=input_schema)
        except jsonschema.ValidationError as e:
            return f"ERROR: Invalid arguments for '{action_name}': {e.message}"

        try:
            result = await target.run_async(args=arguments, tool_context=tool_context)
        except Exception:
            tb = traceback.format_exc()
            logger.error(
                "execute_mcp_action '%s' raised an exception:\n%s", action_name, tb
            )
            return f"ERROR: Tool '{action_name}' raised an exception: {tb}"

        if isinstance(result, str):
            return result
        # Prefer structuredContent (typed, parsed form) over the text fallback.
        structured = extract_structured_content(result)
        if structured is not None:
            return json.dumps(structured, ensure_ascii=False, indent=2)
        return json.dumps(result, ensure_ascii=False, indent=2)

    async def sync_loaded_skills(
        callback_context: CallbackContext,
        _llm_request: LlmRequest,
    ) -> None:
        """Drop loaded_skills entries whose load_skill events are no longer in history.

        After history compaction the load_skill function-call events are replaced
        by a summary. This callback detects that and clears the corresponding
        entries from state so the model must call load_skill again to get the
        tool schemas back into context.
        """
        current_loaded: list[str] = list(
            callback_context.state.get("loaded_skills", [])
        )
        n_events = len(callback_context.session.events)
        logger.info(
            "sync_loaded_skills: state loaded_skills=%s  session_events=%d",
            current_loaded,
            n_events,
        )

        skills_in_events: set[str] = set()
        for event in callback_context.session.events:
            if not (event.content and event.content.parts):
                continue
            for part in event.content.parts:
                if part.function_call and part.function_call.name == "load_skill":
                    skill_name = (part.function_call.args or {}).get("skill_name")
                    if skill_name and skill_name in _skill_map:
                        skills_in_events.add(skill_name)

        new_loaded = [s for s in current_loaded if s in skills_in_events]
        if new_loaded != current_loaded:
            removed = set(current_loaded) - set(new_loaded)
            logger.info(
                "sync_loaded_skills: load_skill events gone after compaction → clearing %s",
                removed,
            )
            callback_context.state["loaded_skills"] = new_loaded
        else:
            logger.info(
                "sync_loaded_skills: skills in events=%s  no change needed",
                skills_in_events,
            )

    return load_skill, execute_mcp_action, sync_loaded_skills
