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
def test_cross_domain_tag_shared_edges(mock_wiki: Path) -> None:
    from backend.wiki_parser import parse_wiki

    result = parse_wiki()
    tag_shared = [e for e in result["edges"] if e["data"].get("edgeType") == "tag-shared"]
    assert len(tag_shared) >= 1, "observability shares 'rag' tag with rag pages across domains"
