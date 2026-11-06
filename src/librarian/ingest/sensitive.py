"""Finds text that must not reach the public wiki. Reports categories and lines, never values.

A pattern scan: it catches secrets, contact details and names on the terms list. It can't
recognise client context nobody listed, so a clean scan is not a judgement that a source is
safe to publish. That judgement stays with the ingest step reading the source.

Terms live in data/wiki/private/_sensitive-terms.txt, one per line, # for comments. The file
is gitignored with the rest of private/, since a public list of names would be its own leak.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import frontmatter
import yaml

TERMS_FILE = "_sensitive-terms.txt"

SECRET_RE = re.compile(
    r"\b(?:sk-(?:ant-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|xox[bpas]-[A-Za-z0-9-]{20,}"
    r"|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,}|ntn_[A-Za-z0-9]{30,}|lin_api_[A-Za-z0-9]{30,})"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
)
EMAIL_RE = re.compile(r"[\w.+-]+@([\w-]+(?:\.[A-Za-z]{2,})+)")
PHONE_RE = re.compile(r"(?<![\w.-])\+\d[\d ().-]{8,}\d(?![\w-])")
IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b")
# Documentation placeholders and service identities, not anybody's contact details.
HARMLESS_EMAIL_DOMAINS = ("example.com", "example.org", "company.com", "gserviceaccount.com")
HARMLESS_EMAIL_LOCALPARTS = ("noreply@", "no-reply@")
_FM_TITLE_RE = re.compile(r"^title:[ \t]*(.+)$", re.MULTILINE)


@dataclass(frozen=True)
class Finding:
    line: int
    category: str  # secret | email | phone | iban | term | private-name


def _valid_iban(candidate: str) -> bool:
    rotated = candidate[4:] + candidate[:4]
    return int("".join(str(int(c, 36)) for c in rotated)) % 97 == 1


def _harmless_email(match: re.Match[str]) -> bool:
    address = match.group(0).lower()
    domain = match.group(1).lower()
    return address.startswith(HARMLESS_EMAIL_LOCALPARTS) or any(
        domain == d or domain.endswith(f".{d}") for d in HARMLESS_EMAIL_DOMAINS
    )


def scan_line(number: int, line: str, names: re.Pattern[str] | None = None) -> list[Finding]:
    found: list[Finding] = []
    if SECRET_RE.search(line):
        found.append(Finding(number, "secret"))
    if any(not _harmless_email(m) for m in EMAIL_RE.finditer(line)):
        found.append(Finding(number, "email"))
    if PHONE_RE.search(line):
        found.append(Finding(number, "phone"))
    if any(_valid_iban(m.group(0)) for m in IBAN_RE.finditer(line)):
        found.append(Finding(number, "iban"))
    if names and names.search(line):
        found.append(Finding(number, "term"))
    return found


def scan_text(text: str, names: re.Pattern[str] | None = None) -> list[Finding]:
    return [
        finding
        for number, line in enumerate(text.splitlines(), start=1)
        for finding in scan_line(number, line, names)
    ]


def load_terms(wiki_dir: Path) -> list[str]:
    path = wiki_dir / "private" / TERMS_FILE
    if not path.is_file():
        return []
    lines = (line.strip() for line in path.read_text().splitlines())
    return [line for line in lines if line and not line.startswith("#")]


def terms_pattern(terms: Iterable[str]) -> re.Pattern[str] | None:
    ordered = sorted(set(terms), key=len, reverse=True)
    if not ordered:
        return None
    alternatives = "|".join(re.escape(t) for t in ordered)
    # Only letters and digits bound a term: "acme-led" and "acme_prod" still name it.
    return re.compile(rf"(?<![^\W_])(?:{alternatives})(?![^\W_])", re.IGNORECASE)


def _page_title(page: Path) -> object:
    text = page.read_text(errors="replace")
    try:
        return frontmatter.loads(text).get("title")
    except (yaml.YAMLError, ValueError):
        # Broken frontmatter must not end the leak check, and the title still counts.
        match = _FM_TITLE_RE.search(text)
        return match.group(1).strip().strip("\"'") if match else None


def private_names(wiki_dir: Path) -> set[str]:
    """Private file stems and titles. Stems match inside longer strings, such as raw paths."""
    root = wiki_dir / "private"
    names: set[str] = set()
    # Globbed from its own root: in a worktree private/ is a symlink rglob wouldn't enter.
    for page in sorted(root.rglob("*.md")) if root.is_dir() else []:
        if page.name.startswith("_"):
            continue
        names.add(page.stem)
        title = _page_title(page)
        if isinstance(title, str) and len(title.split()) >= 3:
            names.add(title)
    return names


def embedded_names_pattern(names: Iterable[str]) -> re.Pattern[str] | None:
    """No word boundaries: a private stem inside a file path names the page just the same."""
    ordered = sorted(set(names), key=len, reverse=True)
    if not ordered:
        return None
    return re.compile("|".join(re.escape(n) for n in ordered), re.IGNORECASE)
