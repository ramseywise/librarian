# Research: Research Agent Note Quality Refactor

**Date**: 2026-04-06
**Trigger**: Manual review of ch13 Knowledge Graphs note output
**Status**: Complete — informed plan

## Problem

The research agent's ch13 note was thorough but had structural and quality issues identified during manual review:

### What was well-covered
- Vector RAG failure modes (Lauritsen example, Table 13.1) — captured accurately
- Precanned vs. generated Cypher contradiction — correctly identified
- Lack of experimental validation — well-articulated

### What was missing or underdeveloped
1. **No deprecation flagging** — `create_structured_chat_agent + AgentExecutor` is deprecated in favor of LangGraph. Agent lacks training-knowledge awareness.
2. **No project context** — `StructuredTool.from_function` pattern matches tools.py; text-paired graphs → ChromaDB metadata filtering; `return_intermediate_steps=True` → tool_selection_eval.py. None connected.
3. **KG schema injection technique** (Listing 13.6 #4) — passing `KG_SCHEMA` into tool description. Actionable but not highlighted.
4. **Template forces redundancy** — 8-section academic structure produces ~60% overlap between Critical Assessment and Methodology/Weaknesses.
5. **No page references** — note not citable without re-reading PDF.
6. **[[wikilinks]] only in Connections** — should be throughout all sections for Obsidian graph view.

### Root causes in code
- `prompts.py` SYSTEM_PROMPT: no deprecation flagging rule, no project context parameter
- `prompts.py` _SECTION_INSTRUCTIONS: 8-section academic template (Core Claim, Research Questions, Methodology, Key Findings, Tradeoffs, Critical Assessment, Connections, Open Questions) optimized for completeness, not actionability
- `build_note_prompt()`: no `project_context` parameter
- `config.py`: no project context file path or loader

## Decision

Single consolidated note with 6 sections:
1. Summary (3-5 sentences, page refs, Relevance N/5)
2. Research Questions (page refs)
3. Methodology (flag weaknesses, page refs)
4. Key Techniques (actionable + failure modes subsection, page refs, [[wikilinks]])
5. Critical Assessment (strengths/weaknesses)
6. Open Questions

**Rejected alternatives**:
- Two-tier (practitioner + academic subnote): adds +1 API call per PDF, user decided consolidated single note covers both needs
- Standalone Connections section: [[wikilinks]] woven throughout all sections instead
- Standalone Quotes section: page refs inline throughout is sufficient
- "Relevance to Active Work" section: too fluid, project context still injected for general awareness
