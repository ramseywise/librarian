"""agent_gateway — generic FastAPI server for A2UI-capable ADK agents.

Endpoints:
  POST /chat            Trigger a new agent turn (fires background task)
  GET  /chat/stream     SSE stream for a session
  GET  /agents          List available agents
  POST /agents/switch   Switch the active agent for a session
"""

from __future__ import annotations

import asyncio
import logging
import pathlib
import sys

from dotenv import load_dotenv

load_dotenv()

import uvicorn  # noqa: E402
from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import StreamingResponse  # noqa: E402
from pydantic import BaseModel  # noqa: E402

# Ensure repo root is on sys.path so agents.* imports resolve.
_REPO_ROOT = pathlib.Path(__file__).parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from .registry import AGENT_DESCRIPTIONS  # noqa: E402
from .session_manager import session_manager  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Agent Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    session_id: str
    request_id: str
    message: str
    agent_name: str = "a2ui_mcp"


class SwitchRequest(BaseModel):
    session_id: str
    agent_name: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.post("/chat")
async def post_chat(req: ChatRequest):
    """Accept a user message and start an ADK turn as a background task.

    The client must open GET /chat/stream before calling this endpoint so
    that SSE events are not lost.
    """
    # Ensure session exists before the background task starts.
    session_manager.get_or_create_session(req.session_id, req.agent_name)
    asyncio.create_task(
        session_manager.run_turn(req.session_id, req.request_id, req.message)
    )
    return {"ok": True}


@app.get("/chat/stream")
async def get_chat_stream(session_id: str, agent_name: str = "a2ui_mcp"):
    """SSE stream for a session.

    Creates the session (and queue) if it does not yet exist, which enables
    the client to open this stream before posting the first message.
    """
    state = session_manager.get_or_create_session(session_id, agent_name)

    async def event_generator():
        # Send an initial heartbeat so the browser EventSource knows the
        # connection is live.
        yield 'data: {"type": "connected"}\n\n'
        while True:
            try:
                payload = await asyncio.wait_for(state.queue.get(), timeout=30.0)
                yield f"data: {payload}\n\n"
            except asyncio.TimeoutError:
                # Keep-alive comment to prevent proxy / browser timeout.
                yield ": keep-alive\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/agents")
async def list_agents():
    """Return the list of registered agents."""
    return [
        {"name": name, "description": desc} for name, desc in AGENT_DESCRIPTIONS.items()
    ]


@app.post("/agents/switch")
async def switch_agent(req: SwitchRequest):
    """Switch the active agent for a session."""
    if req.agent_name not in AGENT_DESCRIPTIONS:
        raise HTTPException(status_code=404, detail=f"Unknown agent: {req.agent_name}")
    session_manager.switch_agent(req.session_id, req.agent_name)
    return {"ok": True}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(
        "agent_gateway.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
    )
