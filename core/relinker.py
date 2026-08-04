"""Post-ingest relinking pass.

Discovers missing semantic links between wiki pages after an ingest cycle.
Run after all pages are created/updated:

    uv run --extra api python core/relinker.py [--threshold 0.65] [--suggest-threshold 0.55] [--dry-run]

Requires the `api` optional dependency group (numpy, sentence-transformers, scikit-learn).

Produces:
- Auto-added links (appended to See Also with <!-- auto-linked --> comment)
- data/wiki/_relink_suggestions.md (candidates between suggest and auto thresholds)
- data/wiki/_bridge_suggestions.md (cross-domain gaps)
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import frontmatter

from core.wiki_common import WIKILINK_RE

REPO_ROOT = Path(__file__).parent.parent
WIKI_DIR = REPO_ROOT / "data" / "wiki"

DOMAIN_TAG_SET = {
    "langgraph",
    "rag",
    "adk",
    "mcp",
    "memory",
    "eval",
    "infra",
    "deep-agents",
    "patterns",
    "meta",
    "projects",
}

TYPE_TAGS = {"concept", "pattern", "decision", "project", "comparison", "reference", "conflict"}


@dataclass
class PageInfo:
    path: Path
    stem: str
    title: str
    tags: list[str]
    domain: str
    type_tag: str
    outgoing_links: set[str] = field(default_factory=set)
    incoming_links: set[str] = field(default_factory=set)


@dataclass
class RelinkReport:
    auto_linked: list[tuple[str, str, float]]  # (source_stem, target_stem, score)
    suggested: list[tuple[str, str, float]]
    orphans_backfilled: list[tuple[str, str]]  # (hub_stem, orphan_stem)
    bridge_gaps: list[tuple[str, str, int]]  # (domain_a, domain_b, cross_link_count)


def _slug(title: str) -> str:
    return title.lower().strip().replace(" ", "-")


def load_pages() -> dict[str, PageInfo]:
    pages: dict[str, PageInfo] = {}
    for md_file in sorted(WIKI_DIR.rglob("*.md")):
        if md_file.name.startswith("_"):
            continue
        post = frontmatter.load(md_file)
        title = post.get("title") or md_file.stem
        tags = post.get("tags") or []
        if isinstance(tags, str):
            tags = [tags]
        domain = md_file.parent.name
        type_tag = next((t for t in tags if t in TYPE_TAGS), "concept")

        pages[md_file.stem] = PageInfo(
            path=md_file,
            stem=md_file.stem,
            title=title,
            tags=tags,
            domain=domain,
            type_tag=type_tag,
        )
    return pages


def build_link_graph(pages: dict[str, PageInfo]) -> None:
    slug_to_stem: dict[str, str] = {}
    for stem, info in pages.items():
        slug_to_stem[stem] = stem
        slug_to_stem[_slug(info.title)] = stem

    for stem, info in pages.items():
        content = info.path.read_text()
        for match in WIKILINK_RE.finditer(content):
            raw = match.group(1).strip()
            target_slug = _slug(raw)
            target_stem = slug_to_stem.get(target_slug, target_slug)
            if target_stem in pages and target_stem != stem:
                info.outgoing_links.add(target_stem)
                pages[target_stem].incoming_links.add(stem)


def compute_adjusted_score(base_score: float, source: PageInfo, target: PageInfo) -> float:
    score = base_score
    if source.domain == target.domain:
        score += 0.1
    shared_tags = set(source.tags) & set(target.tags) - DOMAIN_TAG_SET - TYPE_TAGS
    score += 0.05 * len(shared_tags)
    type_set = {source.type_tag, target.type_tag}
    if "pattern" in type_set and "concept" in type_set:
        score += 0.1
    return score


def append_see_also(page_path: Path, link_title: str, comment: str = "auto-linked") -> None:
    content = page_path.read_text()

    entry = f"- [[{link_title}]] <!-- {comment} -->"

    # Line-exact anchor: pages may QUOTE "## See Also" in prose or inline code
    # (a substring replace once corrupted such a page) — only a real heading
    # line counts as the section.
    match = re.search(r"^## See Also[ \t]*$", content, flags=re.MULTILINE)
    if match:
        content = content[: match.end()] + f"\n{entry}" + content[match.end() :]
    else:
        content = content.rstrip() + f"\n\n## See Also\n{entry}\n"

    page_path.write_text(content)


def relink(
    pages: dict[str, PageInfo],
    auto_threshold: float = 0.65,
    suggest_threshold: float = 0.55,
    changed_pages: list[str] | None = None,
    dry_run: bool = False,
) -> RelinkReport:
    _repo_root_str = str(REPO_ROOT)
    if _repo_root_str not in sys.path:
        sys.path.insert(0, _repo_root_str)
    from sklearn.metrics.pairwise import cosine_similarity

    from shared.embeddings import compute_embeddings

    page_ids, vecs = compute_embeddings()
    if len(page_ids) < 2:
        return RelinkReport([], [], [], [])

    sim = cosine_similarity(vecs)
    id_to_idx = {pid: i for i, pid in enumerate(page_ids)}

    scope = set(changed_pages) if changed_pages else set(pages.keys())

    auto_linked: list[tuple[str, str, float]] = []
    suggested: list[tuple[str, str, float]] = []

    for stem in scope:
        if stem not in pages or stem not in id_to_idx:
            continue
        info = pages[stem]
        idx = id_to_idx[stem]
        already_linked = info.outgoing_links | info.incoming_links

        candidates: list[tuple[str, float]] = []
        for other_stem, other_idx in id_to_idx.items():
            if other_stem == stem or other_stem not in pages:
                continue
            if other_stem in already_linked:
                continue
            base = float(sim[idx, other_idx])
            if base < suggest_threshold - 0.15:
                continue
            adjusted = compute_adjusted_score(base, info, pages[other_stem])
            candidates.append((other_stem, adjusted))

        candidates.sort(key=lambda x: -x[1])
        top_5 = candidates[:5]

        for target_stem, score in top_5:
            if score >= auto_threshold:
                auto_linked.append((stem, target_stem, score))
                if not dry_run:
                    append_see_also(info.path, pages[target_stem].title)
                    info.outgoing_links.add(target_stem)
                    pages[target_stem].incoming_links.add(stem)
            elif score >= suggest_threshold:
                suggested.append((stem, target_stem, score))

    # Orphan backfill: pages with zero incoming links
    orphans_backfilled: list[tuple[str, str]] = []
    for stem, info in pages.items():
        if info.incoming_links:
            continue
        if stem not in id_to_idx:
            continue
        idx = id_to_idx[stem]
        best_hub: str | None = None
        best_score = 0.0
        for other_stem, other_idx in id_to_idx.items():
            if other_stem == stem or other_stem not in pages:
                continue
            if not pages[other_stem].incoming_links:
                continue
            score = float(sim[idx, other_idx])
            if score > best_score:
                best_score = score
                best_hub = other_stem
        if best_hub and best_score > 0.3:
            orphans_backfilled.append((best_hub, stem))
            if not dry_run:
                append_see_also(pages[best_hub].path, info.title, comment="backfill")
                pages[best_hub].outgoing_links.add(stem)
                info.incoming_links.add(best_hub)

    # Bridge gap detection
    bridge_gaps = detect_bridge_gaps(pages)

    # Write suggestions file
    if suggested and not dry_run:
        write_suggestions(suggested, pages)

    if bridge_gaps and not dry_run:
        write_bridge_suggestions(bridge_gaps, pages)

    return RelinkReport(
        auto_linked=auto_linked,
        suggested=suggested,
        orphans_backfilled=orphans_backfilled,
        bridge_gaps=bridge_gaps,
    )


def detect_bridge_gaps(pages: dict[str, PageInfo]) -> list[tuple[str, str, int]]:
    domain_pages: dict[str, list[str]] = defaultdict(list)
    for stem, info in pages.items():
        domain_pages[info.domain].append(stem)

    cross_links: dict[tuple[str, str], int] = defaultdict(int)
    for info in pages.values():
        for target in info.outgoing_links:
            if target in pages:
                src_domain = info.domain
                tgt_domain = pages[target].domain
                if src_domain != tgt_domain:
                    pair = tuple(sorted([src_domain, tgt_domain]))
                    cross_links[pair] += 1

    gaps: list[tuple[str, str, int]] = []
    domains = [d for d, ps in domain_pages.items() if len(ps) >= 5]
    for i, d1 in enumerate(domains):
        for d2 in domains[i + 1 :]:
            pair = tuple(sorted([d1, d2]))
            count = cross_links.get(pair, 0)
            if count < 3:
                gaps.append((pair[0], pair[1], count))

    gaps.sort(key=lambda x: x[2])
    return gaps


def write_suggestions(suggested: list[tuple[str, str, float]], pages: dict[str, PageInfo]) -> None:
    lines = [
        "---",
        "title: Relink Suggestions",
        f"updated: {date.today().isoformat()}",
        "---",
        "",
        "# Relink Suggestions",
        "",
        "Pages below scored above the suggestion threshold but below auto-link.",
        "Review and add as typed links if appropriate, or dismiss by deleting the entry.",
        "",
    ]
    for source, target, score in sorted(suggested, key=lambda x: -x[2]):
        src_title = pages[source].title if source in pages else source
        tgt_title = pages[target].title if target in pages else target
        lines.append(f"- [[{src_title}]] → [[{tgt_title}]] (score: {score:.3f})")
    lines.append("")

    (WIKI_DIR / "_relink_suggestions.md").write_text("\n".join(lines))


def write_bridge_suggestions(gaps: list[tuple[str, str, int]], pages: dict[str, PageInfo]) -> None:
    lines = [
        "---",
        "title: Bridge Suggestions",
        f"updated: {date.today().isoformat()}",
        "---",
        "",
        "# Bridge Suggestions",
        "",
        "Domain pairs below have >5 pages each but fewer than 3 cross-domain links.",
        "Consider creating a bridge page or adding cross-references.",
        "",
    ]
    for d1, d2, count in gaps:
        lines.append(f"## {d1} ↔ {d2} ({count} cross-links)")
        d1_pages = [s for s, p in pages.items() if p.domain == d1]
        d2_pages = [s for s, p in pages.items() if p.domain == d2]
        lines.append(f"  - {d1}: {len(d1_pages)} pages")
        lines.append(f"  - {d2}: {len(d2_pages)} pages")
        lines.append("")
    lines.append("")

    (WIKI_DIR / "_bridge_suggestions.md").write_text("\n".join(lines))


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Post-ingest relinking pass")
    parser.add_argument("--threshold", type=float, default=0.65, help="Auto-link threshold")
    parser.add_argument(
        "--suggest-threshold", type=float, default=0.55, help="Suggestion threshold"
    )
    parser.add_argument("--dry-run", action="store_true", help="Report only, don't modify files")
    parser.add_argument("--changed", nargs="*", help="Only relink these page stems (default: all)")
    args = parser.parse_args()

    print("Loading wiki pages...")
    pages = load_pages()
    print(f"  {len(pages)} pages found")

    print("Building link graph...")
    build_link_graph(pages)
    orphans = [s for s, p in pages.items() if not p.incoming_links]
    print(f"  {len(orphans)} orphan pages")

    print("Computing semantic similarity and relinking...")
    report = relink(
        pages,
        auto_threshold=args.threshold,
        suggest_threshold=args.suggest_threshold,
        changed_pages=args.changed,
        dry_run=args.dry_run,
    )

    print(f"\nResults {'(dry run)' if args.dry_run else ''}:")
    print(f"  Auto-linked: {len(report.auto_linked)}")
    for src, tgt, score in report.auto_linked[:10]:
        print(f"    {pages[src].title} → {pages[tgt].title} ({score:.3f})")
    print(f"  Suggested: {len(report.suggested)}")
    for src, tgt, score in report.suggested[:10]:
        print(f"    {pages[src].title} → {pages[tgt].title} ({score:.3f})")
    print(f"  Orphans backfilled: {len(report.orphans_backfilled)}")
    for hub, orphan in report.orphans_backfilled[:10]:
        print(f"    {pages[hub].title} → {pages[orphan].title}")
    print(f"  Bridge gaps: {len(report.bridge_gaps)}")
    for d1, d2, count in report.bridge_gaps[:10]:
        print(f"    {d1} ↔ {d2} ({count} cross-links)")


if __name__ == "__main__":
    main()
