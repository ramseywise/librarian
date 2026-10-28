---
title: Verify the Issue's Premise Before Planning
tags: [meta, llm, pattern]
summary: "An issue body is a hypothesis about the codebase written before anyone looked. Check its factual claims against the code and data before planning. In one repo's plan docs, four of five issues had a load-bearing premise that was false, and every correction changed the plan."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/GUA-43-plan.md
  - data/raw/repos/guacamayo/.claude--docs--plans--GUA-43-plan.md
  - data/raw/claude-docs/guacamayo/docs/plans/GUA-45-research.md
  - data/raw/repos/guacamayo/.claude--docs--plans--GUA-45-research.md
  - data/raw/claude-docs/guacamayo/docs/plans/GUA-46-research.md
  - data/raw/repos/guacamayo/.claude--docs--plans--GUA-46-research.md
  - data/raw/claude-docs/guacamayo/docs/plans/GUA-46-plan.md
  - data/raw/repos/guacamayo/.claude--docs--plans--GUA-46-plan.md
  - data/raw/claude-docs/guacamayo/docs/plans/GUA-62-plan.md
  - data/raw/repos/guacamayo/.claude--docs--plans--GUA-62-plan.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-20_git-activity-granularity.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-20_git-activity-granularity.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-08-05-typed-graph-retrieval.md
---

# Verify the Issue's Premise Before Planning

guacamayo's plan docs open with a section headed "Issue as filed vs. what's actually
true" or "Premise corrections (verified)". Across one batch of plans, the issue's own
framing was wrong far more often than right.

| Issue claimed | What inspection found | How the plan changed |
|---|---|---|
| A dashboard filter on the "client field (already captured, not yet surfaced)", with "all panels respond to it" | No `client` key in 300+ transcripts, and no surface signal anywhere in the pipeline. The real field (`entrypoint`) had exactly **one** observed value locally. The dashboard was static HTML with zero JavaScript | New plumbing through parser, fact store and dashboard instead of "surfacing". Store the field as an open string, since one machine cannot enumerate the value space. Make the first-JS-in-codebase decision explicitly |
| Name sub-agents for 5 top workflows | Two were already done, one forbids sub-agents by design, two spawn nothing | Ship one contract and record dispositions for the rest ([[Cumulative Metric Hides the Fix]]) |
| "Autocompact regression": it worked, then broke | Raw transcripts showed the **reverse**: zero automatic compactions on four days, then daily automatic compactions from the fifth on. The dashboard's hand-written prose stated the opposite of its own adjacent chart data | No code fix. Correct the prose, refresh the stale data, persist the trigger type ([[Rate Metrics Measure the Logger]]) |
| "Existing sweeps predate it" and "lint/perf findings" | No sweep files existed, because a pre-commit rule blocks staging that directory. The spec covered style and naming only, not performance | The enum migration risk disappeared. Performance was deferred, not answered |
| A plan's risk section: "the daily job already runs `git fetch`" | No `git fetch` anywhere in the code. A cited constant and a cited dataclass field also did not exist | Refinement told the executor to add the fetch, define the map, and add the field. Never import a nonexistent constant |
| A spawn prompt's "established facts" for typed-graph retrieval: the wiki graph is untyped, so edges should be typed | 735 canonical typed edges already existed across 202 pages, and one-hop expansion was already wired. The cited link count included index files | The research question became "does the existing typed layer measurably help?" That led to an ablation and a null result ([[Typed-Graph Retrieval Ablation]]) |

## Why it keeps happening

Issues are filed from memory, from another doc's "out of scope" list, or from a
dashboard's narrative. All of these are claims, not observations. The most dangerous
false premises sound like status: "already captured", "already runs", "existing
sweeps". They tell the planner the work is smaller than it is, or that a mitigation
already exists. A risk-section mitigation that cites existing behaviour is itself a
load-bearing assumption ([[Assumption Audit]]).

## Rule

Before drafting steps, turn each factual claim in the issue into a command: grep the
corpus, grep the code, read the file, count the rows. Record the result as a premise
correction at the top of the plan. When the framing is inverted, as in "regression" vs
"recovery", the deliverable usually becomes a correction to the artefact that produced
the framing, not a code fix.

## See Also
- [[Re-Derive, Never Re-Read]] — extends (an issue body is a recorded claim; re-run the evidence)
- [[Assumption Audit]] — extends (premises hiding in confident status language)
- [[Fallback Mistaken for the Design]] — related (another review that opened with corrections before design)
- [[Analysis Gap vs Collection Gap]] — related ("already captured" is a collection claim worth checking first)
