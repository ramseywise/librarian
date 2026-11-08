"""Batch close-out: which pages each raw source produced, and what still needs a human.

    uv run librarian ingest closeout data/raw/papers/a.md data/raw/papers/b.md
    uv run librarian ingest closeout --from batch3.paths --pages-out pages.txt --mark

For each raw source this finds the public wiki pages whose `sources:` cite it (pages under
`private/` are only counted, never named) and prints `source -> page, page`. Two things are
flagged for the coordinator:

- `NO PAGES`: nothing cites the source, so it was not compiled (exit 1).
- `INCONSISTENT`: the extraction has an "internal inconsistencies" heading, so each page
  citing it must carry that in `## Limits`; pages with no `## Limits` section are named.

`--pages-out` writes the deduplicated public page list (the input to `ingest overlap`, `wiki
verify` and the reviewer). `--mark` records every source that has pages in the manifest, with
its pages (private ones included), in one locked session; sources with no pages are never
marked.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import frontmatter
import yaml

from librarian.config import get_settings
from librarian.ingest.manifest import ManifestSession

REPO_ROOT = get_settings().root
WIKI_DIR = get_settings().wiki_dir

_INCONSISTENT_RE = re.compile(r"internal\s+inconsistenc", re.IGNORECASE)
_LIMITS_RE = re.compile(r"^##\s+Limits\s*$", re.MULTILINE | re.IGNORECASE)


@dataclass
class SourceReport:
    source: str
    pages: list[str] = field(default_factory=list)
    private_pages: list[str] = field(default_factory=list)
    inconsistent: bool = False
    pages_without_limits: list[str] = field(default_factory=list)


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _cited_by(wiki_dir: Path) -> dict[str, list[Path]]:
    """Every raw path any page lists in `sources:`, mapped to the pages that list it."""
    index: dict[str, list[Path]] = {}
    for page in sorted(wiki_dir.rglob("*.md")):
        if page.name.startswith("_"):
            continue
        try:
            raw = frontmatter.loads(page.read_text()).metadata.get("sources") or []
        except (ValueError, yaml.YAMLError):  # a malformed page is lint's to report
            continue
        listed = [raw] if isinstance(raw, str) else raw if isinstance(raw, list) else []
        for source in listed:
            index.setdefault(str(source), []).append(page)
    return index


def closeout(sources: list[Path], wiki_dir: Path = WIKI_DIR) -> list[SourceReport]:
    """One report per source, in the order given."""
    cited = _cited_by(wiki_dir)
    private_dir = wiki_dir / "private"
    reports: list[SourceReport] = []
    for path in sources:
        rel = _rel(path)
        report = SourceReport(rel)
        for page in cited.get(rel, []):
            if page.is_relative_to(private_dir):
                report.private_pages.append(_rel(page))
                continue
            report.pages.append(_rel(page))
        absolute = path if path.is_absolute() else REPO_ROOT / path
        if absolute.is_file() and _INCONSISTENT_RE.search(absolute.read_text()):
            report.inconsistent = True
            report.pages_without_limits = [
                p for p in report.pages if not _LIMITS_RE.search((REPO_ROOT / p).read_text())
            ]
        reports.append(report)
    return reports


def _read_list(path: Path) -> list[Path]:
    """Paths from a file, one per line; a tab ends the path, blank lines are skipped."""
    lines = (line.split("\t")[0].strip() for line in path.read_text().splitlines())
    return [Path(line) for line in lines if line]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    ap.add_argument("sources", nargs="*", type=Path, help="raw files the batch compiled")
    ap.add_argument("--from", dest="from_file", type=Path, help="file listing raw paths")
    ap.add_argument("--pages-out", type=Path, help="write the public page list here")
    ap.add_argument("--mark", action="store_true", help="record sources with pages")
    args = ap.parse_args(argv)
    sources = list(args.sources) + (_read_list(args.from_file) if args.from_file else [])
    if not sources:
        ap.error("give raw sources or --from FILE")

    reports = closeout(sources, WIKI_DIR)
    for r in reports:
        private = f" (+{len(r.private_pages)} private)" if r.private_pages else ""
        print(f"{r.source} -> {', '.join(r.pages) or 'NO PAGES'}{private}")
        if r.inconsistent:
            missing = ", ".join(r.pages_without_limits) or "none"
            print(
                f"  INCONSISTENT: extraction lists inconsistencies; pages without ## Limits: {missing}"
            )

    pages = sorted({p for r in reports for p in r.pages})
    if args.pages_out:
        args.pages_out.write_text("".join(f"{p}\n" for p in pages))
    if args.mark:
        with ManifestSession() as ms:
            for r in reports:
                if r.pages or r.private_pages:
                    ms.mark(REPO_ROOT / r.source, r.pages + r.private_pages)

    unmapped = [r.source for r in reports if not r.pages and not r.private_pages]
    flagged = sum(r.inconsistent for r in reports)
    print(
        f"{len(reports)} source(s), {len(pages)} public page(s), {len(unmapped)} with no pages, "
        f"{flagged} with internal inconsistencies" + (", marked" if args.mark else ""),
        file=sys.stderr,
    )
    return 1 if unmapped else 0


if __name__ == "__main__":
    sys.exit(main())
