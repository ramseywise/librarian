# AGT-09: Spike — ADK vs LangGraph Evaluation

**Source:** Notion (work) — VA Team Task Tracker  
**Date:** 2026-04-21  
**URL:** https://www.notion.so/349f148b3ab780be8a5ee1facb507611  
**Status:** ✅ Q2 (complete)  
**Requirement:** R13  
**Topic:** Agent System  
**Priority:** MVP

---

## Task Description

Compare ADK and LangGraph for orchestration loop.

**Evaluation dimensions:**
- State management
- MCP support
- Observability out-of-the-box
- Prefix caching behavior
- Voice compatibility

**Conclusion stated in task:** Both are viable — decision needed.

**Note:** Page body is blank — this spike was tracked in Linear (see Linear ADK vs LangGraph evaluation) and the decision is documented in wiki/decisions/. The `adk-vs-langgraph-comparison.md` and `adk-vs-langgraph-decision.md` wiki pages represent the output of this spike.

---

## Context

This task is part of the VA (Virtual Assistant) Team's initial workstreams. Parent hierarchy:
- VA- Recap Tasks & Requirements
- Initial Workstreams for VA Team

The spike confirmed LangGraph for the Librarian RAG pipeline (deterministic orchestration, typed state, CRAG retry loops). ADK selected for the Shine Copilot outer coordination layer (managed sessions, Google Cloud integration, multi-modal support).
