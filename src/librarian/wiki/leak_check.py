"""The private-leak check: what a public file may not name, link to or contain."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from librarian.ingest.sensitive import (
    embedded_names_pattern,
    load_terms,
    private_names,
    scan_line,
    terms_pattern,
)
from librarian.wiki import course_leaks
from librarian.wiki.common import (
    WIKILINK_RE,
    slugify,
)
from librarian.wiki.oplog import UNTRACKED_TELEMETRY, _display
from librarian.wiki.pages import (
    Page,
    _link_index,
    _links_to_private,
    _private_pages,
    _public_files,
    _public_pages,
)

# Titles shorter than this are too generic to call a mention a leak.
TITLE_LEAK_MIN_WORDS = 3
# Secrets and listed terms block. Contact details warn: docs are full of sample addresses.
CONTACT_CATEGORIES = {"email", "phone", "iban"}


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


def run_check(
    wiki_dir: Path, telemetry_dir: Path, courses_dir: Path | None = None
) -> LeakReport | None:
    """Scan public text for private references. None when there is no private/ (CI).

    Public lessons under `courses_dir` are scanned too, with or without a wiki private/:
    a link into data/courses/private/ is a leak whether or not that tree exists here.
    """
    if not (wiki_dir / "private").is_dir():
        if courses_dir is None:
            return None
        blockers, scanned = course_leaks.scan_public_lessons(
            courses_dir, lambda _raw: False, _display
        )
        return LeakReport(blockers, [], 0, scanned)
    private_pages = _private_pages(wiki_dir)
    public_pages = _public_pages(wiki_dir)
    private = _link_index(private_pages)
    public = _link_index(public_pages)
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
                _links_to_private(m.group(1), public, private) for m in WIKILINK_RE.finditer(line)
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
    if courses_dir is not None:
        blockers, scanned = course_leaks.scan_public_lessons(
            courses_dir,
            lambda raw: _links_to_private(raw, public, private),
            _display,
        )
        report.blockers.extend(blockers)
        report.files_scanned += scanned
    return report


def check_file(path: Path, wiki_dir: Path) -> list[str]:
    """Blocking rules for one file, for the post-write hook.

    Reads only private/ unless a link matches a private page; only then does it pay for
    the public scan that rules out a public page with the same name.
    """
    if not path.is_file():
        return []
    private_pages = _private_pages(wiki_dir)
    private = _link_index(private_pages)
    terms = terms_pattern(load_terms(wiki_dir))
    embedded = embedded_names_pattern(private_names(wiki_dir) & {p.stem for p in private_pages})
    issues: list[str] = []
    hits: list[tuple[int, str]] = []
    for number, line in enumerate(path.read_text(errors="replace").splitlines(), start=1):
        blockers, _ = _sensitive_issues(line, f"{_display(path)}:{number}", terms, embedded)
        issues.extend(blockers)
        for match in WIKILINK_RE.finditer(line):
            if private.resolve(match.group(1), only_private=True) is not None:
                hits.append((number, match.group(1)))
    if hits:
        public = _link_index(_public_pages(wiki_dir))
        lines = sorted({number for number, t in hits if _links_to_private(t, public, private)})
        issues.extend(f"{_display(path)}:{n} wikilink resolves to a private page" for n in lines)
    return issues
