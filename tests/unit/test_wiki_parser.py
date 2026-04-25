from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "app"))

from backend.wiki_parser import parse_wiki


@pytest.mark.unit
def test_parse_wiki_returns_nodes_and_edges() -> None:
    result = parse_wiki()
    assert "nodes" in result
    assert "edges" in result
    assert len(result["nodes"]) > 0


@pytest.mark.unit
def test_all_nodes_have_required_fields() -> None:
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
def test_no_self_referencing_edges() -> None:
    result = parse_wiki()
    for edge in result["edges"]:
        assert edge["source"] != edge["target"]


@pytest.mark.unit
def test_all_edge_targets_exist() -> None:
    result = parse_wiki()
    node_ids = {n["id"] for n in result["nodes"]}
    for edge in result["edges"]:
        assert edge["source"] in node_ids, f"missing source: {edge['source']}"
        assert edge["target"] in node_ids, f"missing target: {edge['target']}"


@pytest.mark.unit
def test_no_yaml_parse_errors() -> None:
    """Every wiki file must have valid YAML frontmatter."""
    import frontmatter

    wiki_dir = Path(__file__).parent.parent.parent / "wiki"
    errors = []
    for md_file in wiki_dir.rglob("*.md"):
        if md_file.name.startswith("_"):
            continue
        try:
            frontmatter.load(md_file)
        except Exception as e:
            errors.append(f"{md_file.relative_to(wiki_dir)}: {e}")

    assert not errors, "YAML errors in wiki files:\n" + "\n".join(errors)
