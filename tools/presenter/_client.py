"""Anthropic client helpers — replaces the missing core.client module.

Same reason as _settings.py: tools/presenter/ was copied in from a repo with a
core/ package that has never existed here. The two functions below are
reconstructed from their call sites in outline.py, slide_writer.py, and
viz_classifier.py — that is the whole surface presenter uses.
"""

from __future__ import annotations

import json
import os
from typing import Any

import anthropic
import structlog

log = structlog.get_logger(__name__)


def create_client() -> anthropic.Anthropic:
    """Anthropic client from ANTHROPIC_API_KEY.

    Raises rather than returning a client that fails later inside a deck run,
    which would surface as a stack trace several LLM calls deep.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set — required for presenter LLM calls.")
    return anthropic.Anthropic(api_key=api_key)


def _strip_fences(text: str) -> str:
    """Drop a ```json fence if the model wrapped its output in one."""
    text = text.strip()
    if text.startswith("```"):
        text = "\n".join(text.split("\n")[1:]).split("```")[0].strip()
    return text


def parse_json_response(
    client: anthropic.Anthropic,
    text: str,
    model: str,
    system: str,
) -> Any:  # noqa: ANN401 — callers expect dict or list depending on the prompt
    """Parse a model response as JSON, asking the model to repair it once if needed.

    client/model/system are taken so a malformed response can be sent back for
    repair instead of failing the deck run — the reason the signature carries
    them at all. Returns dict or list, whichever the prompt asked for.
    """
    try:
        return json.loads(_strip_fences(text))
    except json.JSONDecodeError as first_error:
        log.warning("presenter.json_repair", error=str(first_error))

    repair = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system,
        messages=[
            {
                "role": "user",
                "content": (
                    "Your previous reply was not valid JSON. Return the same content as "
                    "a single valid JSON value, with no prose and no code fence:\n\n" + text
                ),
            }
        ],
    )
    repaired = repair.content[0].text if repair.content else ""
    try:
        return json.loads(_strip_fences(repaired))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Model did not return valid JSON after one repair attempt: {exc}"
        ) from exc
