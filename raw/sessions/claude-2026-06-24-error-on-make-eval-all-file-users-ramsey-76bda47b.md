---
tags: [adk, context-management, eval, langgraph]
tool: claude-code
project: project-g
date: 2026-06-24
session_id: 76bda47b-2f85-4a70-ac57-ccb454371f43
prompts: 2
total_tokens: 10004
cache_read_tokens: 722564
---

# Claude Code Session — 2026-06-24 (project-g)

**First prompt:** error on make eval-all
  File "/Users/ramsey.wise/Workspace/project-g/src/support_agents/hc_rag/rag/sentence_transformers.py", line 74, in _encode_model
    return load_sentence_transformer(self._model_name, self._revision)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  Fil

## Prompts (2 total)

- error on make eval-all
  File "/Users/ramsey.wise/Workspace/project-g/src/support_agents/hc_rag/rag/sentence_transformers.py", line 74, in _encode_model
    return load_sentence_transformer(self._mode
- Makefile
	$(SA_PYTHON) $(_SA_RAG_MODE) LANGSMITH_TRACING=false $(_MQ) $(_THINKING) \
	  uv run --extra agents uvicorn hc_adk.main:app --port 8011 &
	$(SA_PYTHON) $(_SA_RAG_MODE) LANGSMITH_TRACING=fals

## Stats

| Metric | Value |
|---|---|
| Input tokens | 40 |
| Output tokens | 9,964 |
| Cache read | 722,564 |
| Cache write | 74,251 |
