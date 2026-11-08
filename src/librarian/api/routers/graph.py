"""The wiki graph: /api/graph, semantic edges, the UMAP layout and the /ws live feed.

The live feed is dev-only state: with `settings.dev_watch` on, each socket is kept in
`_ws_clients` and `broadcast_graph()` (called by the watcher in `api.main`) pushes it a fresh
graph after a wiki edit. With it off, as in a deployment, a socket gets the graph once and is
not tracked, so no worker holds clients another cannot reach.
"""

from __future__ import annotations

import asyncio
import contextlib
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from librarian.api.security import WS_SUBPROTOCOL
from librarian.config import get_settings
from librarian.wiki.parser import parse_wiki, public_page_ids, tag_shared_edges

router = APIRouter()

_ws_clients: list[WebSocket] = []


async def broadcast_graph() -> None:
    """Send the current graph to every tracked socket, dropping the ones that fail."""
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


async def close_clients() -> None:
    """Close the tracked sockets (shutdown)."""
    for ws in list(_ws_clients):
        with contextlib.suppress(Exception):
            await ws.close(code=1001)
    _ws_clients.clear()


@router.websocket("/ws")
async def ws_endpoint(ws: WebSocket) -> None:
    # Echo the "bearer" subprotocol the client used to carry its token, or the browser fails the handshake.
    await ws.accept(
        subprotocol=WS_SUBPROTOCOL if WS_SUBPROTOCOL in ws.scope["subprotocols"] else None
    )
    live = get_settings().dev_watch
    if live:
        _ws_clients.append(ws)
    try:
        graph = await asyncio.to_thread(parse_wiki)
        await ws.send_json({"type": "graph_update", "data": graph})
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        if live:
            with contextlib.suppress(ValueError):
                _ws_clients.remove(ws)


# Sync route (threadpool): parse_wiki reads every page, which on the event loop stalls all
# other requests for as long as it takes.
@router.get("/api/graph")
def get_graph(edges: Literal["wikilink", "all"] = "wikilink") -> dict[str, Any]:
    """Same payload as the /ws graph_update. `?edges=all` adds the tag-shared edges the
    UI derives client-side, for scripts that want the full edge set from the server."""
    graph = parse_wiki()
    if edges == "all":
        graph["edges"] = graph["edges"] + tag_shared_edges(graph["nodes"], graph["domains"])
    return graph


@router.get("/api/graph/atlas")
def get_graph_atlas() -> dict[str, Any]:
    """The map's first paint: /api/graph without summaries, paths or edge objects.

    Wikilinks are `[source, target]` index pairs into `nodes` (with the relationship as a
    third item when typed), about a tenth of the edge JSON. The full graph still arrives over
    /ws; the UI uses this until it does. Same pages as parse_wiki(): no private, no tombstones.
    """
    graph = parse_wiki()
    index = {n["id"]: i for i, n in enumerate(graph["nodes"])}
    nodes = [
        {
            "id": n["id"],
            "title": n["data"]["title"],
            "domain": n["data"]["domain"][0],
            "typeTag": n["data"]["typeTag"],
            "tags": n["data"]["tags"],
        }
        for n in graph["nodes"]
    ]
    links = []
    for e in graph["edges"]:
        pair = [index[e["source"]], index[e["target"]]]
        if rel := e["data"].get("relationship"):
            pair.append(rel)
        links.append(pair)
    return {"nodes": nodes, "links": links, "domains": graph["domains"]}


# Sync routes (threadpool): both block on embeddings, and compute_embeddings serialises
# on a lock the course-catalog build may hold — never wait on it from the event loop.
@router.get("/api/edges/semantic")
def get_semantic_edges(threshold: float = 0.65) -> list[dict]:
    from librarian.retrieval.embeddings import semantic_edges

    public = public_page_ids()
    return [e for e in semantic_edges(threshold) if e["source"] in public and e["target"] in public]


@router.post("/api/layout/umap")
def umap_layout() -> dict[str, dict]:
    # Imported lazily: umap-learn pulls in numba, which requires numpy<2.5. When
    # pyproject.toml still pinned numpy>=2.5.1 a module-level import took the entire
    # API down (including /api/graph) over one optional layout endpoint. The pin now
    # reads numpy>=2.4,<2.5, but the lazy import stays — the extra is still optional.
    try:
        from librarian.api.umap_layout import compute_umap_positions

        positions = compute_umap_positions()  # imports umap only when it has to fit
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"UMAP layout unavailable — umap-learn/numba vs numpy conflict: {e}",
        ) from e
    public = public_page_ids()
    return {pid: xy for pid, xy in positions.items() if pid in public}
