from __future__ import annotations

import re
from pathlib import Path

import structlog

from etl.researcher.models import Note
from core.config.agent_settings import settings

log = structlog.get_logger(__name__)

OBSIDIAN_TOPICS = settings.obsidian_vault / "topics"
OBSIDIAN_INDEX = settings.obsidian_vault / "_index.md"

_FRONTMATTER_TEMPLATE = """\
---
title: {title}
source: {source}
topic: {topic}
tags: [{tags}]
date: {date}
relevance: {relevance}
source_file: {source_file}
pages: {pages}
---

"""


def sanitize_filename(title: str) -> str:
    """Convert a title to a safe lowercase kebab-case filename with .md extension."""
    name = title.lower()
    name = re.sub(r"[^a-z0-9\s-]", "", name)
    name = re.sub(r"\s+", "-", name.strip())
    name = re.sub(r"-+", "-", name)
    return name[:80].rstrip("-") + ".md"


def render_note(note: Note) -> str:
    """Render a Note to full Obsidian markdown with YAML frontmatter."""
    tags_str = ", ".join(note.metadata.tags)
    frontmatter = _FRONTMATTER_TEMPLATE.format(
        title=note.metadata.title,
        source=note.metadata.source,
        topic=note.metadata.topic,
        tags=tags_str,
        date=note.metadata.date,
        relevance=note.metadata.relevance,
        source_file=note.metadata.source_file,
        pages=note.metadata.pages,
    )
    return frontmatter + note.body


def write_note(note: Note, pdf_path: Path, topic_override: str | None = None) -> Path:
    """Write rendered note to the correct Obsidian topic folder and update _index.md.

    Returns the path of the written note file.
    """
    topic = topic_override or note.metadata.topic
    topic_dir = OBSIDIAN_TOPICS / topic
    topic_dir.mkdir(parents=True, exist_ok=True)

    filename = sanitize_filename(note.metadata.title)
    note_path = topic_dir / filename

    if note_path.exists():
        log.warning("writer.note_exists", path=str(note_path))
        raise FileExistsError(
            f"Note already exists: {note_path}. Delete it first or use --force."
        )

    content = render_note(note)
    note_path.write_text(content, encoding="utf-8")
    log.info("writer.note_written", path=str(note_path))

    _append_index(note, filename, topic)

    return note_path


def _append_index(note: Note, filename: str, topic: str) -> None:
    """Append one row to _index.md, creating it with a header if it doesn't exist."""
    note_link = f"[[{filename[:-3]}]]"  # strip .md for wikilink
    row = (
        f"| {note.metadata.date} "
        f"| {note_link} "
        f"| {note.metadata.relevance}/5 "
        f"| {topic} "
        f"| {note.metadata.source_file} |\n"
    )

    if not OBSIDIAN_INDEX.exists():
        header = (
            "# Research Index\n\n"
            "| Date | Note | Relevance | Topic | Source |\n"
            "|------|------|-----------|-------|--------|\n"
        )
        OBSIDIAN_INDEX.write_text(header, encoding="utf-8")
        log.info("writer.index_created", path=str(OBSIDIAN_INDEX))

    with OBSIDIAN_INDEX.open("a", encoding="utf-8") as f:
        f.write(row)

    log.info("writer.index_updated", note=filename)
