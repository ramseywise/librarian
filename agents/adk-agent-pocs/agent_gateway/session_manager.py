"""Per-session ADK Runner management and SSE event queue.

Each session gets one Runner and one asyncio.Queue.  The POST /chat endpoint
fires a background task that runs the ADK turn and puts SSE events onto the
queue; the GET /chat/stream endpoint reads from the queue and forwards events
to the browser.

SSE/POST ordering: the client MUST open the SSE stream before posting the
message. session_manager guarantees the queue exists as soon as
get_or_create_session() is called, which happens when the SSE stream is opened.
"""

from __future__ import annotations

import asyncio
import json
import logging
import pathlib
import sys
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# Ensure repo root is on sys.path so agents.* imports resolve.
_REPO_ROOT = pathlib.Path(__file__).parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from google.adk.apps.app import App  # noqa: E402
from google.adk.runners import Runner  # noqa: E402
from google.adk.sessions import InMemorySessionService  # noqa: E402
from google.genai import types  # noqa: E402

from .a2ui_parser import DELIMITER, parse_a2ui_response  # noqa: E402
from .registry import get_agent  # noqa: E402

_DEFAULT_AGENT = "a2ui_mcp"


@dataclass
class SessionState:
    runner: Runner
    agent_name: str
    queue: asyncio.Queue = field(default_factory=asyncio.Queue)


class SessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}

    def get_or_create_session(
        self, session_id: str, agent_name: str = _DEFAULT_AGENT
    ) -> SessionState:
        if session_id not in self._sessions:
            self._sessions[session_id] = self._make_session(session_id, agent_name)
        return self._sessions[session_id]

    def switch_agent(self, session_id: str, agent_name: str) -> None:
        """Replace the runner for an existing session with a new agent."""
        state = self._sessions.get(session_id)
        if state is None or state.agent_name == agent_name:
            return
        new_state = self._make_session(session_id, agent_name)
        # Preserve the existing queue so the SSE stream doesn't miss events.
        new_state.queue = state.queue
        self._sessions[session_id] = new_state

    def _make_session(self, session_id: str, agent_name: str) -> SessionState:
        agent_or_app = get_agent(agent_name)
        if isinstance(agent_or_app, App):
            runner = Runner(
                app=agent_or_app,
                session_service=InMemorySessionService(),
                auto_create_session=True,
            )
        else:
            runner = Runner(
                agent=agent_or_app,
                app_name="agent_gateway",
                session_service=InMemorySessionService(),
                auto_create_session=True,
            )
        return SessionState(runner=runner, agent_name=agent_name)

    async def run_turn(self, session_id: str, request_id: str, message: str) -> None:
        """Run one ADK turn and put SSE events onto the session queue."""
        state = self._sessions.get(session_id)
        if state is None:
            logger.error("run_turn called for unknown session %s", session_id)
            return

        new_message = types.Content(
            role="user",
            parts=[types.Part(text=message)],
        )

        response_buffer = ""
        last_sent_pos = 0
        delimiter_found = False

        # --- Timing tracking ---
        turn_start = time.monotonic()
        phase_start = turn_start
        timing_steps: list[dict[str, Any]] = []
        llm_count = 0
        step_num = 0
        first_token_ms: int | None = None
        in_llm_phase = True  # starts waiting for first model response
        llm_count = 1

        def end_phase(label: str, phase_type: str) -> None:
            nonlocal phase_start
            now = time.monotonic()
            timing_steps.append(
                {
                    "label": label,
                    "start_ms": int((phase_start - turn_start) * 1000),
                    "duration_ms": max(1, int((now - phase_start) * 1000)),
                    "type": phase_type,
                }
            )
            phase_start = now

        _TURN_TIMEOUT = 120  # seconds; guards against hung MCP tool calls

        try:
            async with asyncio.timeout(_TURN_TIMEOUT):
                async for event in state.runner.run_async(
                    user_id="user",
                    session_id=session_id,
                    new_message=new_message,
                ):
                    if not event.content or not event.content.parts:
                        continue

                    # Partition parts by kind so parallel calls are grouped.
                    text_parts = [p.text for p in event.content.parts if p.text]
                    call_parts = [
                        p.function_call for p in event.content.parts if p.function_call
                    ]
                    resp_parts = [
                        p.function_response
                        for p in event.content.parts
                        if p.function_response
                    ]

                    logger.info(
                        "[DBG] event author=%r is_final=%r texts=%d calls=%d resps=%d",
                        getattr(event, "author", None),
                        getattr(event, "is_final_response", lambda: None)(),
                        len(text_parts),
                        len(call_parts),
                        len(resp_parts),
                    )

                    # --- Function calls: close LLM phase, emit tool_calls ---
                    if call_parts:
                        label = "LLM" if llm_count == 1 else f"LLM {llm_count}"
                        end_phase(label, "llm")
                        in_llm_phase = False
                        step_num += 1
                        call_data = [
                            {
                                "id": fc.id or fc.name,
                                "name": fc.name,
                                "args": fc.args or {},
                            }
                            for fc in call_parts
                        ]
                        logger.info(
                            "[DBG] function_call(s): %r", [c["name"] for c in call_data]
                        )
                        await state.queue.put(
                            json.dumps(
                                {
                                    "type": "tool_calls",
                                    "request_id": request_id,
                                    "step": step_num,
                                    "calls": call_data,
                                }
                            )
                        )

                    # --- Function responses: close tool phase, emit tool_results ---
                    if resp_parts:
                        names = [fr.name for fr in resp_parts]
                        truncated = [
                            n[:12] + "…" if len(n) > 12 else n for n in names[:2]
                        ]
                        tool_label = ", ".join(truncated)
                        if len(names) > 2:
                            tool_label += f" +{len(names) - 2}"
                        end_phase(tool_label, "tool")
                        in_llm_phase = True
                        llm_count += 1
                        step_num += 1
                        result_data = []
                        for fr in resp_parts:
                            resp = fr.response
                            if isinstance(resp, dict) and "output" in resp:
                                result: Any = resp["output"]
                            elif isinstance(resp, dict):
                                result = resp
                            else:
                                result = str(resp) if resp is not None else ""
                            result_data.append(
                                {
                                    "id": fr.id or fr.name,
                                    "name": fr.name,
                                    "result": result,
                                }
                            )
                        logger.info(
                            "[DBG] function_response(s): %r",
                            [r["name"] for r in result_data],
                        )
                        await state.queue.put(
                            json.dumps(
                                {
                                    "type": "tool_results",
                                    "request_id": request_id,
                                    "step": step_num,
                                    "results": result_data,
                                }
                            )
                        )

                    # --- Text parts: stream to client ---
                    for text in text_parts:
                        if first_token_ms is None:
                            first_token_ms = int((time.monotonic() - turn_start) * 1000)
                        logger.info(
                            "[DBG] text part (len=%d): %r", len(text), text[:120]
                        )
                        response_buffer += text
                        if not delimiter_found:
                            delim_pos = response_buffer.find(DELIMITER)
                            if delim_pos >= 0:
                                delimiter_found = True
                                to_send = response_buffer[last_sent_pos:delim_pos]
                                if to_send:
                                    await state.queue.put(
                                        json.dumps(
                                            {
                                                "type": "text_chunk",
                                                "request_id": request_id,
                                                "text": to_send,
                                            }
                                        )
                                    )
                                last_sent_pos = len(response_buffer)
                            else:
                                to_send = response_buffer[last_sent_pos:]
                                if to_send:
                                    await state.queue.put(
                                        json.dumps(
                                            {
                                                "type": "text_chunk",
                                                "request_id": request_id,
                                                "text": to_send,
                                            }
                                        )
                                    )
                                last_sent_pos = len(response_buffer)

            logger.info("[DBG] run_async finished. buffer len=%d", len(response_buffer))

            # Close the final LLM phase.
            if in_llm_phase:
                label = "LLM" if llm_count == 1 else f"LLM {llm_count}"
                end_phase(label, "llm")

            total_ms = int((time.monotonic() - turn_start) * 1000)

            # Parse A2UI from the complete buffered response.
            prose, a2ui_messages = parse_a2ui_response(response_buffer)
            if a2ui_messages:
                await state.queue.put(
                    json.dumps(
                        {
                            "type": "a2ui",
                            "request_id": request_id,
                            "messages": a2ui_messages,
                        }
                    )
                )

            # Emit timing so the client can render the response-time bar chart.
            await state.queue.put(
                json.dumps(
                    {
                        "type": "timing",
                        "request_id": request_id,
                        "total_ms": total_ms,
                        "first_token_ms": first_token_ms,
                        "steps": timing_steps,
                    }
                )
            )

        except TimeoutError:
            logger.error(
                "ADK turn timed out after %ds for session %s",
                _TURN_TIMEOUT,
                session_id,
            )
            await state.queue.put(
                json.dumps(
                    {
                        "type": "error",
                        "request_id": request_id,
                        "message": "The agent took too long to respond. Please try again.",
                    }
                )
            )
        except Exception as exc:
            logger.exception("ADK runner error for session %s", session_id)
            await state.queue.put(
                json.dumps(
                    {
                        "type": "error",
                        "request_id": request_id,
                        "message": str(exc),
                    }
                )
            )

        await state.queue.put(json.dumps({"type": "done", "request_id": request_id}))


# Module-level singleton used by main.py
session_manager = SessionManager()
