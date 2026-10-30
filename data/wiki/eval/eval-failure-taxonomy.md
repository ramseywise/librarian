---
title: Eval Failure Taxonomy
tags: [eval, llm, pattern]
summary: "A fixed set of stable failure labels, ordered by pipeline stage, one label per fix, including the eval's own failures (context_missing) — the shared vocabulary for graders, dashboards, gate reports and bug tickets."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--02-defining-correct.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--04-graders.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--12-failure-modes.md
---

# Eval Failure Taxonomy

The output of [[Error Analysis (Open and Axial Coding)]] is a **failure taxonomy**: a fixed
label set for the ways a system fails. It becomes the vocabulary every other eval artifact
aggregates by — grader outputs, dashboards, gate reports, bug tickets.

## Rules for a usable taxonomy

- **Stable names.** `rank_miss`, not "retrieval was kinda off". Dashboards aggregate by
  label, so renaming one breaks history.
- **One label points to one fix.** If a label could be fixed by changing retrieval *or* the
  prompt, split it.
- **Ordered by pipeline stage.** An upstream failure masks everything downstream, so label
  the earliest one (the same first-failure rule as open coding).
- **Include the eval's own failures.** `context_missing` — the grader received no passage
  text — is a label too. It stops eval bugs being counted as system bugs
  ([[Eval Suite Maintenance]]).

## Worked shape (RAG support agent)

| Stage | Labels |
|---|---|
| Corpus | `source_missing`, `url_unmapped`, `topic_proxy` |
| Index | `index_lag`, `chunk_fragmented` |
| Retrieval | `rank_miss`, `query_rewrite_miss`, `reranker_regression` |
| Eval infrastructure | `context_missing` |
| Generation | `citation_hallucination`, `unsupported_claim`, `incomplete_answer` |
| Behavior | `wrong_escalation`, `refusal`, `schema_violation` |

The project-level instance of this table lives in [[RAG Eval Gate Contract]].

## Where labels are consumed

- **Graders** emit the labels a trial earned alongside the score (the grader interface's
  `labels` field — see [[Grader States (Heuristic, Calibrated, Experimental)]]).
- **Gates** report `top_failure_labels` so a failed gate names what broke
  ([[Run-Then-Assert Eval CI]]).
- **Flipped-task review** reads whether regressions cluster on one label — clustered means a
  story, scattered may mean noise ([[Paired Eval Comparison]]).
- **Production triage** labels each harvested failure before it becomes a discovery row.

Review labels on a schedule (quarterly is the course's suggestion): unused labels are eval
debt.

## See Also
- [[Error Analysis (Open and Axial Coding)]] — prerequisite-for (axial coding produces the categories)
- [[RAG Eval Gate Contract]] — instance-of (a project's stable label set)
- [[Trajectory Over Outcome]] — related (label the earliest wrong decision in the path)
- [[One Check Shape for Quality Verdicts]] — related (one verdict shape so labels join across a pipeline)
