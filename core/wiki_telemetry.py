"""Wiki health telemetry: deterministic numbers, an operation log and a gaps list.

No model calls: the output depends only on the files read and the date. Everything written
goes to data/telemetry/, outside data/wiki/, so the MCP index, relinker and graph never see it.

    uv run python core/wiki_telemetry.py stats [--json]
    uv run python core/wiki_telemetry.py snapshot            # stats + one row in metrics.jsonl
    uv run python core/wiki_telemetry.py check [--file PATH] # private-leak check, exit 1 on BLOCKER
    uv run python core/wiki_telemetry.py log <op> "<detail>" # exit 2 if detail names a private page
    uv run python core/wiki_telemetry.py ask "<topic>"       # gitignored asked.jsonl
    uv run --extra api python core/wiki_telemetry.py gaps    # regenerate gitignored gaps.md

`metrics.jsonl` and `operations.jsonl` are tracked in a public repo. Private pages are never
scored, hub-listed or printed: reports name the public file and line, never the private page.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import frontmatter
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
# `python core/wiki_telemetry.py` puts core/ on sys.path, not the repo root.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.sensitive import (  # noqa: E402
    embedded_names_pattern,
    load_terms,
    private_names,
    scan_line,
    scan_text,
    terms_pattern,
)
from core.wiki_common import TYPED_LINK_RE, WIKILINK_RE, page_aliases, slugify  # noqa: E402

WIKI_DIR = REPO_ROOT / "data" / "wiki"
TELEMETRY_DIR = REPO_ROOT / "data" / "telemetry"
COURSES_DIR = REPO_ROOT / "data" / "courses"
RETRIEVAL_LOG = REPO_ROOT / "logs" / "retrieval.jsonl"

METRICS_FILE = "metrics.jsonl"
OPERATIONS_FILE = "operations.jsonl"
ASKED_FILE = "asked.jsonl"
GAPS_FILE = "gaps.md"
# Every other *.jsonl here counts as tracked, so a new one is leak-checked by default.
UNTRACKED_TELEMETRY = {ASKED_FILE}

METRICS_MAX_ROWS = 36
OPERATIONS_KEEP_FULL = 30

# Local heuristics, not research results. Orphan bands and the 80% component line are from
# second-brain-os, whose own docs cite nothing. Degree counts both ends of a link and theirs
# counts one, so their "below two" is the floor of 4 here. The 8-20 band, 200-word stub line,
# 60% component floor and 5% stub rate were chosen here, some after the first snapshot
# (2026-11-05: page degree median 11, p5-p95 5-34; body words p1 191, median 600). The typed
# line is this repo's lint rule. Change them only on evidence from metrics.jsonl snapshots.
ORPHAN_HEALTHY, ORPHAN_BROKEN = 0.05, 0.15
DEGREE_HEALTHY_MIN, DEGREE_HEALTHY_MAX, DEGREE_BROKEN = 8.0, 20.0, 4.0
COMPONENT_HEALTHY, COMPONENT_BROKEN = 0.80, 0.60
TYPED_HEALTHY = 0.50
STUB_HEALTHY = 0.05
STALE_DAYS = 60
STUB_WORDS = 200
TOP_HUBS = 10
TOP_GAPS = 5
# Titles shorter than this are too generic to call a mention a leak.
TITLE_LEAK_MIN_WORDS = 3

# Real questions only: `eval`, `sweep`, `diag` and `review_smoke` rows are harness traffic.
QUERY_TOOLS = {"search_wiki", "search_courses"}
# The retrieval log has no score field, and the blended score the server computes is
# rank-based, with no absolute meaning. So the only defensible floor is "returned nothing".
ASKED_FLOOR_NOTE = (
    "Floor: a query counts as unanswered only if its latest healthy search returned zero results. "
    "logs/retrieval.jsonl carries no scores, so weak matches are invisible here."
)

_SEE_ALSO_RE = re.compile(r"^(#{1,6})\s+see also\b", re.IGNORECASE)
_HEADING_RE = re.compile(r"^(#{1,6})\s")
_SEE_ALSO_PREFIX_RE = re.compile(r"^see also:\s*", re.IGNORECASE)
_STATUS_RE = re.compile(r"^\*\*Status:\*\*\s*(\S+)", re.MULTILINE)
_OP_RE = re.compile(r"^[a-z][a-z0-9-]*$")
_GAP_LINE_RE = re.compile(r"^- (.+) \| first seen (\d{4}-\d{2}-\d{2}) \| count \d+$", re.MULTILINE)
_FM_TITLE_RE = re.compile(r"^title:\s*(.+)$", re.MULTILINE)
_FM_BLOCK_RE = re.compile(r"\A---\n.*?\n---\n?", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


class TelemetryFileError(Exception):
    """A tracked telemetry file can't be parsed, so rewriting it would lose rows."""


