from __future__ import annotations

import asyncio
import contextlib
import json
import os
import time
from collections.abc import AsyncIterator, Callable
from typing import Any, Literal, Self

# Before the heavy imports below, so the startup log covers them too.
_PROCESS_T0 = time.perf_counter()

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, model_validator

from librarian import retrieval
from librarian.agent import run_agent_stream
from librarian.api.routers.courses import router as courses_router
from librarian.api.routers.curriculum import router as curriculum_router
from librarian.api.routers.glossary import router as glossary_router
from librarian.api.routers.wiki_health import router as wiki_health_router
from librarian.api.security import (
    WS_SUBPROTOCOL,
    RequestLogMiddleware,
    SecurityHeadersMiddleware,
    build_csp,
    chat_limiter,
    inline_script_hashes,
    require_token,
)
from librarian.api.startup import find_problems
from librarian.config import get_settings
from librarian.courses.catalog import warm_catalog
from librarian.courses.curriculum import write_snapshot
from librarian.log_config import configure_logging, get_logger
from librarian.observability import setup as setup_observability
from librarian.pricing import TokenUsage
from librarian.wiki.parser import parse_wiki, public_page_ids, tag_shared_edges

# At import, not in a main(): uvicorn imports this module as an ASGI app and never
# calls an entry point of ours. Must precede the first log call from any route.
configure_logging()
log = get_logger(__name__)

WIKI_DIR = get_settings().wiki_dir

_ws_clients: list[WebSocket] = []

# Strong references to fire-and-forget tasks and executor futures so GC can't drop them
_background_tasks: set[asyncio.Future[Any]] = set()


# Seconds of wiki quiet before the course catalog is rebuilt. An ingest writes many pages
# in bursts; each rebuild takes seconds under the catalog lock, so coalesce them.
CATALOG_REWARM_DELAY_S = 10.0
_rewarm_handle: asyncio.TimerHandle | None = None
# Seconds before the wiki watcher restarts after the watch itself raised.
WATCHER_RESTART_DELAY_S = 5.0


def _in_background(fn: Callable[[], None]) -> None:
    """Run a blocking startup job in the default thread executor, holding a reference."""
    fut = asyncio.get_running_loop().run_in_executor(None, fn)
    _background_tasks.add(fut)
    fut.add_done_callback(_background_tasks.discard)


def _run_in_order(jobs: list[Callable[[], None]]) -> None:
    for job in jobs:
        job()


# The index state the lifespan reports: "building" until the background job has opened (and, if
# behind the files, rebuilt) it, then "ready", or "failed". /readyz only reads this: a probe never
# starts a rebuild. "skipped" is for runs that start no warmup (tests): the probe then checks the
# file without building it.
_index_state = "building"


def _build_index() -> None:
    global _index_state
    try:
        retrieval.open_index().close()
        _index_state = "ready"
    except Exception as exc:
        _index_state = "failed"
        log.error("api.startup.index_failed", error=str(exc), error_type=type(exc).__name__)


def _warm_course_data() -> None:
    warm_catalog()
    write_snapshot()


async def _broadcast_graph() -> None:
    graph = await asyncio.to_thread(parse_wiki)
    dead = []
    for ws in list(_ws_clients):
        try:
            await ws.send_json({"type": "graph_update", "data": graph})
        except Exception:
            dead.append(ws)
    for ws in dead:
        with contextlib.suppress(ValueError):
            _ws_clients.remove(ws)
    # A wiki change invalidates the course catalog (lesson <-> concept links); rebuild
    # it once the burst of changes settles rather than on the next request.
    _schedule_catalog_rewarm()


async def _watch_and_broadcast(awatch: Callable[[str], AsyncIterator[object]]) -> None:
    """Push a graph update per wiki change. A failure is logged and the watch goes on."""
    while True:
        try:
            async for _ in awatch(str(WIKI_DIR)):
                try:
                    await _broadcast_graph()
                except Exception:
                    log.exception("api.watcher.broadcast_failed")
            return  # the watch ended cleanly
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("api.watcher.failed", retry_in_s=WATCHER_RESTART_DELAY_S)
            await asyncio.sleep(WATCHER_RESTART_DELAY_S)


