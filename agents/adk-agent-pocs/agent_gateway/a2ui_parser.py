"""Parse A2UI messages from a completed LLM response.

Called once per turn with the full buffered response — not per streaming chunk.
The delimiter and JSON body regularly span chunk boundaries, so per-chunk
parsing silently drops valid payloads.
"""

from __future__ import annotations

import json
import logging
import pathlib
import sys

import jsonschema

logger = logging.getLogger(__name__)

DELIMITER = "---a2ui_JSON---"

# Load schema from repo root (same file used by agents/a2ui_mcp/a2ui_schema.py).
_REPO_ROOT = pathlib.Path(__file__).parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_schema_path = _REPO_ROOT / "a2ui_schema.json"
_A2UI_SCHEMA: dict | None = None

try:
    _A2UI_SCHEMA = json.loads(_schema_path.read_text(encoding="utf-8"))
except FileNotFoundError:
    logger.warning(
        "a2ui_schema.json not found at %s — validation disabled", _schema_path
    )


def parse_a2ui_response(full_response: str) -> tuple[str, list[dict] | None]:
    """Split a completed LLM response into prose and A2UI messages.

    Returns:
        (conversational_text, a2ui_messages_or_None)

    If JSON is invalid or missing, returns (prose, None) so the user still
    sees the text portion of the response.
    """
    if DELIMITER not in full_response:
        return full_response.strip(), None

    prose, _, json_part = full_response.partition(DELIMITER)
    try:
        # Use raw_decode so any trailing text (e.g. a bridge sentence the model
        # appended after the closing ']') is silently ignored instead of causing
        # an "Extra data" JSONDecodeError.
        messages, _ = json.JSONDecoder().raw_decode(json_part.strip())
        if _A2UI_SCHEMA is not None:
            jsonschema.validate(instance=messages, schema=_A2UI_SCHEMA)
        logger.info(
            "[DBG] A2UI messages parsed OK (%d messages): %s",
            len(messages),
            json.dumps(messages)[:2000],
        )
        return prose.strip(), messages
    except json.JSONDecodeError as exc:
        logger.warning("A2UI JSON parse error: %s", exc)
        return prose.strip(), None
    except jsonschema.ValidationError as exc:
        logger.warning("A2UI schema validation error: %s", exc.message)
        return prose.strip(), None
