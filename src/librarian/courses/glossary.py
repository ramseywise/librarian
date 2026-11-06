"""Glossary terms as a graph layer: `data/glossary.yaml` plus where each term is mentioned.

Terms are hand-curated; mentions are word-boundary matches of a term's label and aliases in
public page bodies, computed once per wiki state because they read every page. A term with no
public mention is not served, so a term only private pages use can't surface in the map.
"""

from __future__ import annotations

import re
from typing import Annotated, Any

import frontmatter
import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from librarian.config import get_settings
from librarian.log_config import get_logger
from librarian.wiki import parser as wiki_parser

log = get_logger(__name__)

GLOSSARY_FILE = get_settings().glossary_file
# Two capitals (RAG, BM25, A/B test) mean the case carries the meaning: "rag" is not "RAG".
EXACT_CASE_CAPITALS = 2


class GlossaryTerm(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    aliases: list[Annotated[str, Field(min_length=1)]] = Field(default_factory=list)
    definition: str = Field(alias="def", min_length=1)
    page: str | None = None

    def forms(self) -> list[str]:
        return [self.label, *self.aliases]


def load_terms() -> list[GlossaryTerm]:
    """Terms from the YAML file. A bad file is logged and reads as empty: the layer is optional,
    and the map must not fail over it."""
    try:
        raw = yaml.safe_load(GLOSSARY_FILE.read_text())
        return [GlossaryTerm.model_validate(item) for item in raw or []]
    except FileNotFoundError:
        return []
    except (OSError, yaml.YAMLError, ValidationError, TypeError) as e:
        log.error("glossary.unreadable", error=str(e).splitlines()[0])
        return []


def _pattern(forms: list[str]) -> re.Pattern[str]:
    """Any form, on word boundaries. `\\b` would fail beside a non-word end such as `Bayes'`."""

    def one(form: str) -> str:
        body = re.escape(form)
        if sum(c.isupper() for c in form) < EXACT_CASE_CAPITALS:
            body = f"(?i:{body})"
        return rf"(?<!\w){body}(?!\w)"

    return re.compile("|".join(one(f) for f in sorted(forms, key=len, reverse=True)))


def _compute(terms: list[GlossaryTerm]) -> dict[str, list[str]]:
    """Term id → public pages that mention it, sorted. Starts from parse_wiki's nodes, which
    leave out private and tombstoned pages, so neither can contribute a mention."""
    bodies: dict[str, str] = {}
    for node in wiki_parser.parse_wiki()["nodes"]:
        path = wiki_parser.WIKI_DIR / node["data"]["path"]
        bodies[node["id"]] = frontmatter.loads(path.read_text()).content
    lowered = {pid: body.lower() for pid, body in bodies.items()}

    mentions: dict[str, list[str]] = {}
    for term in terms:
        pattern = _pattern(term.forms())
        # A plain substring test first: the regex alone took 16 s over the real wiki.
        needles = [f.lower() for f in term.forms()]
        hits = {
            pid
            for pid, body in bodies.items()
            if any(n in lowered[pid] for n in needles) and pattern.search(body)
        }
        if term.page in bodies:  # its own page explains it, whatever words that page uses
            hits.add(term.page)
        if hits:
            mentions[term.id] = sorted(hits)
    return mentions


# Last result and the signature it was built from, like wiki_parser._parsed. Each glossary
# request stats every page, which is cheap next to reading them all.
_cached: tuple[tuple, list[GlossaryTerm], dict[str, list[str]]] | None = None


def _signature() -> tuple:
    pages = tuple((str(f), *wiki_parser._stat_key(f)) for f in wiki_parser._public_pages())
    try:
        return (pages, *wiki_parser._stat_key(GLOSSARY_FILE))
    except FileNotFoundError:
        return (pages,)


def _state() -> tuple[list[GlossaryTerm], dict[str, list[str]]]:
    global _cached
    signature = _signature()
    if _cached is None or _cached[0] != signature:
        terms = load_terms()
        _cached = (signature, terms, _compute(terms))
    return _cached[1], _cached[2]


def term_mentions() -> dict[str, list[str]]:
    return _state()[1]


def public_terms() -> list[dict[str, Any]]:
    """Terms with at least one public mention; `page` only when it is a live public page."""
    terms, mentions = _state()
    public = wiki_parser.public_page_ids()
    return [
        {
            "id": t.id,
            "label": t.label,
            "aliases": t.aliases,
            "def": t.definition,
            "page": t.page if t.page in public else None,
            "mentions": len(mentions[t.id]),
        }
        for t in terms
        if t.id in mentions
    ]