def _schedule_catalog_rewarm() -> None:
    global _rewarm_handle
    if _rewarm_handle is not None:
        _rewarm_handle.cancel()
    _rewarm_handle = asyncio.get_running_loop().call_later(
        CATALOG_REWARM_DELAY_S, _in_background, _warm_course_data
    )


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Both startup jobs need the `api` extra (librarian.retrieval.embeddings -> numpy/sentence-transformers,
    # _watch_and_broadcast -> watchfiles), and both are optimizations: warmup only
    # pre-loads a model, the watcher only pushes live graph updates. Neither is required
    # for the routes to answer. Degrade instead of failing startup, because CI installs
    # `--group dev` with no extras and TestClient-as-context-manager runs this lifespan —
    # a hard import here failed every test that enters the lifespan.
    # Course catalog: the cold build takes seconds (frontmatter for ~760 lessons plus
    # concept linking). Build it off the event loop so the first /api/courses request is
    # a cache hit. Needs no extra; warm_catalog() never raises, so startup cannot fail.
    # LIBRARIAN_SKIP_WARMUP=1 (set by tests/conftest.py) skips both warmups so tests that
    # enter the lifespan don't build the real catalog or load the embedding model.
    # The jobs run one after another. A boot running them side by side segfaulted in torch's
    # MPS copy path (1 of 4 tries, 2026-11-04); the cause isn't established, so this and the
    # encode lock in librarian/retrieval/embeddings.py are precautions, not a proven fix.
    watcher: asyncio.Task[None] | None = None
    skip_warmup = os.environ.get("LIBRARIAN_SKIP_WARMUP") == "1" or get_settings().skip_warmup
    global _index_state
    errors, warnings = find_problems(get_settings())
    for line in warnings:
        log.warning("api.startup.config", problem=line)
    for line in errors:
        log.error("api.startup.config", problem=line)
    if errors:
        # Fail before serving: a deployment that cannot work should not look up.
        raise RuntimeError("invalid configuration: " + "; ".join(errors))
    # The index first: it is what /readyz waits for, and the model load can follow it.
    jobs: list[Callable[[], None]] = [] if skip_warmup else [_build_index, _warm_course_data]
    _index_state = "skipped" if skip_warmup else "building"
    try:
        from watchfiles import awatch

        from librarian.retrieval.embeddings import warmup
    except ImportError as e:
        log.warning("startup_jobs_skipped", reason="api extra not installed", error=str(e))
    else:
        # Warmup in background so server accepts connections immediately
        if not skip_warmup:
            jobs.append(warmup)
        watcher = asyncio.create_task(_watch_and_broadcast(awatch))
        _background_tasks.add(watcher)
        watcher.add_done_callback(_background_tasks.discard)
    if jobs:
        _in_background(lambda: _run_in_order(jobs))
    log.info("api.startup.ready", seconds=round(time.perf_counter() - _PROCESS_T0, 2))
    try:
        yield
    finally:
        await _shutdown(watcher)


async def _shutdown(watcher: asyncio.Task[None] | None) -> None:
    """Stop the wiki watcher and pending catalog rewarm, and close live websockets."""
    global _rewarm_handle
    if _rewarm_handle is not None:
        _rewarm_handle.cancel()
        _rewarm_handle = None
    if watcher is not None:
        watcher.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await watcher
    for ws in list(_ws_clients):
        with contextlib.suppress(Exception):
            await ws.close(code=1001)
    _ws_clients.clear()
    log.info("api.shutdown.done")


# Every route needs the token when one is set, /healthz and /readyz and the static UI excepted.
# The interactive docs and schema list every route, so they are off unless EXPOSE_DOCS is set.
_docs = get_settings().expose_docs
app = FastAPI(
    title="Librarian Graph API",
    lifespan=lifespan,
    dependencies=[Depends(require_token)],
    docs_url="/docs" if _docs else None,
    redoc_url="/redoc" if _docs else None,
    openapi_url="/openapi.json" if _docs else None,
)
# Sentry and OTel, each only when its env var is set (librarian/observability.py).
setup_observability(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SecurityHeadersMiddleware,
    csp=build_csp(inline_script_hashes(get_settings().web_dir / "index.html")),
)
app.add_middleware(RequestLogMiddleware)
app.include_router(courses_router)
app.include_router(curriculum_router)
app.include_router(glossary_router)
app.include_router(wiki_health_router)


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket) -> None:
    # Echo the "bearer" subprotocol the client used to carry its token, or the browser fails the handshake.
    await ws.accept(
        subprotocol=WS_SUBPROTOCOL if WS_SUBPROTOCOL in ws.scope["subprotocols"] else None
    )
    _ws_clients.append(ws)
    try:
        graph = await asyncio.to_thread(parse_wiki)
        await ws.send_json({"type": "graph_update", "data": graph})
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        with contextlib.suppress(ValueError):
            _ws_clients.remove(ws)


