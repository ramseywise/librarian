"""Pages split into heading sections: the unit search returns in full and embeds beside the page.

A page is still what search ranks. Sections let it return the part of a page that answers the
query instead of its first lines, and give the page a second, finer semantic signal.

Split rules (`split_sections`): break at `#`, `##` and `###` outside fenced code; drop the
`## See Also` section; fold a section shorter than `section_min_chars` into the next one (the
last one into the one before it); cut a section longer than `section_max_chars` at blank lines,
never inside a fence, so a long code block stays whole. Both thresholds are settings, so chunk
size can be compared on the evals rather than fixed by hand.

The splitter is deterministic, so `read_page("page#Heading")` re-splits the file instead of
storing offsets.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from librarian.config import get_settings

_FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*#*\s*$")
_FENCE_RE = re.compile(r"^[ \t]*(```|~~~)")
_DROPPED = {"see also"}
PATH_SEP = " › "

# Words too common to say which section of a page a query is about.
_STOPWORDS = frozenset(
    [
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "can",
        "do",
        "does",
        "for",
        "from",
        "how",
        "i",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "should",
        "the",
        "to",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "with",
        "you",
        "your",
    ]
)


@dataclass(frozen=True)
class Section:
    ordinal: int
    heading_path: str  # "H2 › H3"; "" for the text before the first heading below the title
    text: str  # the section's markdown, its heading line included


def strip_frontmatter(text: str) -> str:
    return _FRONTMATTER_RE.sub("", text, count=1).lstrip()


def _blocks(body: str) -> list[tuple[str, list[str], bool]]:
    """(heading path, lines, dropped) per heading-delimited block, in page order."""
    blocks: list[tuple[str, list[str], bool]] = []
    stack: dict[int, str] = {}
    path, lines, dropped = "", [], False
    fence: str | None = None
    for line in body.splitlines():
        fm = _FENCE_RE.match(line)
        if fm:
            marker = fm.group(1)
            fence = None if fence == marker else (fence or marker)
        hm = None if fence or fm else _HEADING_RE.match(line)
        if hm:
            blocks.append((path, lines, dropped))
            level, heading = len(hm.group(1)), hm.group(2)
            if level == 1:
                stack = {}  # the page title: what follows is the page's introduction
                path, lines, dropped = "", [], False
                continue
            stack = {k: v for k, v in stack.items() if k < level}
            stack[level] = heading
            path = PATH_SEP.join(stack[k] for k in sorted(stack))
            top = stack.get(2, "")
            dropped = top.strip().lower() in _DROPPED
            lines = [line]
            continue
        lines.append(line)
    blocks.append((path, lines, dropped))
    return blocks


def _split_long(text: str, max_chars: int) -> list[str]:
    """Cut `text` at blank lines outside fences into parts of at most `max_chars` where possible."""
    paras: list[str] = []
    current: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        fm = _FENCE_RE.match(line)
        if fm:
            marker = fm.group(1)
            fence = None if fence == marker else (fence or marker)
        if not line.strip() and fence is None:
            if current:
                paras.append("\n".join(current))
                current = []
            continue
        current.append(line)
    if current:
        paras.append("\n".join(current))
    paras = [piece for para in paras for piece in _split_table(para, max_chars)]

    parts: list[str] = []
    buf = ""
    for para in paras:
        lone_heading = buf and all(_HEADING_RE.match(ln) for ln in buf.splitlines())
        if buf and not lone_heading and len(buf) + 2 + len(para) > max_chars:
            parts.append(buf)
            buf = para
        else:
            buf = f"{buf}\n\n{para}" if buf else para
    if buf:
        parts.append(buf)
    return parts


def _split_table(para: str, max_chars: int) -> list[str]:
    """A markdown table longer than `max_chars` as row groups, each under the header rows.

    The course's references.md tables run to 190k characters in one paragraph. Anything that is
    not a table (a long code block) is returned whole.
    """
    lines = para.splitlines()
    is_table = len(lines) > 2 and all(ln.lstrip().startswith("|") for ln in lines)
    if len(para) <= max_chars or not is_table:
        return [para]
    header, rows = lines[:2], lines[2:]
    groups: list[str] = []
    buf: list[str] = []
    size = sum(len(h) + 1 for h in header)
    for row in rows:
        if buf and size + len(row) + 1 > max_chars:
            groups.append("\n".join(header + buf))
            buf, size = [], sum(len(h) + 1 for h in header)
        buf.append(row)
        size += len(row) + 1
    if buf:
        groups.append("\n".join(header + buf))
    return groups


def split_sections(
    body: str, *, min_chars: int | None = None, max_chars: int | None = None
) -> list[Section]:
    """A page body (frontmatter already stripped or not) as its sections, in page order."""
    settings = get_settings()
    min_chars = settings.section_min_chars if min_chars is None else min_chars
    max_chars = settings.section_max_chars if max_chars is None else max_chars

    kept = [
        (path, "\n".join(lines).strip())
        for path, lines, dropped in _blocks(strip_frontmatter(body))
        if not dropped
    ]
    kept = [(path, text) for path, text in kept if text]

    # Fold short blocks forward: a heading followed straight by a subheading carries no text
    # of its own, and a two-line section is too little to embed or to return on its own.
    # A merged section is named by the first heading in it, where its text starts.
    merged: list[tuple[str, str]] = []
    carry, carry_path = "", ""
    for path, text in kept:
        path = carry_path or path
        text = f"{carry}\n\n{text}" if carry else text
        if len(text) < min_chars:
            carry, carry_path = text, path
            continue
        merged.append((path, text))
        carry, carry_path = "", ""
    if carry:
        if merged:
            path, text = merged[-1]
            merged[-1] = (path, f"{text}\n\n{carry}")
        else:
            merged.append((carry_path, carry))

    out: list[Section] = []
    for path, text in merged:
        parts = _split_long(text, max_chars) if len(text) > max_chars else [text]
        for part in parts:
            out.append(Section(len(out), path, part))
    return out


def embed_text(title: str, section: Section) -> str:
    """The text a section is embedded as: page title and heading path in front (a chunk header)."""
    head = f"{title}{PATH_SEP}{section.heading_path}" if section.heading_path else title
    return f"{head}\n\n{section.text}"


def query_terms(query: str) -> list[str]:
    terms = [t.strip("?!.,:;\"'()`") for t in query.lower().split()]
    return [t for t in terms if len(t) > 2 and t not in _STOPWORDS]


def term_score(terms: list[str], text: str) -> float:
    """Share of the query's terms that appear in `text` (prefix match, so `chunk` finds `chunking`)."""
    if not terms:
        return 0.0
    lower = text.lower()
    return sum(1 for t in terms if t[:5] in lower) / len(terms)


def find_section(body: str, heading: str) -> Section | None:
    """The first section holding a heading named `heading` (case-insensitive), or None.

    `heading` is a heading's text or a full heading path. A short section folded into its
    neighbour is still found: the match is on every heading line in a section's text.
    """
    want = heading.strip().lower().split(PATH_SEP.strip())[-1].strip()
    for sec in split_sections(body):
        for line in sec.text.splitlines():
            hm = _HEADING_RE.match(line)
            if hm and hm.group(2).strip().lower() == want:
                return sec
    return None