# ── Reading the wiki ─────────────────────────────────────────────────────────


@dataclass
class Page:
    path: Path
    rel: str  # posix path relative to the wiki dir
    stem: str
    title: str
    tags: list[str]
    updated: date | None
    body: str
    parsed: bool  # False: broken YAML, so tags and date are unknown
    aliases: tuple[str, ...] = ()

    @property
    def domain(self) -> str:
        parts = self.rel.split("/")
        return parts[0] if len(parts) > 1 else "(root)"

    @property
    def scored(self) -> bool:
        return "tombstone" not in self.tags and not self.stem.startswith("_")


def _to_date(value: object) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip()[:10])
    except ValueError:
        return None


def _load_page(path: Path, wiki_dir: Path) -> Page:
    text = path.read_text(errors="replace")
    rel = path.relative_to(wiki_dir).as_posix()
    try:
        post = frontmatter.loads(text)
    except (yaml.YAMLError, ValueError):
        # The graph and index drop such a page; a leak check must still see its title.
        match = _FM_TITLE_RE.search(text)
        title = match.group(1).strip().strip("\"'") if match else path.stem
        body = _FM_BLOCK_RE.sub("", text, count=1)
        return Page(path, rel, path.stem, title, [], None, body, parsed=False)
    tags = post.get("tags") or []
    tags = [tags] if isinstance(tags, str) else [str(t) for t in tags]
    title = str(post.get("title") or path.stem)
    updated = _to_date(post.get("updated"))
    aliases = tuple(page_aliases(post.metadata))
    return Page(path, rel, path.stem, title, tags, updated, post.content, True, aliases)


def _public_files(wiki_dir: Path) -> list[Path]:
    return sorted(
        f for f in wiki_dir.rglob("*.md") if f.relative_to(wiki_dir).parts[0] != "private"
    )


def _private_pages(wiki_dir: Path) -> list[Page]:
    # Searched from its own root: in a worktree private/ is a symlink, which rglob from
    # the wiki dir would not descend into.
    root = wiki_dir / "private"
    if not root.is_dir():
        return []
    return [_load_page(f, wiki_dir) for f in sorted(root.rglob("*.md"))]


def _public_pages(wiki_dir: Path) -> list[Page]:
    return [_load_page(f, wiki_dir) for f in _public_files(wiki_dir)]


def _slug_map(pages: Iterable[Page]) -> dict[str, Page]:
    """Link slug → page. Stems beat titles beat aliases, the same resolution as core/relinker.py."""
    pages = [p for p in pages if not p.stem.startswith("_")]
    slugs: dict[str, Page] = {}
    for page in pages:
        slugs.setdefault(slugify(page.stem), page)
    for page in pages:
        slugs.setdefault(slugify(page.title), page)
    for page in pages:
        for alias in page.aliases:
            slugs.setdefault(slugify(alias), page)
    return slugs


def _link_target(raw: str) -> tuple[str, bool]:
    """A wikilink's slug, and whether the link spells out a path through private/."""
    target = _SEE_ALSO_PREFIX_RE.sub("", raw.strip())
    if "/" not in target:
        return slugify(target), False
    segments = target.split("/")
    return slugify(segments[-1].removesuffix(".md")), "private" in segments


def _links_to_private(
    target: tuple[str, bool], public: dict[str, Page], private: dict[str, Page]
) -> bool:
    slug, via_private_path = target
    if slug not in private:
        return False
    return via_private_path or slug not in public


# ── Stats ────────────────────────────────────────────────────────────────────


def _rate(part: float, whole: float) -> float:
    return part / whole if whole else 0.0


def _see_also_counts(body: str) -> tuple[int, int]:
    """(entries, typed entries) across a page's See Also sections."""
    entries = typed = 0
    level = 0  # heading level of the open See Also section, 0 when outside one
    for line in body.splitlines():
        if heading := _HEADING_RE.match(line):
            see_also = _SEE_ALSO_RE.match(line)
            if see_also:
                level = len(see_also.group(1))
            elif level and len(heading.group(1)) <= level:
                level = 0
            continue
        stripped = line.strip()
        if level and stripped.startswith(("-", "*")) and WIKILINK_RE.search(stripped):
            entries += 1
            typed += bool(TYPED_LINK_RE.match(stripped))
    return entries, typed


