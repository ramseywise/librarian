from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path

import structlog
from dotenv import load_dotenv
from google import genai
from google.genai import types

from etl.researcher._settings import load_project_context, settings
from etl.researcher.chunker import plan_chunks
from etl.researcher.extractor import extract_pages, get_page_count
from etl.researcher.models import Note, NoteMetadata, resolve_topic
from etl.researcher.prompts import (
    SYSTEM_PROMPT,
    build_merge_prompt,
    build_note_prompt,
)

load_dotenv()

log = structlog.get_logger(__name__)


class ResearchAgent:
    def __init__(self, max_tokens: int = 4096) -> None:
        self._client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
        self._model = os.environ.get("GEMINI_MODEL", settings.gemini_model)
        self.max_tokens = int(os.environ.get("RESEARCH_MAX_TOKENS", str(max_tokens)))
        self.project_context = load_project_context()
        log.info(
            "agent.init",
            model=self._model,
            max_tokens=self.max_tokens,
            has_project_context=bool(self.project_context),
        )

    def _call_gemini(self, user_prompt: str) -> str:
        response = self._client.models.generate_content(
            model=self._model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=self.max_tokens,
            ),
        )
        return response.text or ""

    def process_pdf(self, pdf_path: Path, topic_override: str | None = None) -> Note:
        """Process a PDF into a consolidated research note."""
        log.info("agent.process_pdf.start", path=str(pdf_path))

        page_count = get_page_count(pdf_path)
        log.info("agent.process_pdf.pages", count=page_count)

        chunks = plan_chunks(pdf_path, page_count)
        log.info("agent.process_pdf.chunks", n=len(chunks))

        topic = topic_override or resolve_topic(pdf_path)
        doc_type = _source_type(pdf_path)
        source_title = pdf_path.stem
        vault_topics = _vault_topics()

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
            note_body = self._call_gemini(prompt)
            chunk_notes.append(note_body)
            prior_summary = note_body
            log.info("agent.chunk.done", chunk=i + 1)

        log.info("agent.merge.start", n_chunks=len(chunk_notes))
        final_body = self._call_gemini(
            build_merge_prompt(chunk_notes, source_title, doc_type, self.project_context)
        )
        log.info("agent.merge.done")

        metadata = NoteMetadata(
            title=source_title,
            source=doc_type,
            topic=topic,
            tags=_extract_tags(final_body),
            date=date.today().isoformat(),
            relevance=_extract_relevance(final_body),
            source_file=_relative_source(pdf_path),
            pages=f"1-{page_count}",
        )

        log.info("agent.process_pdf.done", topic=topic, relevance=metadata.relevance)
        return Note(metadata=metadata, body=final_body)


def _source_type(pdf_path: Path) -> str:
    parts_lower = [p.lower() for p in pdf_path.parts]
    if any("course" in p or "lecture" in p for p in parts_lower):
        return "course"
    if any(p.startswith(("0.", "1.", "2.", "3.")) for p in pdf_path.parts):
        return "book-chapter"
    return "paper"


def _relative_source(pdf_path: Path) -> str:
    try:
        return str(pdf_path.relative_to(settings.dropbox_pdf_path))
    except ValueError:
        return pdf_path.name


def _vault_topics() -> list[str]:
    obsidian_topics = settings.obsidian_vault / "topics"
    if obsidian_topics.exists():
        return [d.name for d in obsidian_topics.iterdir() if d.is_dir()]
    return []


def _extract_relevance(body: str) -> int:
    match = re.search(r"Relevance:\s*(\d)/5", body)
    if match:
        return max(1, min(5, int(match.group(1))))
    return 3


def _extract_tags(body: str) -> list[str]:
    raw = re.findall(r"#([a-zA-Z][a-zA-Z0-9_-]*)", body)
    seen: dict[str, None] = {}
    for tag in raw:
        seen[tag.lower()] = None
    return list(seen)
