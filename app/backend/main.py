from __future__ import annotations

import asyncio
import contextlib
import json
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect

load_dotenv(Path(__file__).parent.parent.parent / ".env")
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from app.log_config import configure_logging

from .agent import run_agent_stream
from .embeddings import semantic_edges, warmup
from .wiki_parser import parse_wiki

# At import, not in a main(): uvicorn imports this module as an ASGI app and never
# calls an entry point of ours. Must precede the first log call from any route.
configure_logging()

WIKI_DIR = Path(__file__).parent.parent.parent / "wiki"

_ws_clients: list[WebSocket] = []

# Strong references to fire-and-forget tasks so GC can't cancel them
_background_tasks: set[asyncio.Task] = set()


async def _watch_and_broadcast() -> None:
    from watchfiles import awatch

    async for _ in awatch(str(WIKI_DIR)):
        graph = parse_wiki()
        dead = []
        for ws in list(_ws_clients):
            try:
                await ws.send_json({"type": "graph_update", "data": graph})
            except Exception:
                dead.append(ws)
        for ws in dead:
            with contextlib.suppress(ValueError):
                _ws_clients.remove(ws)


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Warmup in background so server accepts connections immediately
    asyncio.get_event_loop().run_in_executor(None, warmup)
    task = asyncio.create_task(_watch_and_broadcast())
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    yield


app = FastAPI(title="Librarian Graph API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    _ws_clients.append(ws)
    try:
        await ws.send_json({"type": "graph_update", "data": parse_wiki()})
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        with contextlib.suppress(ValueError):
            _ws_clients.remove(ws)


@app.get("/api/graph")
async def get_graph() -> dict[str, Any]:
    return parse_wiki()


@app.get("/api/edges/semantic")
async def get_semantic_edges(threshold: float = 0.65) -> list[dict]:
    return semantic_edges(threshold)


@app.post("/api/layout/umap")
async def umap_layout() -> dict[str, dict]:
    # Imported lazily: umap-learn pulls in numba, which requires numpy<2.5 while
    # pyproject.toml pins numpy>=2.5.1. A module-level import took the entire API
    # down (including /api/graph) over one optional layout endpoint.
    try:
        from .umap_layout import compute_umap_positions
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"UMAP layout unavailable — umap-learn/numba vs numpy conflict: {e}",
        ) from e
    return compute_umap_positions()


class ChatRequest(BaseModel):
    query: str


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest) -> StreamingResponse:
    async def generate() -> AsyncIterator[str]:
        async for event in run_agent_stream(req.query):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# response_model=None: the return union (JSONResponse | dict) is not a valid
# Pydantic field type, and FastAPI rejects the route at import time without this.
@app.post("/api/writeback", response_model=None)
async def writeback(body: dict[str, str]) -> JSONResponse | dict[str, str]:
    page_id = body.get("page_id", "")
    link_to = body.get("link_to", "")
    md_file = next(WIKI_DIR.rglob(f"{page_id}.md"), None)
    if not md_file:
        return JSONResponse(status_code=404, content={"error": "page not found"})
    content = md_file.read_text()
    if "## See Also" not in content:
        content += "\n\n## See Also\n"
    if f"[[{link_to}]]" not in content:
        content += f"- [[{link_to}]]\n"
    md_file.write_text(content)
    return {"status": "ok"}
