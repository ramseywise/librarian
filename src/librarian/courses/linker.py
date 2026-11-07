"""Tying lessons to wiki pages: explicit links, compiled-from sources, title mentions and the semantic merge, plus the `[[wikilink]]` rewrite for a lesson body."""

from __future__ import annotations

import re
from typing import Any

import frontmatter

from librarian.courses.loader import DRILL_KEYS, Catalog, WikiRef, _wiki_slugs
from librarian.wiki.common import WIKILINK_RE, LinkIndex, fm, resolve_link, slugify

MAX_CONCEPTS = 12
# Semantic linking (D5). 0.55 kept after a spot check on the real courses (2026-10-30):
# pairs >= ~0.62 are reliably on-topic, 0.55-0.62 are mostly same-area neighbours, and
# below 0.5 MiniLM pairs lessons with pages that only share vocabulary. Raising to 0.58
# or 0.60 cut lesson coverage from 324 to 284 / 267 of 762 without removing a clear
# class of bad links.
SEMANTIC_THRESHOLD = 0.55
SEMANTIC_TOP_K = 6
LESSON_PROSE_CHARS = 1500
_FENCE_RE = re.compile(r"^\s*(```|~~~)")


# (lesson texts, eligible wiki ids) → per text, (wiki id, cosine) candidates best first,
# or None when embeddings are unavailable. Module-level so tests can swap in a fake.
Neighbours = list[list[tuple[str, float]]]


def _prose(body: str) -> str:
    """Body with fenced code removed — concept mentions inside code are noise."""
    out, in_fence = [], False
    for line in body.split("\n"):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def _concept_matcher(wiki: dict[str, WikiRef]) -> tuple[re.Pattern[str] | None, dict[str, str]]:
    by_title: dict[str, str] = {}
    for ref in wiki.values():
        t = ref.title.strip().lower()
        if len(t.split()) >= 2 and len(t) <= 60:
            by_title.setdefault(t, ref.id)
    if not by_title:
        return None, by_title
    alts = sorted(by_title, key=len, reverse=True)
    pattern = re.compile(
        r"(?<![\w-])(" + "|".join(re.escape(t) for t in alts) + r")(?![\w-])", re.I
    )
    return pattern, by_title


def _resolve_wikilink(target: str, wiki: dict[str, WikiRef], slugs: LinkIndex) -> str | None:
    return resolve_link(target, slugs)


def _drill_meta(
    post: frontmatter.Post, wiki: dict[str, WikiRef], slugs: LinkIndex, hidden: set[str]
) -> dict[str, Any]:
    """DRILL_KEYS, plus `tags`: declared concepts with no wiki page yet (shown as plain labels)."""
    meta = {k: post[k] for k in DRILL_KEYS if fm(post).get(k) is not None}
    tags = [
        str(x)
        for x in (fm(post).get("wiki") or [])
        if not _resolve_wikilink(str(x), wiki, slugs) and slugify(str(x)) not in hidden
    ]
    return meta | ({"tags": tags} if tags else {})


def _rank_concepts(
    post: frontmatter.Post,
    wiki: dict[str, WikiRef],
    slugs: LinkIndex,
    matcher: re.Pattern[str] | None,
    by_title: dict[str, str],
    compiled: list[str],
) -> list[str]:
    explicit = [str(x) for x in (fm(post).get("wiki") or [])]
    explicit += [m.group(1) for m in WIKILINK_RE.finditer(post.content)]
    ranked: list[str] = []
    for target in explicit:
        pid = _resolve_wikilink(target, wiki, slugs)
        if pid and pid not in ranked:
            ranked.append(pid)
    ranked += [pid for pid in compiled if pid not in ranked]
    if matcher:
        counts: dict[str, int] = {}
        text = f"{fm(post).get('title') or ''}\n{_prose(post.content)}"
        for m in matcher.finditer(text):
            pid = by_title[m.group(1).lower()]
            counts[pid] = counts.get(pid, 0) + 1
        for pid, _ in sorted(counts.items(), key=lambda kv: -kv[1]):
            if pid not in ranked:
                ranked.append(pid)
    return ranked[:MAX_CONCEPTS]


def _lesson_text(post: frontmatter.Post, stem: str) -> str:
    title = str(fm(post).get("title") or stem)
    summary = str(fm(post).get("summary") or "")
    return f"{title}. {summary}\n\n{_prose(post.content)[:LESSON_PROSE_CHARS]}"


def _merge_semantic(
    ranked: list[str], candidates: list[tuple[str, float]], wiki: set[str]
) -> list[str]:
    """Append up to SEMANTIC_TOP_K new candidates ≥ SEMANTIC_THRESHOLD after `ranked`.

    Explicit and title-mention links keep their places; `wiki` is the visible page set,
    so a private or tombstoned id can never get in even if the embedder returns one.
    """
    out = list(ranked)
    added = 0
    for pid, score in sorted(candidates, key=lambda c: -c[1]):
        if added >= SEMANTIC_TOP_K or len(out) >= MAX_CONCEPTS or score < SEMANTIC_THRESHOLD:
            break
        if pid in wiki and pid not in out:
            out.append(pid)
            added += 1
    return out


def _link_wikilinks(body: str, cat: Catalog) -> str:
    """[[Title|alias]] → [alias](#wiki:<id>) outside code; unresolved → plain text."""
    slugs = _wiki_slugs(cat.wiki)
    out, in_fence = [], False
    for line in body.split("\n"):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
        elif not in_fence and "[[" in line:

            def sub(m: re.Match[str]) -> str:
                inner = m.group(0)[2:-2]
                target, _, alias = inner.partition("|")
                label = alias or target.split("#")[0]
                pid = _resolve_wikilink(target.split("#")[0], cat.wiki, slugs)
                return f"[{label}](#wiki:{pid})" if pid else label

            line = re.sub(r"\[\[[^\]]+\]\]", sub, line)
        out.append(line)
    return "\n".join(out)