# Sync route (threadpool): parse_wiki reads every page, which on the event loop stalls all
# other requests for as long as it takes.
@app.get("/api/graph")
def get_graph(edges: Literal["wikilink", "all"] = "wikilink") -> dict[str, Any]:
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
    from librarian.retrieval.embeddings import semantic_edges

    public = public_page_ids()
    return [e for e in semantic_edges(threshold) if e["source"] in public and e["target"] in public]


@app.post("/api/layout/umap")
def umap_layout() -> dict[str, dict]:
    # Imported lazily: umap-learn pulls in numba, which requires numpy<2.5. When
    # pyproject.toml still pinned numpy>=2.5.1 a module-level import took the entire
    # API down (including /api/graph) over one optional layout endpoint. The pin now
    # reads numpy>=2.4,<2.5, but the lazy import stays — the extra is still optional.
    try:
        from .umap_layout import compute_umap_positions

        positions = compute_umap_positions()  # imports umap only when it has to fit
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"UMAP layout unavailable — umap-learn/numba vs numpy conflict: {e}",
        ) from e
    public = public_page_ids()
    return {pid: xy for pid, xy in positions.items() if pid in public}


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
    settings = get_settings()
    if not settings.chat_enabled:
        raise HTTPException(status_code=404, detail="chat is disabled")
    chat_limiter.admit(settings)  # 429 before any model call
    history = [t.model_dump() for t in req.history]

    def on_usage(usage: TokenUsage) -> None:
        chat_limiter.record_usage(settings, usage)

    async def generate() -> AsyncIterator[str]:
        async for event in run_agent_stream(req.query, history, on_usage=on_usage):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Liveness: the process answers."""
    return {"status": "ok"}


# The index probe opens the file without building it, so a passing answer is reused briefly.
_READY_TTL_S = 30.0
_ready_until = 0.0


@app.get("/readyz")
def readyz() -> JSONResponse:
    """Readiness: the index is built and the model is loaded, or the rerank is off or failed.

    Never builds or refreshes the index: while the startup job is still at it the answer is 503
    `{"index": "building"}`. A model that failed to load is `degraded`, not unready: search then
    runs on text alone.
    """
    global _ready_until
    if _index_state in ("building", "failed"):
        return JSONResponse(
            {"status": "not_ready", "index": _index_state, "checks": {"index": False}},
            status_code=503,
        )
    checks: dict[str, bool] = {}
    if time.monotonic() < _ready_until:
        checks["index"] = True
    else:
        try:
            checks["index"] = retrieval.index_is_built()
        except Exception as exc:
            log.warning("api.readyz.index_failed", error=str(exc), error_type=type(exc).__name__)
            checks["index"] = False
        if checks["index"]:
            _ready_until = time.monotonic() + _READY_TTL_S
    unavailable = retrieval.embeddings_unavailable()
    checks["embeddings"] = unavailable or retrieval.embeddings_ready()
    degraded = ["embeddings_unavailable"] if unavailable else []
    ready = all(checks.values())
    body: dict[str, Any] = {"status": "ready" if ready else "not_ready", "checks": checks}
    if not checks["index"]:
        body["index"] = "building"
    if degraded:
        body["degraded"] = degraded
    return JSONResponse(body, status_code=200 if ready else 503)


# Last, so every route above keeps precedence. The UI routes with `#/...`, so a plain static
# mount needs no SPA fallback. The bundle itself holds nothing private.
_web_dir = get_settings().web_dir
if _web_dir.is_dir():
    app.mount("/", StaticFiles(directory=_web_dir, html=True), name="web")
