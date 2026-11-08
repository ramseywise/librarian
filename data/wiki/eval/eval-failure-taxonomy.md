---
title: Eval Failure Taxonomy
tags: [eval, llm, pattern]
summary: "A fixed set of stable failure labels, ordered by pipeline stage, one label per fix, including the eval's own failures (context_missing) — the shared vocabulary for graders, dashboards, gate reports and bug tickets."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--02-defining-correct.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--04-graders.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--12-failure-modes.md
  - data/raw/papers/2026-11-05-borji-2023-categorical-archive-chatgpt-failures.md
  - data/raw/papers/2026-11-06-albayaydh-2026-beyond-leaderboard.md
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

## An archive is not a rate

A catalogue of failure examples tells you which labels exist, not how often each occurs.
Borji's archive of early ChatGPT failures (arXiv 2302.03494, 2023) sorts them into 11
categories that the author calls arbitrary and overlapping, from a convenience sample with no
denominators, and later model versions were re-tested ad hoc. Use such an archive to seed
candidate labels, then measure frequencies on a sampled set of your own traces
([[Error Analysis (Open and Axial Coding)]]).

## One literature's clusters

Albayaydh et al. (arXiv 2607.05775, 2026), a narrative synthesis of 27 benchmark, taxonomy and
audit papers on LLM agents, group reported failures into six clusters, namely tool invocation, planning with
constraints, degradation over long horizons, multi-agent coordination, safety, and the validity
of measurement itself. The clusters are the authors' own and, as they note, have subjective boundaries.
Figures they pass on are second-hand and stated with few setups; two examples from the cited
work: GPT-4 reached a 0.6% final-plan success on TravelPlanner, and the MAST study (7 frameworks,
over 200 tasks, manually annotated traces, Cohen's kappa 0.88) coded 14 multi-agent failure
modes in three categories. The paper's own gaps: it covers only English text and web tasks, cites a few sources that
were not peer reviewed and reproduced no experiments.

## See Also
- [[Error Analysis (Open and Axial Coding)]] — prerequisite-for (axial coding produces the categories)
- [[RAG Eval Gate Contract]] — instance-of (a project's stable label set)
- [[Trajectory Over Outcome]] — related (label the earliest wrong decision in the path)
- [[One Check Shape for Quality Verdicts]] — related (one verdict shape so labels join across a pipeline)
- [[AgentBench]] — related (four outcome categories for failed runs)
