"""Ontology checks for `librarian wiki check`: typed-link and title consistency, all WARN.

Deterministic, no model and no embedding cache (a lint must not load a model). Public,
non-tombstone pages only: a private page is never read into a finding, so nothing here can
name one. Findings are `"<CODE> <text>"` lines naming public page paths.

    ONT001  prerequisite-for cycle (one strongly connected set of pages, listed once)
    ONT002  instance-of declared both ways between two pages
    ONT003  instance-of whose general side is a `project` page and instance side is not
    ONT004  near-duplicate pages (token Jaccard of title + summary)

Direction follows CLAUDE.md: `- [[X]] — type` on page P describes X relative to P, so
`prerequisite-for` is the edge X -> P and `instance-of` says X is an instance of P.
"""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Iterator
from pathlib import Path

import frontmatter

from librarian.log_config import get_logger
from librarian.wiki.common import TYPED_LINK_RE, fm
from librarian.wiki.pages import Page, PageLinks, _link_index, _public_pages

log = get_logger(__name__)

CYCLE = "ONT001"
INSTANCE_MUTUAL = "ONT002"
INSTANCE_OF_PROJECT = "ONT003"
NEAR_DUPLICATE = "ONT004"

# Measured on the real wiki (2026-11-08, 1246 pages): the sibling families (the "... Interview
# Study Guide" pages, "ADK X Patterns") score at most 0.27 on title + summary tokens, while the
# pairs that read as one topic split in two start at 0.35. A title-only Jaccard cannot separate
# them (siblings reach 0.6), and the summary-only one finds almost nothing.
NEAR_DUPLICATE_THRESHOLD = 0.35
# Too few tokens and one shared word decides the score.
MIN_TOKENS = 4

_STOPWORDS = frozenset(
    [
        "a",
        "an",
        "the",
        "of",
        "and",
        "or",
        "for",
        "in",
        "on",
        "to",
        "with",
        "vs",
        "is",
        "not",
        "as",
        "by",
        "at",
        "from",
        "into",
        "its",
        "it",
        "your",
        "how",
        "why",
        "what",
        "when",
    ]
)
_TOKEN_RE = re.compile(r"[a-z0-9]+")
_TYPE_TAGS = ("project", "pattern", "decision", "concept", "comparison", "reference")


def _tokens(text: str) -> frozenset[str]:
    out: set[str] = set()
    for token in _TOKEN_RE.findall(text.lower()):
        if token in _STOPWORDS:
            continue
        if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
            token = token[:-1]  # crude plural fold: "patterns" == "pattern"
        out.add(token)
    return frozenset(out)


def typed_edges(pages: list[Page], links: PageLinks, link_type: str) -> Iterator[tuple[Page, Page]]:
    """(P, X) for every `- [[X]] — link_type` line on page P that resolves to a live public page."""
    for page in pages:
        for line in page.body.splitlines():
            match = TYPED_LINK_RE.match(line.strip())
            if match is None or match.group(2) != link_type:
                continue
            target = links.resolve(match.group(1))
            if target is not None and target.rel != page.rel:
                yield page, target


def prerequisite_cycles(pages: list[Page], links: PageLinks) -> list[list[str]]:
    """Each strongly connected set of 2+ pages under X -> P edges, sorted, once."""
    graph: dict[str, set[str]] = defaultdict(set)
    for page, prereq in typed_edges(pages, links, "prerequisite-for"):
        graph[prereq.rel].add(page.rel)
        graph.setdefault(page.rel, set())
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    found: list[list[str]] = []
    counter = 0

    def visit(root: str) -> None:
        # Iterative Tarjan: a long prerequisite chain must not hit the recursion limit.
        nonlocal counter
        work = [(root, iter(sorted(graph[root])))]
        index[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on_stack.add(root)
        while work:
            node, children = work[-1]
            for child in children:
                if child not in index:
                    index[child] = low[child] = counter
                    counter += 1
                    stack.append(child)
                    on_stack.add(child)
                    work.append((child, iter(sorted(graph[child]))))
                    break
                if child in on_stack:
                    low[node] = min(low[node], index[child])
            else:
                work.pop()
                if work:
                    parent = work[-1][0]
                    low[parent] = min(low[parent], low[node])
                if low[node] == index[node]:
                    component = []
                    while True:
                        member = stack.pop()
                        on_stack.discard(member)
                        component.append(member)
                        if member == node:
                            break
                    if len(component) > 1:
                        found.append(sorted(component))

    for node in sorted(graph):
        if node not in index:
            visit(node)
    return sorted(found)


def _type_tag(page: Page) -> str | None:
    return next((t for t in page.tags if t in _TYPE_TAGS), None)


def instance_of_findings(pages: list[Page], links: PageLinks) -> list[str]:
    """Likely-reversed `instance-of` edges.

    ONT002: both pages declare the other an instance, which cannot hold both ways.
    ONT003: the general side (P) is a `project` page and the instance (X) is not. A project
    is concrete: the pattern page lists the project as its instance, not the reverse.
    A pair already reported as ONT002 is not repeated as ONT003.
    """
    edges = {(p.rel, x.rel): (p, x) for p, x in typed_edges(pages, links, "instance-of")}
    findings: list[str] = []
    mutual: set[frozenset[str]] = set()
    for (p, x), _ in sorted(edges.items()):
        if (x, p) in edges and p < x:
            mutual.add(frozenset((p, x)))
            findings.append(f"{INSTANCE_MUTUAL} {p} and {x} each declare the other instance-of")
    for (p, x), (page, target) in sorted(edges.items()):
        if frozenset((p, x)) in mutual:
            continue
        if _type_tag(page) == "project" and _type_tag(target) != "project":
            findings.append(
                f"{INSTANCE_OF_PROJECT} {p} lists {x} as instance-of, "
                "but a project page is the concrete side"
            )
    return findings


def _summary(page: Page) -> str:
    try:
        return str(fm(frontmatter.load(page.path)).get("summary") or "")
    except (OSError, ValueError):
        return ""


def near_duplicates(
    pages: list[Page], threshold: float = NEAR_DUPLICATE_THRESHOLD
) -> list[tuple[float, str, str]]:
    """(score, rel_a, rel_b) for page pairs whose title + summary tokens overlap enough."""
    tokens = [(p.rel, _tokens(f"{p.title} {_summary(p)}")) for p in pages if p.parsed]
    tokens = [(rel, t) for rel, t in tokens if len(t) >= MIN_TOKENS]
    pairs: list[tuple[float, str, str]] = []
    for i, (rel_a, a) in enumerate(tokens):
        for rel_b, b in tokens[i + 1 :]:
            score = len(a & b) / len(a | b)
            if score >= threshold:
                first, second = sorted((rel_a, rel_b))
                pairs.append((round(score, 2), first, second))
    return sorted(pairs, key=lambda r: (-r[0], r[1], r[2]))


def check_ontology(wiki_dir: Path) -> list[str]:
    """All ontology findings for the public wiki, each a WARN line without the level."""
    pages = [p for p in _public_pages(wiki_dir) if p.scored]
    links = _link_index(pages)
    findings = [
        f"{CYCLE} prerequisite-for cycle among {len(cycle)} pages: {', '.join(cycle)}"
        for cycle in prerequisite_cycles(pages, links)
    ]
    findings.extend(instance_of_findings(pages, links))
    findings.extend(
        f"{NEAR_DUPLICATE} near-duplicate pages ({score}): {a} / {b}"
        for score, a, b in near_duplicates(pages)
    )
    log.debug("wiki.ontology.checked", findings=len(findings), pages=len(pages))
    return findings
