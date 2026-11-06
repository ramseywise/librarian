"""librarian.wiki.graph against synthetic wikis. All names here are made up."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path

import pytest

from librarian.wiki.graph import analyse, load_graph, main, render
from librarian.wiki.telemetry import compute_stats

TODAY = date(2026, 11, 5)
PRIVATE_TITLE = "Acme Secret Roadmap"
PRIVATE_STEM = "acme-roadmap-internal"


def write_page(wiki: Path, rel: str, links: list[str], tags: tuple[str, ...] = ("rag",)) -> None:
    path = wiki / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    stem = path.stem
    body = " ".join(f"[[{link}]]" for link in links)
    path.write_text(
        f"---\ntitle: {stem}\ntags: [{', '.join(tags)}, concept]\nsummary: s\n"
        f"updated: 2026-11-01\n---\n\n# {stem}\n\n{body}\n"
    )


def write_group(wiki: Path, directory: str, names: list[str], extra: list[str]) -> None:
    for name in names:
        write_page(wiki, f"{directory}/{name}.md", [n for n in names if n != name] + extra)


@pytest.fixture
def joined(tmp_path: Path) -> Path:
    """Two dense groups whose only route to each other runs through `joint`."""
    wiki = tmp_path / "wiki"
    left = [f"left-{i}" for i in range(6)]
    right = [f"right-{i}" for i in range(6)]
    write_group(wiki, "rag", left, [])
    write_group(wiki, "memory", right, [])
    write_page(wiki, "patterns/joint.md", [*left[:3], *right[:3]])
    return wiki


def test_joint_page_is_top_bridge_and_only_cut_point(joined: Path) -> None:
    report = analyse(load_graph(joined))
    assert report.bridges[0].page == "patterns/joint.md"
    assert report.articulation_points == ["patterns/joint.md"]
    assert report.bridge_links == 0
    assert report.components == 1


def test_two_groups_are_two_clusters(joined: Path) -> None:
    report = analyse(load_graph(joined))
    assert len(report.clusters) == 2
    assert {next(iter(c.directories)) for c in report.clusters} == {"rag", "memory"}
    assert report.stability == pytest.approx(1.0, abs=0.2)


def test_same_wiki_gives_same_report(joined: Path) -> None:
    assert asdict(analyse(load_graph(joined))) == asdict(analyse(load_graph(joined)))


def test_edge_order_does_not_depend_on_the_hash_seed(joined: Path) -> None:
    # Louvain walks adjacency order, so a set-ordered edge list changes clusters between processes.
    script = (
        "import sys; from pathlib import Path; from librarian.wiki.graph import load_graph; "
        "print(list(load_graph(Path(sys.argv[1])).edges))"
    )
    orders = {
        subprocess.run(
            [sys.executable, "-c", script, str(joined)],
            env={**os.environ, "PYTHONHASHSEED": seed},
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        for seed in ("1", "2", "3", "4")
    }
    assert len(orders) == 1


def test_directory_split_across_three_clusters_is_flagged(tmp_path: Path) -> None:
    wiki = tmp_path / "wiki"
    for i in range(3):
        write_group(wiki, "foundations", [f"group{i}-{j}" for j in range(6)], [])
    report = analyse(load_graph(wiki))
    assert report.split_directories == {"foundations": [1, 2, 3]}
    assert report.mixed_clusters == []


def test_cluster_with_no_majority_directory_is_flagged(tmp_path: Path) -> None:
    wiki = tmp_path / "wiki"
    names = {"rag": ["a0", "a1"], "memory": ["b0", "b1"], "adk": ["c0", "c1"]}
    everyone = [n for group in names.values() for n in group]
    for directory, group in names.items():
        for name in group:
            write_page(wiki, f"{directory}/{name}.md", [n for n in everyone if n != name])
    assert analyse(load_graph(wiki)).mixed_clusters == [1]


def test_only_public_scored_pages_are_nodes(joined: Path) -> None:
    write_page(joined, "rag/old.md", ["left-0"], tags=("rag", "tombstone"))
    write_page(joined, "_index.md", ["left-0"])
    write_page(joined, f"private/{PRIVATE_STEM}.md", ["left-0"])
    graph = load_graph(joined)
    assert graph.number_of_nodes() == 13
    assert graph.number_of_nodes() == compute_stats(joined, TODAY)["pages"]


def test_link_counts_match_wiki_stats(joined: Path) -> None:
    graph = load_graph(joined)
    stats = compute_stats(joined, TODAY)
    directed = sum(graph.nodes[n]["outbound"] for n in graph)
    assert stats["metrics"]["average_degree"]["value"] == round(directed * 2 / len(graph), 4)


def test_private_page_is_absent_from_text_and_json(
    joined: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    private = joined / "private" / f"{PRIVATE_STEM}.md"
    private.parent.mkdir(parents=True)
    private.write_text(
        f"---\ntitle: {PRIVATE_TITLE}\ntags: [rag, concept]\nsummary: s\nupdated: 2026-11-01\n---\n"
        "\n[[left-0]]\n"
    )
    write_page(joined, "rag/left-0.md", [f"left-{i}" for i in range(1, 6)] + [PRIVATE_TITLE])

    assert main(["--wiki-dir", str(joined)]) == 0
    assert main(["--wiki-dir", str(joined), "--json"]) == 0
    out = capsys.readouterr().out
    assert PRIVATE_STEM not in out
    assert PRIVATE_TITLE not in out


@pytest.mark.parametrize(
    "pages",
    [
        pytest.param([], id="empty"),
        pytest.param([("rag/only.md", [])], id="one-page"),
        pytest.param([("rag/a.md", []), ("rag/b.md", []), ("memory/c.md", [])], id="no-links"),
    ],
)
def test_degenerate_wikis_do_not_crash(tmp_path: Path, pages: list[tuple[str, list[str]]]) -> None:
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    for rel, links in pages:
        write_page(wiki, rel, links)
    report = analyse(load_graph(wiki))
    assert report.pages == len(pages)
    assert report.clusters == []
    assert report.unsettled == len(pages)
    assert render(report)


def test_json_output_parses(joined: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--wiki-dir", str(joined), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["pages"] == 13
    assert data["bridges"][0]["page"] == "patterns/joint.md"
