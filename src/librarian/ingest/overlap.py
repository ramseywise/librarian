"""Copied-wording check: phrases a wiki page shares word for word with its raw sources.

    uv run librarian ingest overlap data/wiki/eval/mle-bench.md
    uv run librarian ingest overlap <pages> --source data/raw/papers/x.md --words 10

A page is public once pushed and must paraphrase its source. For each page this compares the
body (frontmatter and `## See Also` left out) with every raw file in its `sources:`, or with
the `--source` files given, and prints `page:line — "phrase"` for each run of `--words` or
more consecutive words (default 8) that also appears in a source. Case and punctuation are
ignored; a run that spans lines is reported at its first line. Exit 1 when anything matches.
Run it before the ingest reviewer, which then only has to judge what is left.

`--since REV` reports only runs that start on a line added since that git revision (a page not
in REV counts as all added), so an ingest that appends one line to an old page is not charged
with the page's older wording: `--since HEAD` checks just the uncommitted text.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import frontmatter

from librarian.config import get_settings

REPO_ROOT = get_settings().root
DEFAULT_WORDS = 8

_WORD_RE = re.compile(r"[a-z0-9]+(?:['’][a-z]+)?")
_LINK_RE = re.compile(r"\[\[[^\]]*\]\]")
_SEE_ALSO_RE = re.compile(r"^##\s+See Also\s*$", re.MULTILINE | re.IGNORECASE)


@dataclass(frozen=True)
class Match:
    page: Path
    line: int
    phrase: str


def _words(text: str) -> list[str]:
    return _WORD_RE.findall(text.lower())


def _body_lines(path: Path) -> tuple[list[tuple[int, str]], list[str]]:
    """The page's checked lines as (line number, text), and its `sources:` list."""
    text = path.read_text()
    post = frontmatter.loads(text)
    raw = post.metadata.get("sources") or []
    sources: list[object] = (
        [raw] if isinstance(raw, str) else list(raw) if isinstance(raw, list) else []
    )
    offset = text.count("\n", 0, text.find(post.content)) if post.content else 0
    body = post.content
    cut = _SEE_ALSO_RE.search(body)
    if cut:
        body = body[: cut.start()]
    lines = [(offset + i + 1, _LINK_RE.sub(" ", line)) for i, line in enumerate(body.splitlines())]
    return lines, [str(s) for s in sources]


def _ngrams(words: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


def _resolve(source: str) -> Path:
    path = Path(source)
    return path if path.is_absolute() else REPO_ROOT / path


def overlaps(page: Path, sources: list[Path] | None = None, n: int = DEFAULT_WORDS) -> list[Match]:
    """Each maximal run of `n`+ page words that a source contains, at the line it starts on."""
    lines, listed = _body_lines(page)
    paths = sources if sources is not None else [_resolve(s) for s in listed]
    grams: set[tuple[str, ...]] = set()
    for path in paths:
        if path.is_file():
            grams |= _ngrams(_words(path.read_text()), n)
    tokens = [(lineno, w) for lineno, text in lines for w in _words(text)]
    words = [w for _, w in tokens]
    matches: list[Match] = []
    i = 0
    while i <= len(words) - n:
        if tuple(words[i : i + n]) not in grams:
            i += 1
            continue
        end = i + n
        while end < len(words) and tuple(words[end - n + 1 : end + 1]) in grams:
            end += 1
        matches.append(Match(page, tokens[i][0], " ".join(words[i:end])))
        i = end
    return matches


_HUNK_RE = re.compile(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@", re.MULTILINE)


def added_lines(page: Path, rev: str) -> set[int] | None:
    """Line numbers of `page` added since `rev`; None when the page is not in `rev` (all new)."""
    rel = _rel(page)
    known = subprocess.run(
        ["git", "cat-file", "-e", f"{rev}:{rel}"], cwd=REPO_ROOT, capture_output=True
    )
    if known.returncode != 0:
        return None
    diff = subprocess.run(
        ["git", "diff", "-U0", rev, "--", rel],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    lines: set[int] = set()
    for m in _HUNK_RE.finditer(diff):
        start, count = int(m.group(1)), int(m.group(2) or 1)
        lines.update(range(start, start + count))
    return lines


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    ap.add_argument("pages", nargs="+", type=Path, help="wiki pages to check")
    ap.add_argument(
        "--source",
        action="append",
        type=Path,
        help="raw file to compare with (repeatable); default: each page's sources:",
    )
    ap.add_argument("--words", type=int, default=DEFAULT_WORDS, help="shortest run reported")
    ap.add_argument("--since", metavar="REV", help="only runs on lines added since this revision")
    args = ap.parse_args(argv)
    found = 0
    for page in args.pages:
        sources = [_resolve(str(s)) for s in args.source] if args.source else None
        listed = sources if sources is not None else [_resolve(s) for s in _body_lines(page)[1]]
        missing = [s for s in listed if not s.is_file()]
        for path in missing:
            print(f"WARN {_rel(page)}: source not found: {_rel(path)}", file=sys.stderr)
        fresh = added_lines(page, args.since) if args.since else None
        for m in overlaps(page, sources, args.words):
            if args.since and fresh is not None and m.line not in fresh:
                continue
            found += 1
            print(f'{_rel(m.page)}:{m.line} — "{m.phrase}"')
    if found:
        print(f"{found} copied run(s) of {args.words}+ words: paraphrase them", file=sys.stderr)
        return 1
    print(f"OK {len(args.pages)} page(s): no run of {args.words}+ words copied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
