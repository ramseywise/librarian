from __future__ import annotations

import httpx
import pytest

BASE = "http://localhost:8100"


@pytest.mark.e2e
def test_repos_endpoint_lists_librarian() -> None:
    r = httpx.get(f"{BASE}/api/repos", timeout=10)
    assert r.status_code == 200
    repos = r.json()
    assert any(repo["repo_id"] == "librarian" for repo in repos)


@pytest.mark.e2e
def test_find_symbol_returns_known_function() -> None:
    r = httpx.get(
        f"{BASE}/api/symbols/find", params={"name": "build_index", "repo": "librarian"}, timeout=10
    )
    assert r.status_code == 200
    results = r.json()
    assert any(s["name"] == "build_index" for s in results)


@pytest.mark.e2e
def test_repo_map_returns_ranked_files() -> None:
    r = httpx.get(f"{BASE}/api/repo_map", params={"repo": "librarian", "limit": 10}, timeout=10)
    assert r.status_code == 200
    files = r.json()
    assert len(files) > 0
    assert all("rel_path" in f and "inbound_weight" in f for f in files)


@pytest.mark.e2e
def test_callers_endpoint_finds_known_caller() -> None:
    r = httpx.get(f"{BASE}/api/callers", params={"symbol_name": "index_repo"}, timeout=10)
    assert r.status_code == 200
    callers = r.json()
    assert any(c["rel_path"] == "tools/codemap/indexer.py" for c in callers)


@pytest.mark.e2e
def test_semantic_search_returns_501_or_results() -> None:
    """sentence-transformers may or may not be installed in the environment
    running this test — both outcomes are valid, this just confirms the
    endpoint responds correctly either way rather than erroring."""
    r = httpx.get(
        f"{BASE}/api/symbols/semantic_search", params={"query": "parse a file"}, timeout=15
    )
    assert r.status_code in (200, 501)
    if r.status_code == 200:
        assert isinstance(r.json(), list)
