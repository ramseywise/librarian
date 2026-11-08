"""The shape of the wiki's link graph: hubs, bridges and consensus clusters. Read-only.

`make wiki-stats` asks whether the graph is healthy; this asks what shape it is. Nodes and edges
are the ones wiki-stats counts, so private pages, tombstones and underscore files are never nodes
and the output can only name public pages.

One Louvain run is too unstable to read: two seeds gave NMI 0.69-0.79 on the real wiki. Clusters
here are a consensus: keep a link when its two pages share a community in at least `cut` of the
runs, then take connected components. The cut and size floor are local heuristics. Seeds are
fixed, so the same wiki always gives the same report. Cluster numbers move as the wiki changes:
never store them.

    uv run librarian wiki graph [--json]
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

import networkx as nx
from networkx.algorithms.community import louvain_communities
from sklearn.metrics import normalized_mutual_info_score

from librarian.wiki.telemetry import WIKI_DIR, _link_edges, _link_index, _public_pages

TOP_HUBS = 10
TOP_BRIDGES = 10
TOP_CLUSTER_PAGES = 5
TOP_CLUSTER_TAGS = 5
# A bridge outside this many top pages by degree is one a degree list would never have shown.
DEGREE_RANK_HIDDEN = 50
MIN_CLUSTER_PAGES = 5
CONSENSUS_SEEDS = 20
CONSENSUS_CUT = 0.8
STABILITY_SEED_OFFSET = 1000
STABILITY_FLOOR = 0.9
# A directory is split when at least this many clusters each hold this share of its pages.
SPLIT_MIN_CLUSTERS = 3
SPLIT_MIN_SHARE = 0.10
MIXED_MAX_SHARE = 0.5
# A directory holding this share of all pages has stopped being a domain and become a bucket;
# when it is also split, its clusters are the subject directories it should become.
OVERSIZED_SHARE = 0.20
TYPE_TAGS = {"concept", "pattern", "decision", "project", "comparison", "reference", "conflict"}


@dataclass
class Hub:
    page: str
    degree: int
    inbound: int
    outbound: int
    clusters_spanned: int


@dataclass
class Bridge:
    page: str
    betweenness: float
    degree: int
    clusters_touched: int
    hidden_by_degree: bool


@dataclass
class Cluster:
    number: int
    size: int
    directories: dict[str, int]
    top_pages: list[str]
    top_tags: list[str]


@dataclass
class GraphReport:
    pages: int
    links: int
    components: int
    articulation_points: list[str]
    bridge_links: int
    hubs: list[Hub]
    bridges: list[Bridge]
    clusters: list[Cluster]
    unsettled: int
    split_directories: dict[str, list[int]]
    oversized_directories: dict[str, float]
    mixed_clusters: list[int]
    stability: float


def load_graph(wiki_dir: Path) -> nx.Graph:
    """The undirected link graph, with each page's directory, tags and link counts on its node."""
    public = _public_pages(wiki_dir)
    pages = [p for p in public if p.scored]
    outbound, inbound = _link_edges(pages, _link_index(public))
    graph = nx.Graph()
    for page in pages:
        graph.add_node(
            page.rel,
            directory=page.domain,
            tags=page.tags,
            inbound=len(inbound[page.rel]),
            outbound=len(outbound[page.rel]),
        )
    # Sorted because Louvain walks adjacency order, and a set of strings changes order per process.
    graph.add_edges_from(
        (rel, target) for rel, targets in outbound.items() for target in sorted(targets)
    )
    return graph


def consensus_clusters(graph: nx.Graph, seeds: Iterable[int], cut: float) -> list[set[str]]:
    """Connected components of the links whose ends share a community in `cut` of the runs."""
    runs = [
        {
            node: i
            for i, members in enumerate(louvain_communities(graph, seed=s))
            for node in members
        }
        for s in seeds
    ]
    kept = nx.Graph()
    kept.add_nodes_from(graph)
    for u, v in graph.edges:
        if sum(run[u] == run[v] for run in runs) / len(runs) >= cut:
            kept.add_edge(u, v)
    return sorted(nx.connected_components(kept), key=lambda c: (-len(c), min(c)))


