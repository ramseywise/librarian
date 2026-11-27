"""Plain-text forms of the learning payloads (`librarian.courses.learning`), for LLM tool results.

Shared by the chat agent and the MCP tools, which both build from the one registry in
`librarian.agent.tools`, so both say the same thing within the same bounds. Standard library only.

Absent evidence is worded with care throughout: "no evidence" means nothing was recorded in the
app, never that the learner has not practised.
"""

from __future__ import annotations

from typing import Any

NEXT_DEFAULT_LIMIT = 5
NEXT_MAX_LIMIT = 10
MAX_SPOKES = 5  # lessons, drills and decks shown per concept

ESTIMATE_NOTE = (
    "Mastery figures are estimates from study events recorded in the app (lessons finished, "
    "flashcards, drills, spoken grades), not measurements. Study done elsewhere is invisible to them."
)
NO_EVIDENCE_NOTE = (
    "No study evidence recorded for this concept. That does not show it was never practised: "
    "only study recorded in the app counts here."
)
NOTHING_DUE = (
    "No concepts are due for review. This list only covers concepts with recorded study "
    "evidence, so it says nothing about concepts without any."
)
CATALOG_UNAVAILABLE = (
    "The course catalog is unavailable right now: its cache is still building, or there is no "
    "course checkout. This says nothing about which lessons exist or what was studied. Try again "
    "shortly, and do not report this as no lessons being available on a topic."
)
NO_USER = "Study progress is only available for a signed-in user; none is attached to this call."

_LINK_LABEL = {"explicit": "linked", "semantic": "similar text, weak"}


def clamp_limit(limit: object) -> int:
    """A usable row count from whatever the caller sent. Bad input gets the default."""
    try:
        value = int(limit)  # type: ignore[call-overload]
    except (TypeError, ValueError):
        return NEXT_DEFAULT_LIMIT
    return max(1, min(value, NEXT_MAX_LIMIT))


def lesson_line(row: dict[str, Any]) -> str:
    """One lesson or drill. Drill metadata is an allowlist: nothing else in a row is echoed."""
    drill = row.get("drill") or {}
    extras = [
        row.get("kind") or "reading",
        *(str(drill[k]) for k in ("difficulty", "track") if drill.get(k)),
        *([f"{drill['timebox_min']} min"] if drill.get("timebox_min") else []),
        *([_LINK_LABEL[row["link"]]] if row.get("link") in _LINK_LABEL else []),
    ]
    return f"- {row.get('title', '')} (lesson id: `{row['id']}`; {', '.join(extras)})"


def _capped(
    label: str, lines: list[str], limit: int = MAX_SPOKES, *, exact: bool = True
) -> list[str]:
    """`exact` off where the rows are already capped upstream, so their count is not the total."""
    if not lines:
        return []
    more = len(lines) - limit
    return [
        f"{label}:",
        *lines[:limit],
        *(
            [f"- ... and {more if exact else 'others'} {'more ' if exact else ''}not shown"]
            if more > 0
            else []
        ),
    ]


def format_next(rows: list[dict[str, Any]], *, more: bool = False) -> str:
    """The Due list. `more`: the caller knows further rows exist beyond these."""
    if not rows:
        return NOTHING_DUE
    parts = [f"Concepts due for review, weakest first. {ESTIMATE_NOTE}"]
    for row in rows:
        concept = row["concept"]
        lines = [
            f"## {concept['title']} (page id: `{concept['id']}`)",
            f"Estimated strength {row['strength']:.2f}. Why: {row['reason']}",
            *_capped("Lessons", [lesson_line(r) for r in row.get("lessons", [])], 3, exact=False),
            *_capped("Drills", [lesson_line(r) for r in row.get("drills", [])], 3, exact=False),
        ]
        parts.append("\n".join(lines))
    if more:
        parts.append(f"More concepts are due than the {len(rows)} shown; raise limit to see them.")
    return "\n\n".join(parts)


def format_concept(detail: dict[str, Any]) -> str:
    """One concept hub. `catalogReady` false means no lessons is "don't know", so say that."""
    lines = [
        f"# {detail['title']} (page id: `{detail['id']}`, domain: {detail.get('domain', '')})",
        str(detail.get("summary") or ""),
        "",
    ]
    mastery = detail.get("mastery")
    if mastery:
        current = mastery["strength"] * mastery["recency"]
        lines += [
            f"Estimated mastery: strength {mastery['strength']:.2f}, recency "
            f"{mastery['recency']:.2f}, current {current:.2f}; "
            f"{'due for review' if mastery['due'] else 'not due'}; last seen "
            f"{str(mastery['lastSeen'])[:10]}.",
            (
                "Evidence is direct."
                if mastery["evidence"] == "direct"
                else "Evidence is weak only (similar text): capped, never due."
            ),
            ESTIMATE_NOTE,
        ]
    else:
        lines.append(NO_EVIDENCE_NOTE)
    lines.append("")
    if not detail.get("catalogReady", True):
        lines.append(CATALOG_UNAVAILABLE)
        return "\n".join(lines).strip()
    lines += _capped("Lessons", [lesson_line(r) for r in detail.get("lessons", [])])
    lines += _capped("Drills", [lesson_line(r) for r in detail.get("drills", [])])
    lines += _capped(
        "Flashcard decks",
        [f"- {d['title']} (deck id: `{d['id']}`)" for d in detail.get("decks", [])],
    )
    if not any(detail.get(k) for k in ("lessons", "drills", "decks")):
        lines.append("No lessons, drills or decks link to this concept.")
    return "\n".join(lines).strip()


def format_no_page(page_id: str) -> str:
    """Private, retired and unknown ids read alike, so this cannot probe for private pages."""
    return f"No wiki page with id `{page_id}`. Use the id exactly as a search result shows it."
