from __future__ import annotations

import asyncio
import contextlib
import os
import signal
import time
from collections.abc import AsyncIterator, Callable, Coroutine
from typing import Any

# Before the heavy imports below, so the startup log covers them too.
_PROCESS_T0 = time.perf_counter()

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from librarian import release, retrieval
from librarian.api import prom
from librarian.api.routers import graph
from librarian.api.routers.account import router as account_router
from librarian.api.routers.auth import router as auth_router
from librarian.api.routers.chat import router as chat_router
from librarian.api.routers.courses import router as courses_router
from librarian.api.routers.curriculum import router as curriculum_router
from librarian.api.routers.feedback import router as feedback_router
from librarian.api.routers.glossary import router as glossary_router
from librarian.api.routers.release import ReleaseHeaderMiddleware, poll_releases
from librarian.api.routers.release import router as release_router
from librarian.api.routers.spend import router as spend_router
from librarian.api.routers.tools import router as tools_router
from librarian.api.routers.wiki_health import router as wiki_health_router
from librarian.api.security import (
    RequestLogMiddleware,
    SecurityHeadersMiddleware,
    build_csp,
    current_user,
    inline_script_hashes,
)
from librarian.api.startup import find_problems
from librarian.config import get_settings
from librarian.courses.catalog import warm_catalog
from librarian.courses.curriculum import write_snapshot
from librarian.log_config import configure_logging, get_logger
from librarian.observability import setup as setup_observability

# At import, not in a main(): uvicorn imports this module as an ASGI app and never
# calls an entry point of ours. Must precede the first log call from any route.
configure_logging()
log = get_logger(__name__)

WIKI_DIR = get_settings().wiki_dir

# Process state that is safe with N workers: each worker holds its own startup jobs, and the
# watcher and catalog rewarm below run only with settings.dev_watch (one dev process).
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


def _warm_course_data() -> None:
    warm_catalog()
    write_snapshot()


async def _broadcast_graph() -> None:
    await graph.broadcast_graph()
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
    # pre-loads a model, the watcher (dev_watch only) pushes live graph updates. Neither is required
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
    errors, warnings = find_problems(get_settings())
    for line in warnings:
        log.warning("api.startup.config", problem=line)
    for line in errors:
        log.error("api.startup.config", problem=line)
    if errors:
        # Fail before serving: a deployment that cannot work should not look up.
        raise RuntimeError("invalid configuration: " + "; ".join(errors))
    # The index is a build artifact: the handle opens `current` read-only (dev mode with none
    # builds one in a thread, and /readyz says "building" meanwhile). No request writes to it.
    handle = retrieval.IndexHandle(autobuild=get_settings().index_autobuild)
    retrieval.set_handle(handle)
    handle.start()
    _install_reload_signal(handle)
    jobs: list[Callable[[], None]] = [] if skip_warmup else [_warm_course_data]
    try:
        from librarian.retrieval.embeddings import warmup
    except ImportError as e:
        log.warning("startup_jobs_skipped", reason="api extra not installed", error=str(e))
    else:
        # Warmup in background so server accepts connections immediately
        if not skip_warmup:
            jobs.append(warmup)
    if get_settings().dev_watch:
        watcher = _start_watcher()
    poller = _start_task(poll_releases()) if get_settings().release_url else None
    if jobs:
        _in_background(lambda: _run_in_order(jobs))
    log.info("api.startup.ready", seconds=round(time.perf_counter() - _PROCESS_T0, 2))
    try:
        yield
    finally:
        retrieval.set_handle(None)
        await _shutdown(watcher, poller)


def _start_watcher() -> asyncio.Task[None] | None:
    try:
        from watchfiles import awatch
    except ImportError as e:
        log.warning("api.watcher.skipped", reason="api extra not installed", error=str(e))
        return None
    return _start_task(_watch_and_broadcast(awatch))


def _start_task(coro: Coroutine[Any, Any, None]) -> asyncio.Task[None]:
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return task