def _stability(graph: nx.Graph, first: list[set[str]], seeds: int, cut: float) -> float:
    """NMI between the clustering and one from seeds it never saw. 1.0 is identical."""
    if graph.number_of_nodes() < 2:
        return 1.0
    offset = range(STABILITY_SEED_OFFSET, STABILITY_SEED_OFFSET + seeds)
    second = consensus_clusters(graph, offset, cut)
    labels_a, labels_b = (
        {node: i for i, members in enumerate(clusters) for node in members}
        for clusters in (first, second)
    )
    nodes = sorted(graph)
    return float(
        normalized_mutual_info_score([labels_a[n] for n in nodes], [labels_b[n] for n in nodes])
    )


def _by_degree(graph: nx.Graph, nodes: Iterable[str]) -> list[str]:
    return sorted(nodes, key=lambda n: (-graph.degree(n), n))


def _neighbour_clusters(graph: nx.Graph, node: str, cluster_of: dict[str, int]) -> int:
    return len({cluster_of[n] for n in graph[node] if n in cluster_of})


def _describe_cluster(graph: nx.Graph, number: int, members: set[str]) -> Cluster:
    directories = Counter(graph.nodes[n]["directory"] for n in members)
    tags = Counter(t for n in members for t in graph.nodes[n]["tags"] if t not in TYPE_TAGS)
    return Cluster(
        number=number,
        size=len(members),
        directories=dict(sorted(directories.items(), key=lambda kv: (-kv[1], kv[0]))),
        top_pages=_by_degree(graph, members)[:TOP_CLUSTER_PAGES],
        top_tags=[t for t, _ in sorted(tags.items(), key=lambda kv: (-kv[1], kv[0]))][
            :TOP_CLUSTER_TAGS
        ],
    )


def _split_directories(graph: nx.Graph, clusters: list[Cluster]) -> dict[str, list[int]]:
    """Directory → the numbers of the clusters holding a real share of it, when there are enough."""
    totals = Counter(graph.nodes[n]["directory"] for n in graph)
    split = {}
    for directory, total in sorted(totals.items()):
        holding = [
            c.number for c in clusters if c.directories.get(directory, 0) / total >= SPLIT_MIN_SHARE
        ]
        if len(holding) >= SPLIT_MIN_CLUSTERS:
            split[directory] = holding
    return split


def _oversized_directories(graph: nx.Graph) -> dict[str, float]:
    """Directory → its share of all pages, for directories at or over `OVERSIZED_SHARE`."""
    totals = Counter(graph.nodes[n]["directory"] for n in graph)
    pages = graph.number_of_nodes()
    return {
        directory: round(total / pages, 3)
        for directory, total in sorted(totals.items())
        if pages and total / pages >= OVERSIZED_SHARE
    }


