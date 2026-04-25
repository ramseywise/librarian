from __future__ import annotations

import os
from pathlib import Path

import structlog
from dotenv import load_dotenv

from etl.researcher.chunker import plan_chunks
from etl.researcher.extractor import extract_pages, get_page_count
from etl.researcher.models import Note, NoteMetadata, resolve_topic
from etl.researcher.prompts import (
    SYSTEM_PROMPT,
    build_merge_prompt,
    build_note_prompt,
)
from core.client import create_client
from core.config.agent_settings import load_project_context, settings

load_dotenv()

log = structlog.get_logger(__name__)


def _source_type(pdf_path: Path) -> str:
    """Heuristically determine doc type from path components."""
    parts_lower = [p.lower() for p in pdf_path.parts]
    if any("course" in p or "lecture" in p for p in parts_lower):
        return "course"
    if any(p.startswith(("0.", "1.", "2.", "3.")) for p in pdf_path.parts):
        return "book-chapter"
    return "paper"


def _relative_source(pdf_path: Path) -> str:
    try:
        return str(pdf_path.relative_to(settings.readings_dir))
    except ValueError:
        return pdf_path.name


def _vault_topics() -> list[str]:
    obsidian_topics = settings.obsidian_vault / "topics"
    if obsidian_topics.exists():
        return [d.name for d in obsidian_topics.iterdir() if d.is_dir()]
    return []


class ResearchAgent:
    def __init__(self, max_tokens: int = 4096) -> None:
        self.client = create_client()
        self.model = os.environ.get("ANTHROPIC_MODEL", settings.anthropic_model)
        self.max_tokens = int(os.environ.get("RESEARCH_MAX_TOKENS", str(max_tokens)))
        self.project_context = load_project_context()
        log.info(
            "agent.init",
            model=self.model,
            max_tokens=self.max_tokens,
            has_project_context=bool(self.project_context),
        )

    def _call_claude(self, user_prompt: str) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text  # type: ignore[index]

    def process_pdf(self, pdf_path: Path, topic_override: str | None = None) -> Note:
        """Process a PDF into a consolidated research note.

        Returns a single Note with practitioner-oriented structure,
        page references, and [[wikilinks]] throughout.
        """
        log.info("agent.process_pdf.start", path=str(pdf_path))

        page_count = get_page_count(pdf_path)
        log.info("agent.process_pdf.pages", count=page_count)

        chunks = plan_chunks(pdf_path, page_count)
        log.info("agent.process_pdf.chunks", n=len(chunks))

        topic = topic_override or resolve_topic(pdf_path)
        doc_type = _source_type(pdf_path)
        source_title = pdf_path.stem
        vault_topics = _vault_topics()

        # --- Phase 1: Chunk-level analysis ---
        chunk_notes: list[str] = []
        prior_summary: str = ""

        for i, chunk in enumerate(chunks):
            log.info(
                "agent.chunk.start",
                chunk=i + 1,
                total=len(chunks),
                pages=f"{chunk.start_page}-{chunk.end_page}",
                title=chunk.title,
            )
            chunk_text = extract_pages(pdf_path, chunk.start_page, chunk.end_page)
            prompt = build_note_prompt(
                chunk_text=chunk_text,
                source_title=f"{source_title} — {chunk.title}",
                doc_type=doc_type,
                prior_summary=prior_summary,
                existing_vault_topics=vault_topics,
                project_context=self.project_context,
            )
            note_body = self._call_claude(prompt)
            chunk_notes.append(note_body)
            prior_summary = note_body
            log.info("agent.chunk.done", chunk=i + 1)

        # --- Phase 2: Merge into consolidated note ---
        if len(chunk_notes) == 1:
            log.info("agent.merge.single_chunk")
            final_body = self._call_claude(
                build_merge_prompt(
                    chunk_notes,
                    source_title,
                    doc_type,
                    self.project_context,
                )
            )
        else:
            log.info("agent.merge.start", n_chunks=len(chunk_notes))
            final_body = self._call_claude(
                build_merge_prompt(
                    chunk_notes,
                    source_title,
                    doc_type,
                    self.project_context,
                )
            )
            log.info("agent.merge.done")

        # --- Phase 3: Build metadata ---
        relevance = _extract_relevance(final_body)
        tags = _extract_tags(final_body)

        metadata = NoteMetadata(
            title=source_title,
            source=doc_type,
            topic=topic,
            tags=tags,
            date=_today(),
            relevance=relevance,
            source_file=_relative_source(pdf_path),
            pages=f"1-{page_count}",
        )

        log.info("agent.process_pdf.done", topic=topic, relevance=relevance)
        return Note(metadata=metadata, body=final_body)


def _extract_relevance(body: str) -> int:
    """Parse 'Relevance: N/5' from Claude output; default to 3 if not found."""
    import re

    match = re.search(r"Relevance:\s*(\d)/5", body)
    if match:
        val = int(match.group(1))
        return max(1, min(5, val))
    return 3


def _extract_tags(body: str) -> list[str]:
    """Extract #tags from the note body (deduped, lowercased, no leading #)."""
    import re

    raw = re.findall(r"#([a-zA-Z][a-zA-Z0-9_-]*)", body)
    seen: dict[str, None] = {}
    for tag in raw:
        seen[tag.lower()] = None
    return list(seen)


def _today() -> str:
    from datetime import date

    return date.today().isoformat()
