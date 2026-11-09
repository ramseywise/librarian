---
title: Code, Workflow, RAG or Agent Decision Guide
tags: [harness, agents, reference]
summary: "A qualitative four-way decision guide for choosing plain code, a deterministic workflow, a chatbot or retrieval system, or an autonomous agent, with design principles; no cost or latency numbers back it."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-building-applications-with-ai-agents-ch01-introduction-agents.md
---

# Code, Workflow, RAG or Agent Decision Guide

The first chapter of a book on building applications with agents treats agency as a spectrum. Its test for a true agent is whether the system makes real decisions rather than following a fixed script. It then offers a guide for choosing the simplest tool that fits.

## The four options

- **Plain code** when the input shape is known in advance, the response must arrive within milliseconds, or a regulated domain needs deterministic, auditable logic.
- **Deterministic workflow** when every branch can be listed and you need audit, retries with backoff or human approval.
- **Chatbot or retrieval system** when the job is answering questions over a corpus with few external actions.
- **Autonomous agent** where input is messy, new or very varied and needs multistep adaptive planning, parallel subtasks or learning from feedback.

Four questions precede choosing an agent: is the input unstructured, does the task need adaptive multistep planning, would retrieval do, and are the latency and upkeep acceptable.

## Principles and framework advice

The chapter lists scalability, modularity, resilience and future-proofing; it advises against hardcoding tools in the agent service or tying prompts to one vendor, and recommends retry and fallback logic. For models it suggests starting with a strong general model, routing simple queries to small cheap ones, and designing for several models. For frameworks it suggests CrewAI or an agents SDK for prototypes and LangGraph or AutoGen for production-grade control, noting frameworks are optional.

## Limits

- No experiments of its own; the guidance is qualitative and the scalability example (10 versus 1,000 tickets a minute) is illustrative.
- The model table is an August 2025 leaderboard snapshot (reported by the book, scores from one benchmark suite) and has dated.
- Author and year are not printed in the text.

## See Also
- [[Framework Selection — LangChain vs LangGraph vs Deep Agents]] — related
- [[Agent Fundamentals]] — prerequisite-for
