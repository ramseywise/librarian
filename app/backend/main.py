from __future__ import annotations

import asyncio
import contextlib
import json
import os
from collections.abc import AsyncIterator, Callable
from pathlib import Path
from typing import Any, Literal, Self

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect

load_dotenv(Path(__file__).parent.parent.parent / ".env")
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, model_validator

from shared.log_config import configure_logging, get_logger

from .agent import run_agent_stream
from .courses import router as courses_router
from .courses import warm_catalog
from .wiki_parser import parse_wiki, tag_shared_edges

# At import, not in a main(): uvicorn imports this module as an ASGI app and never
# calls an entry point of ours. Must precede the first log call from any route.
configure_logging()
log = get_logger(__name__)

WIKI_DIR = Path(__file__).parent.parent.parent / "data" / "wiki"

_ws_clients: list[WebSocket] = []

# Strong references to fire-and-forget tasks and executor futures so GC can't drop them
_background_tasks: set[asyncio.Future[Any]] = set()


# Seconds of wiki quiet before the course catalog is rebuilt. An ingest writes many pages
# in bursts; each rebuild takes seconds under the catalog lock, so coalesce them.
CATALOG_REWARM_DELAY_S = 10.0
_rewarm_handle: asyncio.TimerHandle | None = None


def _in_background(fn: Callable[[], None]) -> None:
    """Run a blocking startup job in the default thread executor, holding a reference."""
    fut = asyncio.get_running_loop().run_in_executor(None, fn)
    _background_tasks.add(fut)
    fut.add_done_callback(_background_tasks.discard)


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
        # A wiki change invalidates the course catalog (lesson ↔ concept links); rebuild
        # it once the burst of changes settles rather than on the next request.
        _schedule_catalog_rewarm()


def _schedule_catalog_rewarm() -> None:
    global _rewarm_handle
    if _rewarm_handle is not None:
        _rewarm_handle.cancel()
    _rewarm_handle = asyncio.get_running_loop().call_later(
        CATALOG_REWARM_DELAY_S, _in_background, warm_catalog
    )


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Both startup jobs need the `api` extra (shared.embeddings -> numpy/sentence-transformers,
    # _watch_and_broadcast -> watchfiles), and both are optimizations: warmup only
    # pre-loads a model, the watcher only pushes live graph updates. Neither is required
    # for the routes to answer. Degrade instead of failing startup, because CI installs
    # `--group dev` with no extras and TestClient-as-context-manager runs this lifespan —
    # a hard import here failed every test in tests/app/test_writeback_security.py.
    # Course catalog: the cold build takes seconds (frontmatter for ~760 lessons plus
    # concept linking). Build it off the event loop so the first /api/courses request is
    # a cache hit. Needs no extra; warm_catalog() never raises, so startup cannot fail.
    # LIBRARIAN_SKIP_WARMUP=1 (set by tests/conftest.py) skips both warmups so tests that
    # enter the lifespan don't build the real catalog or load the embedding model.
    skip_warmup = os.environ.get("LIBRARIAN_SKIP_WARMUP") == "1"
    if not skip_warmup:
        _in_background(warm_catalog)
    try:
        from watchfiles import awatch

        from shared.embeddings import warmup
    except ImportError as e:
        log.warning("startup_jobs_skipped", reason="api extra not installed", error=str(e))
    else:
        # Warmup in background so server accepts connections immediately
        if not skip_warmup:
            _in_background(warmup)
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
app.include_router(courses_router)


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
async def get_graph(edges: Literal["wikilink", "all"] = "wikilink") -> dict[str, Any]:
    """Same payload as the /ws graph_update. `?edges=all` adds the tag-shared edges the
    UI derives client-side, for scripts that want the full edge set from the server."""
    graph = parse_wiki()
    if edges == "all":
        graph["edges"] = graph["edges"] + tag_shared_edges(graph["nodes"], graph["domains"])
    return graph


# Sync routes (threadpool): both block on embeddings, and compute_embeddings serialises
# on a lock the course-catalog build may hold — never wait on it from the event loop.
@app.get("/api/edges/semantic")
def get_semantic_edges(threshold: float = 0.65) -> list[dict]:
    from shared.embeddings import semantic_edges

    return semantic_edges(threshold)


@app.post("/api/layout/umap")
def umap_layout() -> dict[str, dict]:
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


# Per-message bound at the boundary; the agent applies the tighter count/total-chars
# trim (agent.MAX_HISTORY_TURNS / MAX_HISTORY_CHARS). This cap only rejects payloads
# no real chat produces. The list cap is loose for the same reason — the client may
# send its whole transcript and let the agent keep the tail.
_MAX_MESSAGE_CHARS = 32_000
_MAX_HISTORY_ITEMS = 200


class ChatTurn(BaseModel):
    """One prior text-only turn. Tool blocks never cross the wire."""

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=_MAX_MESSAGE_CHARS)


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=_MAX_MESSAGE_CHARS)
    history: list[ChatTurn] = Field(default_factory=list, max_length=_MAX_HISTORY_ITEMS)

    @model_validator(mode="after")
    def _alternating(self) -> Self:
        # The new query is appended as the next user turn, so history must alternate
        # user/assistant and end on assistant. Reject rather than repair: a malformed
        # transcript means a client bug, and silently merging turns would hide it.
        for i, turn in enumerate(self.history):
            expected = "user" if i % 2 == 0 else "assistant"
            if turn.role != expected:
                raise ValueError(f"history[{i}] must have role {expected!r}")
        if self.history and self.history[-1].role != "assistant":
            raise ValueError("history must end with an assistant turn")
        return self


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest) -> StreamingResponse:
    history = [t.model_dump() for t in req.history]

    async def generate() -> AsyncIterator[str]:
        async for event in run_agent_stream(req.query, history):
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
