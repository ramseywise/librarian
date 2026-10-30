---
title: AI Engineering Take-Home Landscape
tags: [interview, eval, reference]
summary: "Field data on what AI-engineering take-homes ask for (RAG 40%+, agents 30%+, 2–4h of work over 2–7 days, then a defense round that often outweighs the code), how they are graded, the single biggest differentiator (build the eval harness first), and the recurring hidden constraints in real prompts that a practice build should rehearse."
updated: 2026-10-30
sources:
  - data/raw/repos/sisyphus/interviewing--rounds--case-study--take-home-field-data.md
  - data/raw/repos/sisyphus/interviewing--rounds--case-study--README.md
---

# AI Engineering Take-Home Landscape

[[Case Study Interview Study Guide]] covers how to write up and defend a take-home. This
page covers what take-homes actually ask for. The data comes from a third-party analysis
of about 1,765 job descriptions and 100+ public submission repos from late 2025 to mid 2026.

## Prevalence and shape

- About a third of companies that disclose their process include a take-home, and a few more use paid work trials.
- Topic mix: **RAG 40%+**, agents and tool calling 30%+, conversational 20%+, document processing ~15%, LLM-as-judge eval 10%+.
- **2–4 hours of real work** with a 2–7 day deadline. They grade decisions and clarity, not code golf.
- Usually followed by a **45–90 minute defense round**, which often matters more than the code.
- AI coding tools are almost never banned, rarely explicitly allowed, and mostly not mentioned. See [[AI-Assisted Take-Home Playbook]].

## How they are graded

Rubrics that are published cover functional correctness, code quality and architecture,
**evaluation methodology**, production readiness (caching, monitoring, cost, PII handling,
rate limiting), stated performance targets (for example p95 under 2s, 100+ req/s, cache
hit rate above 40%), tests (sometimes mandatory, sometimes with coverage targets), and
documentation of decisions and trade-offs. Some publish weights, for example 30%
functionality / 30% challenge completion / 25% context engineering / 15% code quality.
Quantitative tasks name their metric, such as RAGAS faithfulness and context precision for
RAG or ARI/NMI for clustering.

## The differentiator: eval first

Across submissions, the clearest dividing line is that **submissions which don't evaluate
the AI outputs don't get offers**. Hiring teams report "doesn't start with evals" as a red
flag. Build the eval harness before the main logic. This is the take-home form of
[[Build the Checker Before the Generator]].

Other traits of strong submissions: clarifying questions before starting, design decisions
written down with the alternatives considered, a short video walkthrough, configurability
(models and chunking strategies set in config), basic edge-case tests even when not
required, cost and latency estimates, and technical metrics tied to business outcomes.
Common failures: too little effort (the most cited), over-engineering without
justification, and not preparing for the defense.

## Hidden constraints that recur in real prompts

Prompt categories: RAG and document Q&A, agents and tool calling, multi-agent and workflow
engines, document extraction, full-stack AI apps, legal-document workflows, and LLM
infrastructure. Within them the same constraints keep appearing, and each is worth
rehearsing as its own practice build:

| Constraint | Typical form |
|---|---|
| Abstain when unanswerable | "respond 'I don't have that information'"; an eval set split into answerable, partially answerable and unanswerable |
| Mandatory citations | every answer cites a source; out-of-scope questions get a safe fallback |
| Approval gate on side effects | bash commands, outbound messages or finalization need explicit human approval |
| Data minimization to the model | only aggregates go to the LLM, never raw rows; PII requests are detected and refused, and refusal correctness is graded as its own dimension |
| Bounded execution | workflow engine with a step cap and built-in infinite-cycle protection; mandatory unit tests |
| Behaviour-preserving refactor | clean up a messy RAG app while keeping the exact external API, removing global mutable state, and making it testable without running services |
| Resisting injection | a support workspace that applies policy, resists prompt injection, and writes structured decision logs |
| Safety-critical domains | crisis detection, PII redaction and pseudonymization, no secrets in logs, "educational, not advice" |
| Learning from edits | a legal workflow that ingests messy documents, drafts with citations, and improves from operator corrections |
| Performance targets | routing, exact plus semantic caching, provider failover and tracing against stated throughput and latency targets |

Practice protocol: pick one prompt, set a 3-hour timer, and deliver a repo whose README
covers design decisions, the eval harness and its results, what you would do with more
time, and cost and latency estimates. Then rehearse the defense.

## See Also
- [[Case Study Interview Study Guide]] — extends (what the take-home format actually contains)
- [[AI-Assisted Take-Home Playbook]] — extends (how to spend the hours once you have the prompt)
- [[Timebox-Scaled Deliverable Bar]] — extends (how the deliverable bar moves with the window)
- [[Build the Checker Before the Generator]] — instance-of (eval harness first)
