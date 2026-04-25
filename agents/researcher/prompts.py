from __future__ import annotations

SYSTEM_PROMPT = """\
You are a research assistant building a personal AI engineering knowledge base in Obsidian.
Your notes are used for: (1) project planning reference, (2) cross-document relationship mapping,
(3) future RAG retrieval.

Active domains (use these to judge relevance):
- RAG systems and retrieval architecture
- LangGraph / multi-agent orchestration
- Prompt engineering and instruction tuning
- Knowledge graphs and graph-based retrieval

Rules:
- Use [[wikilinks]] liberally throughout ALL sections for any concept, paper, tool, or \
technique that deserves its own note (e.g. [[RAG]], [[LangGraph]], [[knowledge graph]], \
[[HNSW]], [[chain-of-thought]]). These drive Obsidian's graph view — the more \
cross-linked, the more useful the vault becomes.
- Add #tags inline for key terms to drive Obsidian tag search and sparse retrieval \
(e.g. #rag #knowledge-graph #langgraph #chunking #embeddings)
- Include page references on specific claims, techniques, and findings throughout: (p. N) or (p. N–M)
- Be critical: note what the work does NOT solve and where claims are weak or unsupported
- Rate relevance 1–5 against active domains (5 = directly applicable to current projects)
- For book chapters: note what this chapter adds beyond prior chapters (referenced in prior_summary)
- For multi-chunk documents: connections and open questions should build on prior chunks
- Flag when source code examples use deprecated APIs, superseded patterns, or outdated libraries. \
Note the current replacement based on your training knowledge. Mark these clearly with ⚠️ DEPRECATED.
- When project context is provided, connect findings to specific files, patterns, and techniques \
in active projects. Be concrete — name the file or pattern, not just the concept.
- Output ONLY the markdown body — no preamble, no "Here is your note:" framing
"""

# ---------------------------------------------------------------------------
# Chunk-level instructions (used for per-chunk analysis before merging)
# ---------------------------------------------------------------------------

_CHUNK_INSTRUCTIONS = """\
Analyse the text above. Produce notes covering ALL of the following. \
Use this structure exactly — do not rename or skip sections. \
Use [[wikilinks]] throughout every section, not just selectively. \
Include page references (p. N) on specific claims and techniques.

## Summary
2–3 sentences stating the central argument or contribution of this chunk. \
Note how it connects to ([[wikilinks]]) and extends prior work.

## Research Questions
For papers: explicit research questions or hypotheses. \
For book chapters / courses: stated learning goals or questions addressed.

## Methodology
How was the work done? (experimental setup, algorithm design, dataset, system architecture, etc.) \
Flag if methodology is weak or underspecified. Use [[wikilinks]] for tools, frameworks, datasets.

## Key Techniques
Bullet list of concrete, actionable techniques, patterns, and tools. \
Use [[wikilinks]] for key concepts. Include code patterns, algorithm designs, \
and architectural decisions — not just abstract ideas. \
Note how each technique relates to (extends, contradicts, enables) other concepts.

Also include a **What NOT to do** sub-section: failure modes, deprecated patterns \
(mark ⚠️ DEPRECATED), known limitations, and specific failure examples from the source.

## Critical Assessment
Where are the claims strongest? Where weakest or oversold? \
Flag contradictions with prior work explicitly using [[wikilinks]]. \
Rate relevance: **Relevance: N/5** (final line, N = 1–5).

## Open Questions
Questions this work raises but does not answer. What would you investigate next?
"""

# ---------------------------------------------------------------------------
# Merge instructions — single consolidated note
# ---------------------------------------------------------------------------

