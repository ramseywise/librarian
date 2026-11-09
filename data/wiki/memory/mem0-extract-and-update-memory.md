---
title: "Mem0 Extract-and-Update Memory"
tags: [memory, pattern]
summary: "Mem0 extracts salient facts from each message pair and lets an LLM choose ADD, UPDATE, DELETE or NOOP against similar stored memories; its authors report near-full-context accuracy on LoCoMo at a fraction of the latency and tokens, with a graph variant that helps temporal questions but not single- or multi-hop ones (self-reported, company authors)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-chhikara-2025-mem0.md
---

# Mem0 Extract-and-Update Memory

Mem0 (a preprint by the Mem0 team) reads each message pair along with a running conversation summary and a window of recent messages. An LLM proposes candidate facts, each fact is checked against the closest existing memories, and the LLM selects an operation by function call, either ADD, UPDATE, DELETE or NOOP. The Mem0g variant keeps entities and their relations as a directed, labeled graph in Neo4j, where LLM conflict resolution marks a relation invalid instead of deleting it.

## Results

Setup: the LOCOMO benchmark (10 conversations, roughly 26k tokens each) with GPT-4o-mini, LLM-judge score J; the judge model is not named and the adversarial category is excluded. All figures are self-reported.

- Full context still has the highest overall J (about 73%) but about 17 s p95 total latency; the authors frame memory as a cost trade-off.
- Mem0 search latency is the lowest of all methods (p95 0.200 s); memory footprint is about 7k tokens per conversation for Mem0, about 14k for Mem0g and over 600k for Zep, against about 26k raw.
- Mem0 shows a 26% relative J gain over OpenAI's memory; the best RAG configuration peaks near 61% J.
- Mem0g does best on temporal questions, while Mem0 does better on single-hop (67.13 against 65.71) and multi-hop (51.15 against 47.19). Zep scores highest on open-domain questions (Mem0g 75.71, Mem0 72.93).
- The OpenAI memory baseline does very badly on temporal questions, which the paper ties to missing timestamps in its memories.

## Limits

- One benchmark and one model; thresholds are unstated; the OpenAI baseline gets all generated memories and its extraction cost is excluded; Zep ran on the platform version, where results improved after several hours (anecdotal).
- That performance holds up whatever the conversation length is stated, not tested on longer conversations. Baseline latencies depend on the authors' infrastructure.

## See Also
- [[Memory Store Operations]] — prerequisite-for
- [[Memory Forms Taxonomy]] — prerequisite-for
- [[A-Mem Zettelkasten Agentic Memory]] — alternative-to
- [[Multi-Session Agent Benchmarks]] — related (LoCoMo)
