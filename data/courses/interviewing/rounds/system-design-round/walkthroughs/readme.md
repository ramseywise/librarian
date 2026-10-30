---
imported_hash: 20affa5d1f37658a
title: System-design walkthroughs
summary: Phase-by-phase AI system-design problems.
order: 90
kind: reading
section: System design round / Walkthroughs
source: sisyphus/interviewing/rounds/system-design-round/walkthroughs/README.md
---

# System-design walkthroughs

Phase-by-phase AI system-design problems. Each step gives the prompt the interviewer asks;
answer it out loud (or on the Excalidraw board) before opening the reference.

Source: [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/ai-system-design/`, converted 2026-10-29.

| Walkthrough | Skill | Difficulty |
|---|---|---|
| [Design a multi-step agentic workflow (e.g. meeting scheduling, code review, or an email campaign).](agentic-workflow.md) | agentic | hard |
| [Design an AI chatbot like ChatGPT (a conversational LLM service at scale).](chatgpt-chatbot.md) | chatbot | hard |
| [Design an AI coding copilot (inline code completion like GitHub Copilot).](coding-copilot.md) | serving | hard |
| [Design a content / policy-violation moderation system.](content-moderation.md) | serving | medium |
| [Your LLM app gets 1M queries/day. How do you optimize cost (without wrecking quality)?](cost-optimization-1m.md) | scaling | medium |
| [Design a large-scale document-processing pipeline (e.g. extract structured data from payslips, IDs, and references).](document-processing.md) | scaling | hard |
| [Design a fraud-detection system (real-time transaction scoring, with a role for GenAI).](fraud-detection.md) | serving | hard |
| [Design a real-time LLM-powered search engine (like Perplexity.ai).](perplexity-search.md) | rag | hard |
| [Design a Document Q&A / RAG system for 10M+ articles.](rag-10m.md) | ai-system-design | hard |

Blank phase skeleton: [`template.md`](template.md).