def analyse(
    graph: nx.Graph, seeds: int = CONSENSUS_SEEDS, cut: float = CONSENSUS_CUT
) -> GraphReport:
    components = consensus_clusters(graph, range(seeds), cut)
    settled = [c for c in components if len(c) >= MIN_CLUSTER_PAGES]
    cluster_of = {node: i for i, members in enumerate(settled, 1) for node in members}
    clusters = [_describe_cluster(graph, i, members) for i, members in enumerate(settled, 1)]

    hubs = [
        Hub(
            page=node,
            degree=graph.degree(node),
            inbound=graph.nodes[node]["inbound"],
            outbound=graph.nodes[node]["outbound"],
            clusters_spanned=_neighbour_clusters(graph, node, cluster_of),
        )
        for node in _by_degree(graph, graph)[:TOP_HUBS]
    ]

    betweenness = nx.betweenness_centrality(graph)
    well_linked = set(_by_degree(graph, graph)[:DEGREE_RANK_HIDDEN])
    bridges = [
        Bridge(
            page=node,
            betweenness=round(betweenness[node], 4),
            degree=graph.degree(node),
            clusters_touched=_neighbour_clusters(graph, node, cluster_of),
            hidden_by_degree=node not in well_linked,
        )
        for node in sorted(graph, key=lambda n: (-betweenness[n], n))[:TOP_BRIDGES]
        if betweenness[node] > 0
    ]

    return GraphReport(
        pages=graph.number_of_nodes(),
        links=graph.number_of_edges(),
        components=nx.number_connected_components(graph) if graph else 0,
        articulation_points=sorted(nx.articulation_points(graph)),
        bridge_links=sum(1 for _ in nx.bridges(graph)),
        hubs=hubs,
        bridges=bridges,
        clusters=clusters,
        unsettled=graph.number_of_nodes() - len(cluster_of),
        split_directories=_split_directories(graph, clusters),
        oversized_directories=_oversized_directories(graph),
        mixed_clusters=[
            c.number for c in clusters if max(c.directories.values()) / c.size <= MIXED_MAX_SHARE
        ],
        stability=round(_stability(graph, components, seeds, cut), 3),
    )


def render(report: GraphReport) -> str:
    lines = [
        f"Pages: {report.pages}  Links: {report.links}  Components: {report.components}",
        f"Stability: {report.stability:.3f}",
    ]
    if report.stability < STABILITY_FLOOR:
        lines.append(f"Below {STABILITY_FLOOR}: clusters are unsettled, do not read much into them")
    lines.append(
        f"Cut points: {len(report.articulation_points)} pages, {report.bridge_links} links"
    )
    lines += [f"  {page}" for page in report.articulation_points]

    lines += ["", f"Hubs (top {TOP_HUBS} by links):"]
    lines += [
        f"  {h.degree:>4} links ({h.inbound} in, {h.outbound} out), "
        f"spans {h.clusters_spanned} clusters  {h.page}"
        for h in report.hubs
    ]

    lines += ["", f"Bridges (top {TOP_BRIDGES} by betweenness):"]
    lines += [
        f"  {b.betweenness:.3f}  {b.degree:>4} links, touches {b.clusters_touched} clusters  {b.page}"
        + ("  [hidden by degree]" if b.hidden_by_degree else "")
        for b in report.bridges
    ]

    lines += ["", f"Clusters: {len(report.clusters)}, plus {report.unsettled} unsettled pages"]
    for c in report.clusters:
        mix = ", ".join(f"{directory} {n}" for directory, n in c.directories.items())
        lines += [
            f"  {c.number}. {c.size} pages: {mix}",
            f"     tags: {', '.join(c.top_tags)}",
            *[f"     {page}" for page in c.top_pages],
        ]

    lines += ["", "Directories across 3+ clusters:"]
    lines += [
        f"  {directory}: clusters {', '.join(map(str, numbers))}"
        for directory, numbers in report.split_directories.items()
    ] or ["  none"]
    lines += ["", f"Directories over {OVERSIZED_SHARE:.0%} of pages:"]
    lines += [
        f"  {directory}: {share:.0%}"
        + (
            f", split across clusters {', '.join(map(str, report.split_directories[directory]))}:"
            " a split candidate (check the routing rule first)"
            if directory in report.split_directories
            else ", one subject: big but coherent"
        )
        for directory, share in report.oversized_directories.items()
    ] or ["  none"]
    mixed = ", ".join(map(str, report.mixed_clusters)) or "none"
    lines.append(f"Clusters with no majority directory: {mixed}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    parser.add_argument("--wiki-dir", type=Path, default=WIKI_DIR)
    args = parser.parse_args(argv)

    report = analyse(load_graph(args.wiki_dir))
    print(json.dumps(asdict(report), indent=2) if args.json else render(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
