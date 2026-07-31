from __future__ import annotations

import asyncio
import contextlib
import json
from collections.abc import AsyncIterator, Callable
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect

load_dotenv(Path(__file__).parent.parent.parent / ".env")
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from app.log_config import configure_logging, get_logger

from .agent import run_agent_stream
from .wiki_parser import parse_wiki

# At import, not in a main(): uvicorn imports this module as an ASGI app and never
# calls an entry point of ours. Must precede the first log call from any route.
configure_logging()
log = get_logger(__name__)

WIKI_DIR = Path(__file__).parent.parent.parent / "data" / "wiki"

_ws_clients: list[WebSocket] = []

# Strong references to fire-and-forget tasks so GC can't cancel them
_background_tasks: set[asyncio.Task] = set()


async def _watch_and_broadcast(awatch: Callable[[str], AsyncIterator[object]]) -> None:
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
    # Both startup jobs need the `api` extra (.embeddings -> numpy/sentence-transformers,
    # _watch_and_broadcast -> watchfiles), and both are optimizations: warmup only
    # pre-loads a model, the watcher only pushes live graph updates. Neither is required
    # for the routes to answer. Degrade instead of failing startup, because CI installs
    # `--group dev` with no extras and TestClient-as-context-manager runs this lifespan —
    # a hard import here failed every test in tests/unit/test_writeback_security.py.
    try:
        from watchfiles import awatch

        from .embeddings import warmup
    except ImportError as e:
        log.warning("startup_jobs_skipped", reason="api extra not installed", error=str(e))
    else:
        # Warmup in background so server accepts connections immediately
        asyncio.get_event_loop().run_in_executor(None, warmup)
        task = asyncio.create_task(_watch_and_broadcast(awatch))
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
    from .embeddings import semantic_edges

    return semantic_edges(threshold)


@app.post("/api/layout/umap")
async def umap_layout() -> dict[str, dict]:
    # Imported lazily: umap-learn pulls in numba, which requires numpy<2.5. When
    # pyproject.toml still pinned numpy>=2.5.1 a module-level import took the entire
    # API down (including /api/graph) over one optional layout endpoint. The pin now
    # reads numpy>=2.4,<2.5, but the lazy import stays — the extra is still optional.
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

    # Reject `..` segments and absolute paths before touching the filesystem.
    # rglob alone does not constrain results to WIKI_DIR — an injected page_id
    # like "../../etc/passwd" or an absolute path would let a caller read or
    # overwrite arbitrary files. The resolve()/is_relative_to() check below is
    # the same guard applied in server.py (list_pages) and agent.py (_read_page).
    if not page_id or ".." in page_id or page_id.startswith("/"):
        return JSONResponse(status_code=400, content={"error": "invalid page_id"})

    md_file = next(WIKI_DIR.rglob(f"{page_id}.md"), None)
    if not md_file:
        return JSONResponse(status_code=404, content={"error": "page not found"})

    # Second check: resolve symlinks / relative components and confirm the
    # matched file actually lives inside the wiki root.
    if not md_file.resolve().is_relative_to(WIKI_DIR.resolve()):
        return JSONResponse(status_code=400, content={"error": "invalid page_id"})

    content = md_file.read_text()
    if "## See Also" not in content:
        content += "\n\n## See Also\n"
    if f"[[{link_to}]]" not in content:
        content += f"- [[{link_to}]]\n"
    md_file.write_text(content)
    return {"status": "ok"}
