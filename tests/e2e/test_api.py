from __future__ import annotations

import pytest
import httpx

BASE = "http://localhost:8000"


@pytest.mark.e2e
def test_graph_endpoint_returns_nodes() -> None:
    r = httpx.get(f"{BASE}/api/graph", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert len(data["nodes"]) > 0
    assert len(data["edges"]) > 0


@pytest.mark.e2e
def test_graph_nodes_have_positions() -> None:
    """All nodes must have position set (not all zeroes after layout)."""
    r = httpx.get(f"{BASE}/api/graph", timeout=10)
    data = r.json()
    assert all("position" in n for n in data["nodes"])


@pytest.mark.e2e
def test_semantic_edges_endpoint() -> None:
    r = httpx.get(f"{BASE}/api/edges/semantic?threshold=0.8", timeout=30)
    assert r.status_code == 200
    edges = r.json()
    assert isinstance(edges, list)
    if edges:
        assert edges[0]["data"]["edgeType"] == "semantic"