_MERGE_INSTRUCTIONS = """\
Merge the chunk notes below into a single, cohesive note. \
Remove redundancy but preserve all [[wikilinks]], #tags, and page references. \
The result should be a practitioner working note — scannable but thorough enough to cite.

Use this structure exactly — do not rename or skip sections. \
Use [[wikilinks]] throughout EVERY section to drive Obsidian graph view. \
Note how concepts relate to each other (extends, contradicts, enables, alternative-to) \
inline where they appear, not in a separate connections section. \
Include page references (p. N) on specific claims and techniques throughout.

## Summary
3–5 sentences: central argument, what it adds to the field, and key takeaway. \
Use [[wikilinks]] for key concepts and note relationships to prior work inline. \
Rate relevance: **Relevance: N/5** (final line, N = 1–5, averaged from chunks).

## Research Questions
Consolidated list from all chunks. Deduplicate. Use [[wikilinks]] for key concepts. \
Include page references.

## Methodology
How the work was done: architecture, dataset, tools, validation approach. \
Flag weaknesses. Use [[wikilinks]] for tools, frameworks, and datasets. \
Note how the methodology extends or contradicts other approaches.

## Key Techniques
Bulleted list of actionable techniques, patterns, and tools. Use [[wikilinks]]. \
Focus on what a practitioner can USE: code patterns, implementation details, \
architectural decisions. Note how each relates to other concepts inline. \
Include page references for each technique.

Include a **What NOT to do** sub-section: failure modes, deprecated patterns \
(mark ⚠️ DEPRECATED with current replacement), known limitations, and specific \
failure examples from the source with page refs.

## Critical Assessment
Strengths and weaknesses. Where are claims strongest? Where oversold? \
Flag contradictions with prior work using [[wikilinks]]. \
Note deprecated or superseded approaches.

## Open Questions
Consolidated from chunks. Deduplicate. Frame as next investigations — \
what would you test, measure, or build?
"""


def build_note_prompt(
    chunk_text: str,
    source_title: str,
    doc_type: str,
    prior_summary: str = "",
    existing_vault_topics: list[str] | None = None,
    project_context: str = "",
) -> str:
    """Build the user-turn prompt for a single chunk.

    Args:
        chunk_text: Extracted text from this PDF chunk.
        source_title: Human-readable title of the source (filename or chapter title).
        doc_type: One of "paper", "book-chapter", "course", "article".
        prior_summary: Accumulated summary text from previous chunks (empty for first chunk).
        existing_vault_topics: List of topic slugs already in the vault, for grounding connections.
        project_context: Active project brief for connecting findings to real work.
    """
    parts: list[str] = []

    parts.append(f"**Source**: {source_title}")
    parts.append(f"**Type**: {doc_type}")

    if existing_vault_topics:
        topics_str = ", ".join(existing_vault_topics)
        parts.append(
            f"**Existing vault topics** (ground [[wikilinks]] here where relevant): {topics_str}"
        )

    if project_context:
        parts.append(
            f"**Project context** (connect findings to this active work):\n{project_context}"
        )

    if prior_summary:
        parts.append(
            f"**Prior chunks summary** (build on this — do not repeat, do reference it for connections and contradictions):\n{prior_summary}"
        )

    parts.append("\n**Text to analyse**:\n")
    parts.append(chunk_text)
    parts.append("\n---")
    parts.append(_CHUNK_INSTRUCTIONS)

    return "\n\n".join(parts)


def build_merge_prompt(
    chunk_notes: list[str],
    source_title: str,
    doc_type: str,
    project_context: str = "",
) -> str:
    """Merge chunk notes into a single consolidated note."""
    joined = "\n\n---CHUNK BOUNDARY---\n\n".join(chunk_notes)

    parts: list[str] = [
        f"**Source**: {source_title}",
        f"**Type**: {doc_type}",
    ]

    if project_context:
        parts.append(
            f"**Project context** (use for connecting findings to active work):\n{project_context}"
        )

    parts.append(
        "The following are draft notes from sequential chunks of the same document.\n"
    )
    parts.append(joined)
    parts.append("\n---")
    parts.append(_MERGE_INSTRUCTIONS)

    return "\n\n".join(parts)