def _install_reload_signal(handle: retrieval.IndexHandle) -> None:
    """SIGHUP swaps in the build `current` names now. Skipped where signals can't be hooked."""

    def reload() -> None:
        log.info("api.index.sighup", **handle.reload())

    try:
        asyncio.get_running_loop().add_signal_handler(signal.SIGHUP, reload)
    except (NotImplementedError, RuntimeError, ValueError):
        log.debug("api.index.sighup_unavailable")


async def _shutdown(*tasks: asyncio.Task[None] | None) -> None:
    """Stop the wiki watcher, the release poller and pending catalog rewarm; close websockets."""
    global _rewarm_handle
    if _rewarm_handle is not None:
        _rewarm_handle.cancel()
        _rewarm_handle = None
    for task in tasks:
        if task is not None:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
    await graph.close_clients()
    log.info("api.shutdown.done")


# Every route resolves the caller (security.current_user): an API key, or the owner for the
# bootstrap token and open mode. /healthz, /readyz and the static UI excepted.
# The interactive docs and schema list every route, so they are off unless EXPOSE_DOCS is set.
_docs = get_settings().expose_docs
app = FastAPI(
    title="Librarian Graph API",
    lifespan=lifespan,
    dependencies=[Depends(current_user)],
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
    expose_headers=["X-Librarian-Release"],
)
app.add_middleware(
    SecurityHeadersMiddleware,
    csp=build_csp(inline_script_hashes(get_settings().web_dir / "index.html")),
)
app.add_middleware(RequestLogMiddleware)
app.add_middleware(prom.MetricsMiddleware)
app.add_middleware(ReleaseHeaderMiddleware)
app.include_router(graph.router)
app.include_router(account_router)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(courses_router)
app.include_router(curriculum_router)
app.include_router(feedback_router)
app.include_router(glossary_router)
app.include_router(release_router)
app.include_router(spend_router)
app.include_router(tools_router)
app.include_router(wiki_health_router)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Liveness: the process answers."""
    return {"status": "ok"}


@app.exception_handler(retrieval.IndexNotReadyError)
async def _index_not_ready(_: Request, exc: retrieval.IndexNotReadyError) -> JSONResponse:
    return JSONResponse({"detail": str(exc)}, status_code=503, headers={"Retry-After": "5"})


def readiness() -> tuple[bool, dict[str, Any]]:
    """(ready, body) for /readyz: a built index is loaded and the model is loaded, or the rerank
    is off or failed.

    Never builds or refreshes anything. `index` is the handle's state: ready, building (dev mode,
    first build), missing or error. A model that failed to load is `degraded`, not unready:
    search then runs on text alone.
    """
    handle = retrieval.get_handle()
    state = handle.state if handle else "missing"
    checks: dict[str, bool] = {}
    try:
        checks["index"] = retrieval.index_is_built()
    except Exception as exc:
        log.warning("api.readyz.index_failed", error=str(exc), error_type=type(exc).__name__)
        checks["index"] = False
    if get_settings().release_url:  # serving releases: none installed yet means nothing to serve
        checks["content"] = release.current_name() is not None
    unavailable = retrieval.embeddings_unavailable()
    checks["embeddings"] = unavailable or retrieval.embeddings_ready()
    ready = all(checks.values())
    body: dict[str, Any] = {
        "status": "ready" if ready else "not_ready",
        "index": state,
        "checks": checks,
    }
    if unavailable:
        body["degraded"] = ["embeddings_unavailable"]
    return ready, body


@app.get("/readyz")
def readyz() -> JSONResponse:
    """Readiness probe: 200 when `readiness()` says ready, else 503."""
    ready, body = readiness()
    return JSONResponse(body, status_code=200 if ready else 503)


# Prometheus scrape target. A plain Starlette route, so the app-wide `current_user` dependency
# does not apply: it checks LIBRARIAN_METRICS_TOKEN itself (404 when unset). api/prom.py.
prom.set_readiness(lambda: readiness()[0])
app.add_route(prom.METRICS_PATH, prom.metrics_endpoint, include_in_schema=False)


# Last, so every route above keeps precedence. The UI routes with `#/...`, so a plain static
# mount needs no SPA fallback. The bundle itself holds nothing private.
_web_dir = get_settings().web_dir
if _web_dir.is_dir():
    app.mount("/", StaticFiles(directory=_web_dir, html=True), name="web")
