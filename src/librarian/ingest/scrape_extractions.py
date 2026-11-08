"""Course reading extractions from learn-ai-engineering → raw/papers/

The sibling's `source-reader` writes one JSON extraction per paper or book chapter it reads
(`scripts/papers/extractions/<key>.json`: question, method, results with their setup, limits,
terms, lineage). Each becomes one markdown source here, so `/ingest data/raw/papers/` can
compile them into the wiki like any other raw input.

Append-only, as all of raw/ is: a file is named by the date the source was read and the PDF
it came from (`2026-11-08-zeng-2022-glm-130b.md`) and is never rewritten. A re-read on a
later date lands as a new file. The PDFs themselves are not copied; `extracted_from` is the
path inside the sibling (served locally through COURSE_SOURCES_DIR).

Usage:
    uv run librarian scrape extractions
    uv run librarian scrape extractions --dry-run
    uv run librarian scrape extractions --home generative-ai
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import structlog
import yaml

from librarian.config import get_settings
from librarian.ingest.base import ScraperBase

log = structlog.get_logger()

DEFAULT_OUTPUT_DIR = get_settings().raw_dir / "papers"
EXTRACTIONS = Path("scripts") / "papers" / "extractions"


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def filename(extraction: dict[str, Any]) -> str:
    """`<read date>-<pdf stem>.md`; a book chapter keeps its book folder (`<book>-ch05-x`)."""
    date = str((extraction.get("read") or {}).get("at", ""))[:10]
    pdf = extraction.get("pdf")
    if pdf:
        path = Path(pdf)
        stem = path.stem if path.parent.name == "sources" else f"{path.parent.name}-{path.stem}"
    else:
        stem = str(extraction.get("key", ""))
    return f"{date}-{_slug(stem)[:80]}.md"


def _bullets(items: list[Any], fmt: Callable[[Any], str] = str) -> list[str]:
    return [f"- {fmt(i)}" for i in items if i]


def _result(r: dict[str, Any]) -> str:
    parts = [r.get("claim", "")]
    if r.get("setup"):
        parts.append(f"Setup: {r['setup']}")
    if r.get("kind") and r["kind"] != "measured":
        parts.append(f"({r['kind']})")
    return " ".join(p for p in parts if p)


def _term(t: dict[str, Any]) -> str:
    return f"**{t.get('term', '')}**: {t.get('definition', '')}"


def _lineage(entry: dict[str, Any]) -> str:
    ident = f" (arXiv:{entry['arxiv']})" if entry.get("arxiv") else ""
    note = f": {entry['note']}" if entry.get("note") else ""
    return f"{entry.get('relation', 'related')} {entry.get('work', '')}, {entry.get('year', '')}{ident}{note}"


def _code(c: dict[str, Any]) -> str:
    return f"{c.get('where', '')}:\n\n```\n{c.get('snippet', '')}\n```\n"


def render(extraction: dict[str, Any]) -> str:
    """The extraction as a raw markdown source: frontmatter, then one section per field."""
    bib = extraction.get("bib") or {}
    pdf = extraction.get("pdf") or ""
    front = {
        "title": bib.get("title") or extraction.get("key"),
        "source_type": "reading-extraction",
        "key": extraction.get("key"),
        "type": extraction.get("type") or "unclassified",
        "year": bib.get("year"),
        "arxiv": bib.get("arxiv"),
        "doi": bib.get("doi"),
        "course_home": pdf.split("/")[0] if pdf else None,
        "extracted_from": f"learn-ai-engineering/{pdf}" if pdf else None,
        "read_at": str((extraction.get("read") or {}).get("at", "")),
        "confidence": "medium",
    }
    front = {k: v for k, v in front.items() if v}
    lines = [f"---\n{yaml.safe_dump(front, sort_keys=False, allow_unicode=True)}---\n"]
    lines.append(f"# {front['title']}\n")
    authors = bib.get("authors") or ([bib["first_author"]] if bib.get("first_author") else [])
    if authors:
        more = " et al." if len(authors) > 3 else ""
        lines.append(
            f"Authors: {', '.join(authors[:3])}{more}. Venue: {bib.get('venue') or 'n/a'}.\n"
        )

    method = extraction.get("method") or {}
    sections: list[tuple[str, list[str]]] = [
        ("Question", [extraction.get("question") or ""]),
        ("Hypothesis", [extraction.get("hypothesis") or ""]),
        ("Contributions", _bullets(extraction.get("contributions") or [])),
        ("Method", [method.get("summary", "") if isinstance(method, dict) else str(method)]),
        ("Results", _bullets(extraction.get("results") or [], _result)),
        ("Limits", _bullets(extraction.get("limits") or [])),
        ("Practices", _bullets(extraction.get("practices") or [], _practice)),
        ("Terms", _bullets(extraction.get("terms") or [], _term)),
        ("Lineage", _bullets(extraction.get("lineage") or [], _lineage)),
        ("Code", [_code(c) for c in extraction.get("code") or []]),
        ("Report", [extraction.get("legacy_report") or ""]),
    ]
    for heading, body in sections:
        body = [b for b in body if b and b.strip()]
        if body:
            lines.append(f"## {heading}\n\n" + "\n".join(body) + "\n")
    return "\n".join(lines)


def _practice(p: object) -> str:
    if isinstance(p, dict):
        return " ".join(str(v) for v in p.values() if v)
    return str(p)


class ExtractionsScraper(ScraperBase):
    source_name = "scrape-extractions"
    output_dir = DEFAULT_OUTPUT_DIR

    def __init__(
        self,
        sibling: Path | None = None,
        output_dir: Path = DEFAULT_OUTPUT_DIR,
        home: str | None = None,
    ) -> None:
        self._sibling = sibling or get_settings().course_sources_dir
        self.output_dir = output_dir
        self._home = home

    def run(self, dry_run: bool = False) -> list[Path]:
        source = self._sibling / EXTRACTIONS
        if not source.is_dir():
            log.warning("extractions_missing", path=str(source))
            return []
        written: list[Path] = []
        skipped = 0
        for path in sorted(source.glob("*.json")):
            try:
                extraction = json.loads(path.read_text())
            except (OSError, json.JSONDecodeError) as exc:
                log.warning("extraction_unreadable", path=path.name, error=str(exc))
                continue
            pdf = extraction.get("pdf") or ""
            if self._home and not pdf.startswith(self._home + "/"):
                continue
            dest = self.output_dir / filename(extraction)
            key = f"key: {yaml.safe_dump(extraction.get('key')).splitlines()[0]}\n"
            if dest in written or (dest.exists() and key not in dest.read_text()[:2000]):
                # Another reading (the same paper filed in two homes) has the name: add the key.
                dest = dest.with_name(f"{dest.stem}-{_slug(str(extraction.get('key')))[-24:]}.md")
            if dest.exists():  # raw/ is append-only: never rewrite a source
                skipped += 1
                continue
            written.append(dest)
            if not dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(render(extraction))
        prefix = "[dry-run] " if dry_run else ""
        print(
            f"{prefix}{len(written)} new extractions → {self.output_dir} ({skipped} already there)"
        )
        if written and not dry_run:
            print("Next: /ingest data/raw/papers/ to compile them into the wiki.")
        return written

    @classmethod
    def _add_args(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--sibling", type=Path, help="learn-ai-engineering checkout")
        parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
        parser.add_argument("--home", help="only extractions of PDFs in this course home")

    @classmethod
    def _from_args(cls, args: argparse.Namespace) -> ExtractionsScraper:
        return cls(sibling=args.sibling, output_dir=args.output_dir, home=args.home)


def main(argv: list[str] | None = None) -> None:
    ExtractionsScraper.cli(description="Course reading extractions → raw/papers/", argv=argv)


if __name__ == "__main__":
    main()
