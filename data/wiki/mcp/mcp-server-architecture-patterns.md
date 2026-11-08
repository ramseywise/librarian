---
title: MCP Server Architecture Patterns
tags: [mcp, pattern]
summary: "A 2026 industry paper sorts 15 MCP servers into five architecture patterns and reports from one voice-AI deployment that tool-selection accuracy dips below 90% between 10 and 15 tools for Haiku 4.5 and at 30 for Sonnet 4 (self-reported, observational)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-rodrigues-2026-mcp-server-architecture-patterns-llm.md
---

# MCP Server Architecture Patterns

Rodrigues and Vas (Celabe, which runs the ANSYR voice AI platform, and the University of Waterloo; a June 2026 industry-track preprint) catalogue how MCP servers are built. The first author's employer supplies the production data, which the paper discloses.

## Patterns

Open coding of 15 servers (5 of the authors' own, 10 public) gave five patterns, each needing at least two servers: the Resource Gateway, the Tool Orchestrator, the Stateful Session Server, the Proxy Aggregator and the Domain-Specific Adapter. Named anti-patterns include vague or missing tool descriptions and the "God Tool", a single do-anything tool with an undifferentiated schema. Other advice, argued and not tested: sanitise resource content before it reaches the model, return a job ID and a poll tool for long work, authenticate at the transport, return structured errors, and record per call the tool's name, a hash of the input, latency, output size and error code.

## Findings (self-reported)

- **Tool count.** Retrospective production telemetry, Q1 2025, buckets of 1 to 50 tools, 200 session turns each, ground truth a human-confirmed tool: Haiku 4.5 scored 91% at 10 tools and 87% at 15; Sonnet 4 held at or above 90% to 20 tools and fell below at 30. Wilson intervals are within 4 points. The authors recommend about 10 to 15 tools per context and partitioning past that with a scoped Proxy Aggregator; no experiment compares scoped with static aggregation.
- **Speed against accuracy at 10 tools:** Haiku reached 91% with a 245 ms median, Sonnet 95% with 410 ms.
- **Transport:** on a loopback echo server (100 calls, no model), stdio p50 was 0.01 ms and streamable-http 0.39 ms. Three remote rows (30.4, 38.4, 62.4 ms) are modelled from an assumed round trip, not measured.
- **Pattern labelling:** two Claude raters at temperature 0 on 54 held-out servers gave Cohen's kappa 0.76 and 81.5% raw agreement, with 68.5% (Haiku) and 75.9% (Sonnet) agreement with the authors.

## Limits

- Single organisation, retrospective data, not a controlled study; raw logs are not released, only per-bucket numbers. The extraction notes Haiku's 91% sits one point above the line with a 4-point interval, so the crossing is not statistically firm.
- Descriptions are never varied, so the description-quality claim is argued; overlap, schema token cost and description length are not controlled.
- Two Claude models only; thresholds have likely dated. Single-coder pattern derivation; LLM raters may share blind spots; the authors state that none of their work yet ties a pattern choice to measured accuracy.
- The abstract and body agree on Sonnet's range, but its accuracy at 30 tools appears only in a figure.

## See Also
- [[MCP Protocol]] — prerequisite-for
- [[Dynamic Tool Discovery]] — related (retrieval over tools as the answer to tool count)
- [[Tool Design as Context Engineering]] — related
- [[MCP Server Security Patterns]] — related
