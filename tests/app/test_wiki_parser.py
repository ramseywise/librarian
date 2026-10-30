from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "app"))


def _write_page(
    directory: Path,
    domain: str,
    stem: str,
    title: str,
    tags: list[str],
    summary: str,
    body: str = "",
) -> None:
    d = directory / domain
    d.mkdir(parents=True, exist_ok=True)
    tag_str = ", ".join(tags)
    lines = [
        "---",
        f"title: {title}",
        f"tags: [{tag_str}]",
        f"summary: {summary}",
        "updated: 2026-07-23",
        "sources: []",
        "---",
        "",
        f"# {title}",
        "",
        body,
    ]
    (d / f"{stem}.md").write_text("\n".join(lines) + "\n")


@pytest.fixture()
def mock_wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    _write_page(
        tmp_path,
        "rag",
        "semantic-cache",
        "Semantic Cache",
        ["rag", "pattern"],
        "Cache embeddings for faster retrieval",
        "Uses [[Vector Databases]] for storage.\n\n## See Also\n- [[Vector Databases]] — extends",
    )
    _write_page(
        tmp_path,
        "rag",
        "vector-databases",
        "Vector Databases",
        ["rag", "concept"],
        "Stores and queries dense vectors",
        "## See Also\n- [[Semantic Cache]] — prerequisite-for",
    )
    _write_page(
        tmp_path,
        "infra",
        "observability",
        "Observability",
        ["infra", "rag", "concept"],
        "Monitor agent systems in production",
    )

    import backend.wiki_parser as wp

    monkeypatch.setattr(wp, "WIKI_DIR", tmp_path)
    return tmp_path


@pytest.mark.unit
def test_parse_wiki_returns_nodes_and_edges(mock_wiki: Path) -> None:
    from backend.wiki_parser import parse_wiki

    result = parse_wiki()
    assert "nodes" in result
    assert "edges" in result
    assert len(result["nodes"]) > 0


@pytest.mark.unit
def test_all_nodes_have_required_fields(mock_wiki: Path) -> None:
    from backend.wiki_parser import parse_wiki

    result = parse_wiki()
    for node in result["nodes"]:
        assert "id" in node
        assert "type" in node
        assert "data" in node
        data = node["data"]
        assert "title" in data
        assert "tags" in data
        assert "domain" in data
        assert "typeTag" in data
        assert "summary" in data


@pytest.mark.unit
def test_no_self_referencing_edges(mock_wiki: Path) -> None:
    from backend.wiki_parser import parse_wiki

    result = parse_wiki()
    for edge in result["edges"]:
        assert edge["source"] != edge["target"]


@pytest.mark.unit
def test_all_edge_targets_exist(mock_wiki: Path) -> None:
    from backend.wiki_parser import parse_wiki

    result = parse_wiki()
    node_ids = {n["id"] for n in result["nodes"]}
    for edge in result["edges"]:
        assert edge["source"] in node_ids, f"missing source: {edge['source']}"
        assert edge["target"] in node_ids, f"missing target: {edge['target']}"


@pytest.mark.unit
def test_no_yaml_parse_errors(mock_wiki: Path) -> None:
    """Every wiki file must have valid YAML frontmatter."""
    import frontmatter

    errors = []
    for md_file in mock_wiki.rglob("*.md"):
        if md_file.name.startswith("_"):
            continue
        try:
            frontmatter.load(md_file)
        except Exception as e:
            errors.append(f"{md_file.name}: {e}")

    assert not errors, "YAML errors in wiki files:\n" + "\n".join(errors)


@pytest.mark.unit
def test_wikilink_edges_extracted(mock_wiki: Path) -> None:
    from backend.wiki_parser import parse_wiki

    result = parse_wiki()
    wikilink_edges = [e for e in result["edges"] if e["data"].get("edgeType") == "wikilink"]
    assert len(wikilink_edges) >= 1


@pytest.mark.unit
def test_typed_relationship_extracted(mock_wiki: Path) -> None:
    from backend.wiki_parser import parse_wiki

    result = parse_wiki()
    typed = [e for e in result["edges"] if e["data"].get("relationship")]
    assert len(typed) >= 1
    assert typed[0]["data"]["relationship"] in {"extends", "prerequisite-for"}


