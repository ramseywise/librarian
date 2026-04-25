from __future__ import annotations

import logging
from typing import Any

from google.adk.models.gemini_llm_connection import GeminiLlmConnection
from google.genai import types


def patch_live_realtime_input_routing() -> None:
    """Route live realtime blobs through modality-specific input fields."""
    if getattr(
        GeminiLlmConnection,
        "_adk_agent_samples_live_realtime_input_patch",
        False,
    ):
        return

    logger = logging.getLogger(__name__)
    original_send_realtime = GeminiLlmConnection.send_realtime

    async def _patched_send_realtime(
        self: GeminiLlmConnection,
        input: Any,
    ) -> None:
        if isinstance(input, types.Blob):
            mime_type = (input.mime_type or "").lower()
            if mime_type.startswith("audio/"):
                logger.debug("Sending live audio via realtime_input.audio")
                await self._gemini_session.send_realtime_input(audio=input)
                return
            if mime_type.startswith("image/") or mime_type.startswith("video/"):
                logger.debug("Sending live video via realtime_input.video")
                await self._gemini_session.send_realtime_input(video=input)
                return

        await original_send_realtime(self, input)

    GeminiLlmConnection.send_realtime = _patched_send_realtime
    GeminiLlmConnection._adk_agent_samples_live_realtime_input_patch = True