def _main_component_size(nodes: list[str], edges: dict[str, set[str]]) -> int:
    """Largest weakly connected component: link direction doesn't matter here."""
    neighbours: dict[str, set[str]] = defaultdict(set)
    for source, targets in edges.items():
        for target in targets:
            neighbours[source].add(target)
            neighbours[target].add(source)
    seen: set[str] = set()
    largest = 0
    for start in nodes:
        if start in seen:
            continue
        stack, size = [start], 0
        seen.add(start)
        while stack:
            size += 1
            for next_node in neighbours[stack.pop()] - seen:
                seen.add(next_node)
                stack.append(next_node)
        largest = max(largest, size)
    return largest


def _open_conflicts(wiki_dir: Path) -> int:
    """Conflict entries whose status isn't Resolved, so an odd status still surfaces."""
    path = wiki_dir / "_conflicts.md"
    if not path.is_file():
        return 0
    return sum(
        not status.lower().startswith("resolved") for status in _STATUS_RE.findall(path.read_text())
    )


def _band_status(healthy: bool, broken: bool) -> str:
    return "healthy" if healthy else "broken" if broken else "watch"


def _link_edges(
    pages: list[Page], slugs: dict[str, Page]
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Distinct (outbound, inbound) links between scored pages, keyed by rel. No self-links."""
    outbound: dict[str, set[str]] = {p.rel: set() for p in pages}
    inbound: dict[str, set[str]] = {p.rel: set() for p in pages}
    for page in pages:
        for match in WIKILINK_RE.finditer(page.body):
            target = slugs.get(_link_target(match.group(1))[0])
            if target is not None and target.scored and target.rel != page.rel:
                outbound[page.rel].add(target.rel)
                inbound[target.rel].add(page.rel)
    return outbound, inbound


def compute_stats(wiki_dir: Path, today: date) -> dict[str, Any]:
    """The six health numbers plus page count, hubs, domains and open conflicts.

    Private pages, tombstones and underscore files are out of every rate. Links to or from
    them make no edge. Degree counts distinct directed page pairs, so a page linking the
    same target twice adds one edge. Word counts cover the body including See Also.
    """
    public = _public_pages(wiki_dir)
    pages = [p for p in public if p.scored]
    slugs = _slug_map(public)
    total = len(pages)

    outbound, inbound = _link_edges(pages, slugs)
    see_also = typed = stale = undated = stubs = 0
    cutoff = today - timedelta(days=STALE_DAYS)
    for page in pages:
        entries, typed_entries = _see_also_counts(page.body)
        see_also += entries
        typed += typed_entries
        if page.updated is None:
            undated += 1
        elif page.updated < cutoff:
            stale += 1
        stubs += len(page.body.split()) < STUB_WORDS

    orphan = _rate(sum(not inbound[p.rel] for p in pages), total)
    degree = _rate(sum(len(v) for v in outbound.values()) * 2, total)
    component = _rate(_main_component_size([p.rel for p in pages], outbound), total)
    stale_rate = _rate(stale, total)
    typed_rate = _rate(typed, see_also)
    stub_rate = _rate(stubs, total)

    def metric(value: float, status: str) -> dict[str, Any]:
        return {"value": round(value, 4), "status": status if total else "no-data"}

    hubs = sorted(pages, key=lambda p: (-(len(inbound[p.rel]) + len(outbound[p.rel])), p.rel))
    return {
        "date": today.isoformat(),
        "pages": total,
        "metrics": {
            "orphan_rate": metric(
                orphan, _band_status(orphan < ORPHAN_HEALTHY, orphan > ORPHAN_BROKEN)
            ),
            "average_degree": metric(
                degree,
                _band_status(
                    DEGREE_HEALTHY_MIN <= degree <= DEGREE_HEALTHY_MAX, degree < DEGREE_BROKEN
                ),
            ),
            "main_component": metric(
                component,
                _band_status(component >= COMPONENT_HEALTHY, component < COMPONENT_BROKEN),
            ),
            "stale_rate": metric(stale_rate, "report"),
            "typed_link_rate": metric(typed_rate, _band_status(typed_rate >= TYPED_HEALTHY, False)),
            "stub_rate": metric(stub_rate, _band_status(stub_rate < STUB_HEALTHY, False)),
        },
        "hubs": [
            {
                "page": p.rel.removesuffix(".md"),
                "title": p.title,
                "inbound": len(inbound[p.rel]),
                "outbound": len(outbound[p.rel]),
            }
            for p in hubs[:TOP_HUBS]
        ],
        "domains": dict(sorted(Counter(p.domain for p in pages).items())),
        "open_conflicts": _open_conflicts(wiki_dir),
        "undated_pages": undated,  # no usable `updated`: not counted as stale, not known fresh
        "unparsed_pages": sum(not p.parsed for p in pages),
    }


METRIC_LABELS = {
    "orphan_rate": ("Orphan rate", True),
    "average_degree": ("Average degree", False),
    "main_component": ("Main component", True),
    "stale_rate": ("Stale rate", True),
    "typed_link_rate": ("Typed-link rate", True),
    "stub_rate": ("Stub rate", True),
}


def _render_stats(stats: dict[str, Any]) -> str:
    lines = []
    for key, (label, is_rate) in METRIC_LABELS.items():
        metric = stats["metrics"][key]
        value = f"{metric['value']:.1%}" if is_rate else f"{metric['value']:.2f}"
        lines.append(f"{label:<16} {value:>7}  {metric['status']}")
    lines += ["", f"Pages: {stats['pages']}", "", "Top hubs (in + out):"]
    lines += [
        f"  {h['inbound'] + h['outbound']:>4}  {h['page']}  ({h['inbound']} in, {h['outbound']} out)"
        for h in stats["hubs"]
    ]
    lines += ["", "Pages per domain:"]
    lines += [f"  {count:>4}  {domain}" for domain, count in stats["domains"].items()]
    lines += ["", f"Open conflicts: {stats['open_conflicts']}"]
    if stats["undated_pages"]:
        lines.append(f"Undated pages: {stats['undated_pages']}")
    if stats["unparsed_pages"]:
        lines.append(f"Pages with broken frontmatter: {stats['unparsed_pages']}")
    return "\n".join(lines)


# ── Telemetry files ──────────────────────────────────────────────────────────


def _read_tracked_jsonl(path: Path) -> list[dict[str, Any]]:
    """Rows of a tracked file. A bad line stops the run: rewriting would drop it."""
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError as e:
            raise TelemetryFileError(f"{_display(path)}:{number} is not valid JSON") from e
        if not isinstance(row, dict):
            raise TelemetryFileError(f"{_display(path)}:{number} is not a JSON object")
        rows.append(row)
    return rows


def _read_loose_jsonl(path: Path) -> list[dict[str, Any]]:
    """Rows of a log nobody rewrites here: unreadable lines are skipped."""
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(errors="replace") as handle:
        for line in handle:
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if isinstance(row, dict):
                rows.append(row)
    return rows


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(text)
    os.replace(tmp, path)


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    _write_text(path, "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def _display(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def write_snapshot(stats: dict[str, Any], telemetry_dir: Path) -> None:
    """One row per day, oldest first, capped; a same-day re-run replaces that day's row."""
    path = telemetry_dir / METRICS_FILE
    rows = [r for r in _read_tracked_jsonl(path) if r.get("date") != stats["date"]]
    rows.append(stats)
    rows.sort(key=lambda r: str(r.get("date")))
    _write_jsonl(path, rows[-METRICS_MAX_ROWS:])


def roll_operations(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Last ~30 entries in full; older ones become one `{month, count, ops}` row per month."""
    rollups = {r["month"]: r for r in rows if "month" in r}
    entries = [r for r in rows if "month" not in r]
    overflow = entries[:-OPERATIONS_KEEP_FULL] if len(entries) > OPERATIONS_KEEP_FULL else []
    for entry in overflow:
        month = str(entry.get("date"))[:7]
        rollup = rollups.setdefault(month, {"month": month, "count": 0, "ops": {}})
        op = str(entry.get("op"))
        rollup["count"] += 1
        rollup["ops"][op] = rollup["ops"].get(op, 0) + 1
    ordered = [rollups[m] for m in sorted(rollups)]
    return ordered + entries[len(overflow) :]


def _private_name_pattern(private: list[Page]) -> re.Pattern[str] | None:
    """Matches any title, slug or path of a private page, however short."""
    names: set[str] = set()
    for page in private:
        names |= {
            page.title,
            slugify(page.title),
            page.stem,
            page.rel,
            page.rel.removesuffix(".md"),
        }
    names.discard("")
    return _names_pattern(names)


def _names_pattern(names: Iterable[str]) -> re.Pattern[str] | None:
    ordered = sorted(names, key=len, reverse=True)
    if not ordered:
        return None
    alternatives = "|".join(re.escape(n) for n in ordered)
    return re.compile(rf"(?<![\w-])(?:{alternatives})(?![\w-])", re.IGNORECASE)


def _names_private_page(text: str, pattern: re.Pattern[str] | None) -> bool:
    return "wiki/private/" in text.lower() or bool(pattern and pattern.search(text))


# ── Private-leak check ───────────────────────────────────────────────────────

# Secrets and listed terms block. Contact details warn: docs are full of sample addresses.
CONTACT_CATEGORIES = {"email", "phone", "iban"}


@dataclass
class LeakReport:
    blockers: list[str]
    warnings: list[str]
    private_pages: int
    files_scanned: int
    terms_listed: int = 0


def _title_leak_pattern(private: list[Page], public: list[Page]) -> re.Pattern[str] | None:
    """Private titles and file stems of 3+ words, minus names a public page also has:
    a mention of those can't be told from a mention of the public page."""
    taken = {p.title.casefold() for p in public} | {p.stem.casefold() for p in public}
    names: set[str] = set()
    for page in private:
        if len(page.title.split()) >= TITLE_LEAK_MIN_WORDS:
            names.add(page.title)
        if len(page.stem.split("-")) >= TITLE_LEAK_MIN_WORDS:
            names.add(page.stem)
    return _names_pattern(n for n in names if n.casefold() not in taken)


def _private_path_pattern(private: list[Page]) -> re.Pattern[str] | None:
    return _names_pattern(p.rel.removesuffix(".md") for p in private)


def _sensitive_issues(
    line: str, where: str, terms: re.Pattern[str] | None, embedded: re.Pattern[str] | None
) -> tuple[list[str], list[str]]:
    """(blockers, warnings) for one public line. Says what kind of thing, never the value."""
    blockers: list[str] = []
    warnings: list[str] = []
    for finding in scan_line(0, line, terms):
        message = f"{where} contains a {finding.category}"
        (warnings if finding.category in CONTACT_CATEGORIES else blockers).append(message)
    if embedded and embedded.search(line):
        blockers.append(f"{where} text contains a private page's file name")
    return blockers, warnings


def _embedded_private_stems(private: list[Page], public: list[Page]) -> re.Pattern[str] | None:
    """Stems a public page can't also account for. Titles need word boundaries, stems don't."""
    public_stems = {p.stem.casefold() for p in public}
    return embedded_names_pattern(
        p.stem for p in private if not any(p.stem.casefold() in stem for stem in public_stems)
    )


def run_check(wiki_dir: Path, telemetry_dir: Path) -> LeakReport | None:
    """Scan public text for private references. None when there is no private/ (CI)."""
    if not (wiki_dir / "private").is_dir():
        return None
    private_pages = _private_pages(wiki_dir)
    public_pages = _public_pages(wiki_dir)
    private = _slug_map(private_pages)
    public = _slug_map(public_pages)
    titles = _title_leak_pattern(private_pages, public_pages)
    paths = _private_path_pattern(private_pages)
    terms = terms_pattern(load_terms(wiki_dir))
    embedded = _embedded_private_stems(private_pages, public_pages)

    report = LeakReport([], [], len(private_pages), 0, len(load_terms(wiki_dir)))

    def scan(path: Path, path_mention_blocks: bool) -> None:
        report.files_scanned += 1
        for number, line in enumerate(path.read_text(errors="replace").splitlines(), start=1):
            where = f"{_display(path)}:{number}"
            blockers, warnings = _sensitive_issues(line, where, terms, embedded)
            report.blockers.extend(blockers)
            report.warnings.extend(warnings)
            if any(
                _links_to_private(_link_target(m.group(1)), public, private)
                for m in WIKILINK_RE.finditer(line)
            ):
                report.blockers.append(f"{where} wikilink resolves to a private page")
            elif paths and paths.search(line):
                target = report.blockers if path_mention_blocks else report.warnings
                target.append(f"{where} text contains a private page's path")
            elif titles and titles.search(line):
                report.warnings.append(f"{where} text contains a private page's title or file name")

    for md in _public_files(wiki_dir):
        scan(md, path_mention_blocks=False)
    if telemetry_dir.is_dir():
        for jsonl in sorted(telemetry_dir.glob("*.jsonl")):
            if jsonl.name not in UNTRACKED_TELEMETRY:
                scan(jsonl, path_mention_blocks=True)
    return report


def check_file(path: Path, wiki_dir: Path) -> list[str]:
    """Blocking rules for one file, for the post-write hook.

    Reads only private/ unless a link matches a private page; only then does it pay for
    the public scan that rules out a public page with the same name.
    """
    if not path.is_file():
        return []
    private_pages = _private_pages(wiki_dir)
    private = _slug_map(private_pages)
    terms = terms_pattern(load_terms(wiki_dir))
    embedded = embedded_names_pattern(private_names(wiki_dir) & {p.stem for p in private_pages})
    issues: list[str] = []
    hits: list[tuple[int, tuple[str, bool]]] = []
    for number, line in enumerate(path.read_text(errors="replace").splitlines(), start=1):
        blockers, _ = _sensitive_issues(line, f"{_display(path)}:{number}", terms, embedded)
        issues.extend(blockers)
        for match in WIKILINK_RE.finditer(line):
            target = _link_target(match.group(1))
            if target[0] in private:
                hits.append((number, target))
    if hits:
        public = _slug_map(_public_pages(wiki_dir))
        lines = sorted({number for number, t in hits if _links_to_private(t, public, private)})
        issues.extend(f"{_display(path)}:{n} wikilink resolves to a private page" for n in lines)
    return issues


# ── Gaps ─────────────────────────────────────────────────────────────────────


@dataclass
class Gap:
    name: str
    first_seen: str
    count: int


@dataclass
class AskedGaps:
    gaps: list[Gap]
    withheld: int  # named a private page, so not written out
    degraded_skipped: int  # zero results while retrieval was degraded: no evidence either way


def _asked_gaps(
    telemetry_dir: Path,
    retrieval_log: Path,
    public: dict[str, Page],
    private_names: re.Pattern[str] | None,
) -> AskedGaps:
    seen: dict[str, dict[str, Any]] = {}

    def add(topic: str, day: str) -> None:
        key = " ".join(topic.lower().split())
        entry = seen.setdefault(key, {"name": " ".join(topic.split()), "first": day, "count": 0})
        entry["first"] = min(entry["first"], day)
        entry["count"] += 1

    for row in _read_loose_jsonl(telemetry_dir / ASKED_FILE):
        if row.get("topic"):
            add(str(row["topic"]), str(row.get("date", ""))[:10])

    # A query later answered is no longer a gap, so only the latest healthy search counts.
    misses: dict[str, list[tuple[str, str]]] = defaultdict(list)
    latest_hit: dict[str, bool] = {}
    degraded_skipped = 0
    for row in _read_loose_jsonl(retrieval_log):
        if row.get("tool") not in QUERY_TOOLS or not row.get("query"):
            continue
        key = " ".join(str(row["query"]).lower().split())
        hit = bool(row.get("n_results"))
        if row.get("degraded"):
            degraded_skipped += not hit
            continue
        latest_hit[key] = hit
        if not hit:
            misses[key].append((str(row["query"]), str(row.get("ts", ""))[:10]))
    for key, rows in misses.items():
        if not latest_hit[key]:
            for query, day in rows:
                add(query, day)

    gaps: list[Gap] = []
    withheld = 0
    for key, entry in seen.items():
        if _names_private_page(entry["name"], private_names):
            withheld += 1
        elif (page := public.get(slugify(key))) is None or not page.scored:
            gaps.append(Gap(entry["name"], entry["first"], entry["count"]))
    return AskedGaps(gaps, withheld, degraded_skipped)


@dataclass
class CourseGaps:
    modules: list[Gap]  # first_seen filled in by _apply_first_seen
    links: list[Gap]
    withheld: int  # lesson links into private pages or tombstones
    note: str | None  # why the course sections couldn't be computed


def _course_gaps(
    courses_dir: Path, wiki_dir: Path, public: dict[str, Page], private: dict[str, Page]
) -> CourseGaps:
    """Empty curriculum modules and lesson links with no page.

    Builds the catalog with semantic linking off: that path loads an embedding model, and
    a gap list that shifts with the model's state wouldn't be deterministic. A module counts
    as covered through explicit, compiled or title-mention links, a stricter bar than the
    map's filter panel, which also shows embedding neighbours.
    """
    try:
        from app.backend import courses, curriculum
    except ImportError as e:
        return CourseGaps(
            [], [], 0, f"unavailable: {e.name or 'import'} missing (needs the api extra)"
        )

    original = courses._semantic_neighbours
    courses._semantic_neighbours = lambda *_: None
    try:
        signature = courses._signature(courses_dir, wiki_dir)
        cat = courses._load(courses_dir, wiki_dir, signature)
        built = curriculum._build(cat, [])
    except (yaml.YAMLError, OSError, ValueError) as e:
        return CourseGaps([], [], 0, f"unavailable: {type(e).__name__} while reading the courses")
    finally:
        courses._semantic_neighbours = original

    lesson_counts = {
        (c["id"], m["id"]): len(m["lessons"]) for c in cat.courses for m in c["modules"]
    }
    modules: list[Gap] = []
    for course in built["courses"]:
        for module in course["modules"]:
            lessons = lesson_counts.get((course["id"], module["id"]), 0)
            if lessons and not module["pageIds"]:
                name = f"{course['id']}/{module['id']}: {module['title']}"
                modules.append(Gap(name, "", lessons))

    linking: dict[str, set[str]] = defaultdict(set)
    names: dict[str, str] = {}
    withheld: set[str] = set()
    for lesson_id in cat.lessons:
        post = frontmatter.load(courses_dir / f"{lesson_id}.md")
        targets = [str(t) for t in post.get("wiki") or []]
        # Code holds things like [[1, 2]]: not links.
        prose = _INLINE_CODE_RE.sub("", courses._prose(post.content))
        targets += [m.group(1) for m in WIKILINK_RE.finditer(prose)]
        for target in targets:
            slug = _link_target(target)[0]
            if not re.search(r"[a-z]", slug):
                continue
            if (page := public.get(slug)) is not None:
                if not page.scored:
                    withheld.add(slug)
            elif slug in private:
                withheld.add(slug)
            else:
                linking[slug].add(lesson_id)
                names.setdefault(slug, target.strip())
    links = [Gap(names[slug], "", len(ids)) for slug, ids in linking.items()]
    return CourseGaps(modules, links, len(withheld), None)


def _apply_first_seen(gaps: list[Gap], previous: dict[str, str], today: str) -> None:
    """Earliest of what the sources say and what the last gaps.md recorded."""
    for gap in gaps:
        known = [d for d in (gap.first_seen, previous.get(gap.name)) if d]
        gap.first_seen = min(known) if known else today


def _sorted_gaps(gaps: list[Gap]) -> list[Gap]:
    return sorted(gaps, key=lambda g: (-g.count, g.first_seen, g.name.lower()))


def _gap_lines(gaps: list[Gap]) -> list[str]:
    return [f"- {g.name} | first seen {g.first_seen} | count {g.count}" for g in gaps] or ["- none"]


def regenerate_gaps(
    wiki_dir: Path, telemetry_dir: Path, courses_dir: Path, retrieval_log: Path, today: date
) -> list[str]:
    """Write gaps.md; returns its top five lines, real demand (asked) ranked first."""
    public_pages = _public_pages(wiki_dir)
    private_pages = _private_pages(wiki_dir)
    public = _slug_map(public_pages)
    private = _slug_map(private_pages)
    path = telemetry_dir / GAPS_FILE
    previous = dict(_GAP_LINE_RE.findall(path.read_text())) if path.is_file() else {}

    asked = _asked_gaps(telemetry_dir, retrieval_log, public, _private_name_pattern(private_pages))
    course = _course_gaps(courses_dir, wiki_dir, public, private)
    day = today.isoformat()
    for group in (asked.gaps, course.modules, course.links):
        _apply_first_seen(group, previous, day)
    asked_sorted = _sorted_gaps(asked.gaps)
    modules = _sorted_gaps(course.modules)
    links = _sorted_gaps(course.links)

    lines = [
        f"# Wiki gaps ({day})",
        "",
        "Generated by `core/wiki_telemetry.py gaps`; do not edit. Gitignored: holds query history.",
        "",
        "## Asked, not answered",
        "",
        ASKED_FLOOR_NOTE,
    ]
    if asked.degraded_skipped:
        lines.append(f"Skipped {asked.degraded_skipped} empty results from degraded retrieval.")
    if asked.withheld:
        lines.append(f"Withheld {asked.withheld} that name a private page.")
    lines += ["", *_gap_lines(asked_sorted), "", "## Curriculum modules with no page", ""]
    lines.append(
        "Covered means an explicit, compiled or title-mention link from a lesson; "
        "embedding neighbours don't count. Count is the module's lessons."
    )
    lines += ["", *([f"- {course.note}"] if course.note else _gap_lines(modules))]
    lines += ["", "## Linked from lessons, missing in wiki", ""]
    lines.append("Count is the lessons linking it.")
    if course.withheld:
        lines.append(f"Withheld {course.withheld} that point at a private or retired page.")
    lines += ["", *([f"- {course.note}"] if course.note else _gap_lines(links)), ""]
    _write_text(path, "\n".join(lines))

    ranked = [
        *(("asked", g) for g in asked_sorted),
        *(("lesson link", g) for g in links),
        *(("module", g) for g in modules),
    ]
    return [
        f"{kind}: {g.name} (first seen {g.first_seen}, count {g.count})"
        for kind, g in ranked[:TOP_GAPS]
    ]


# ── CLI ──────────────────────────────────────────────────────────────────────


def _cmd_stats(args: argparse.Namespace) -> int:
    stats = compute_stats(args.wiki_dir, args.today)
    print(json.dumps(stats, indent=2, ensure_ascii=False) if args.json else _render_stats(stats))
    return 0


def _graph_shape(wiki_dir: Path) -> dict[str, Any]:
    """Cluster count, unsettled pages and stability for a snapshot row: report-only, no bands."""
    # Imported here: wiki_graph imports this module, and only snapshots need networkx and sklearn.
    from core.wiki_graph import analyse, load_graph

    report = analyse(load_graph(wiki_dir))
    return {
        "clusters": len(report.clusters),
        "unsettled": report.unsettled,
        "stability": report.stability,
    }


def _cmd_snapshot(args: argparse.Namespace) -> int:
    stats = compute_stats(args.wiki_dir, args.today)
    write_snapshot({**stats, **_graph_shape(args.wiki_dir)}, args.telemetry_dir)
    print(_render_stats(stats))
    print(f"\nSnapshot {stats['date']} written to {_display(args.telemetry_dir / METRICS_FILE)}")
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    if not (args.wiki_dir / "private").is_dir():
        print("check: no private/ directory here, nothing to compare against")
        return 0
    if args.file:
        blockers = check_file(args.file, args.wiki_dir)
        for line in blockers:
            print(f"BLOCKER {line}")
        return 1 if blockers else 0
    report = run_check(args.wiki_dir, args.telemetry_dir)
    assert report is not None  # private/ exists: checked above
    for line in report.blockers:
        print(f"BLOCKER {line}")
    for line in report.warnings:
        print(f"WARN {line}")
    print(
        f"check: {len(report.blockers)} blocker(s), {len(report.warnings)} warning(s), "
        f"{report.files_scanned} files against {report.private_pages} private pages, "
        f"{report.terms_listed} sensitive terms"
    )
    return 1 if report.blockers else 0


def _cmd_log(args: argparse.Namespace) -> int:
    if not _OP_RE.match(args.op):
        print("log: op must be one lowercase word, e.g. ingest", file=sys.stderr)
        return 2
    pattern = _private_name_pattern(_private_pages(args.wiki_dir))
    if _names_private_page(f"{args.op} {args.detail}", pattern):
        print(
            "log: refused, this text names a private page and operations.jsonl is public",
            file=sys.stderr,
        )
        return 2
    findings = scan_text(f"{args.op} {args.detail}", terms_pattern(load_terms(args.wiki_dir)))
    if findings:
        categories = ", ".join(sorted({f.category for f in findings}))
        print(
            f"log: refused, operations.jsonl is public and this text has: {categories}",
            file=sys.stderr,
        )
        return 2
    path = args.telemetry_dir / OPERATIONS_FILE
    rows = _read_tracked_jsonl(path)
    rows.append({"date": args.today.isoformat(), "op": args.op, "detail": args.detail})
    _write_jsonl(path, roll_operations(rows))
    return 0


def _cmd_ask(args: argparse.Namespace) -> int:
    path = args.telemetry_dir / ASKED_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as handle:
        row = {"date": args.today.isoformat(), "topic": args.topic}
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return 0


def _cmd_gaps(args: argparse.Namespace) -> int:
    top = regenerate_gaps(
        args.wiki_dir, args.telemetry_dir, args.courses_dir, args.retrieval_log, args.today
    )
    print(f"Wrote {_display(args.telemetry_dir / GAPS_FILE)}. Top {len(top)}:")
    for line in top:
        print(f"  {line}")
    return 0


def _parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--wiki-dir", type=Path, default=WIKI_DIR)
    common.add_argument("--telemetry-dir", type=Path, default=TELEMETRY_DIR)
    common.add_argument("--courses-dir", type=Path, default=COURSES_DIR)
    common.add_argument("--retrieval-log", type=Path, default=RETRIEVAL_LOG)
    common.add_argument(
        "--today", type=date.fromisoformat, default=None, help="YYYY-MM-DD, for tests"
    )

    parser = argparse.ArgumentParser(description="Deterministic wiki health telemetry.")
    commands = parser.add_subparsers(dest="command", required=True)
    stats = commands.add_parser("stats", parents=[common], help="print the health numbers")
    stats.add_argument("--json", action="store_true")
    stats.set_defaults(func=_cmd_stats)
    snapshot = commands.add_parser("snapshot", parents=[common], help="stats + one metrics row")
    snapshot.set_defaults(func=_cmd_snapshot)
    check = commands.add_parser("check", parents=[common], help="private-leak check")
    check.add_argument("--file", type=Path, help="only this file's wikilinks (post-write hook)")
    check.set_defaults(func=_cmd_check)
    log = commands.add_parser("log", parents=[common], help="append to operations.jsonl")
    log.add_argument("op")
    log.add_argument("detail")
    log.set_defaults(func=_cmd_log)
    ask = commands.add_parser("ask", parents=[common], help="append to asked.jsonl")
    ask.add_argument("topic")
    ask.set_defaults(func=_cmd_ask)
    gaps = commands.add_parser("gaps", parents=[common], help="regenerate gaps.md")
    gaps.set_defaults(func=_cmd_gaps)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    args.today = args.today or date.today()
    if not args.wiki_dir.is_dir():
        print(f"{args.command}: wiki dir not found: {args.wiki_dir}", file=sys.stderr)
        return 2
    try:
        return args.func(args)
    except TelemetryFileError as e:
        print(f"{args.command}: {e}; fix the line and re-run", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