@pytest.mark.unit
def test_payload_has_no_tag_shared_edges_and_lists_domains(mock_wiki: Path) -> None:
    """Contract 1 (D3): the payload carries wikilink edges only, plus a sorted domain list.

    Tag-shared edges were ~42k pairs / ~10 MB per graph_update; the UI now derives them.
    """
    from backend.wiki_parser import parse_wiki

    result = parse_wiki()
    assert {e["data"]["edgeType"] for e in result["edges"]} == {"wikilink"}
    assert result["domains"] == ["infra", "rag"]


@pytest.mark.unit
def test_cross_domain_tag_shared_edges(mock_wiki: Path) -> None:
    from backend.wiki_parser import parse_wiki, tag_shared_edges

    result = parse_wiki()
    tag_shared = tag_shared_edges(result["nodes"], result["domains"])
    assert {e["id"] for e in tag_shared} == {
        "ts:observability->semantic-cache",
        "ts:observability->vector-databases",
    }, "observability shares 'rag' with the rag pages across directories; rag↔rag is skipped"
    assert all(e["data"]["sharedTags"] == ["rag"] for e in tag_shared)


def _node(nid: str, directory: str, tags: list[str]) -> dict:
    return {"id": nid, "data": {"domain": [directory], "tags": tags}}


@pytest.mark.unit
def test_tag_shared_rule_matches_frontend_tag_edges() -> None:
    """Same cases as app/frontend/src/utils/__tests__/tagEdges.test.ts — the Python rule
    (used by /api/graph?edges=all) and the client-side one must stay identical."""
    from backend.wiki_parser import tag_shared_edges

    domains = ["rag", "eval", "memory"]
    assert tag_shared_edges(
        [_node("a", "rag", ["rag", "pattern"]), _node("b", "eval", ["rag"])], domains
    ) == [
        {
            "id": "ts:a->b",
            "source": "a",
            "target": "b",
            "data": {"edgeType": "tag-shared", "sharedTags": ["rag"]},
        }
    ]
    assert tag_shared_edges([_node("a", "rag", ["rag"]), _node("b", "rag", ["rag"])], domains) == []
    assert (
        tag_shared_edges([_node("a", "rag", ["pattern"]), _node("b", "eval", ["pattern"])], domains)
        == []
    )
    edges = tag_shared_edges(
        [_node("z", "rag", ["rag", "memory"]), _node("a", "eval", ["memory", "rag"])], domains
    )
    assert len(edges) == 1
    assert edges[0]["id"] == "ts:a->z"
    assert edges[0]["data"]["sharedTags"] == ["memory", "rag"]


@pytest.mark.unit
def test_private_pages_are_in_graph_flagged_and_not_a_domain(mock_wiki: Path) -> None:
    """Deliberate decision D1 (2026-10-30), not an accident: data/wiki/private/ pages stay
    visible in the LOCAL graph UI, flagged `private` so the UI can badge them. They are
    not a filterable domain. (Courses API and MCP search exclude them — tested elsewhere.)
    Change this test only together with a recorded decision."""
    from backend.wiki_parser import parse_wiki

    _write_page(mock_wiki, "private", "client-notes", "Client Notes", ["projects", "project"], "S")
    result = parse_wiki()
    by_id = {n["id"]: n for n in result["nodes"]}
    assert by_id["client-notes"]["data"]["private"] is True
    assert by_id["semantic-cache"]["data"]["private"] is False
    assert "private" not in result["domains"]


@pytest.mark.unit
def test_api_graph_edges_all_adds_tag_shared(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """GET /api/graph defaults to the slim payload; ?edges=all restores tag-shared edges."""
    from fastapi.testclient import TestClient

    import app.backend.main as main_module
    import app.backend.wiki_parser as app_wp

    _write_page(tmp_path, "rag", "a-page", "A Page", ["rag", "concept"], "S", "[[B Page]]")
    _write_page(tmp_path, "eval", "b-page", "B Page", ["eval", "rag", "concept"], "S")
    monkeypatch.setattr(app_wp, "WIKI_DIR", tmp_path)
    client = TestClient(main_module.app)  # no `with`: lifespan (warmups, watcher) not run

    slim = client.get("/api/graph").json()
    assert [e["id"] for e in slim["edges"]] == ["wl:a-page->b-page"]
    assert slim["domains"] == ["eval", "rag"]
    full = client.get("/api/graph", params={"edges": "all"}).json()
    assert {e["id"] for e in full["edges"]} == {"wl:a-page->b-page", "ts:a-page->b-page"}
    assert client.get("/api/graph", params={"edges": "bogus"}).status_code == 422
