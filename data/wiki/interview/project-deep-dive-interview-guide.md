---
title: Project Deep-Dive Interview Study Guide
tags: [interview, reference]
summary: "Method guide for the project deep-dive / experience review — seniority reads as decisions defended, not technologies listed: a three-altitude answer per project, a constraints-at-the-time decision template, a five-part incident story where the isolation step is the hardest part to fake, calibrated ownership language, confidentiality-safe constraint shapes, and the eight probe chains that pull a project apart."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--project-deep-dive.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--project-deep-dive--README.md
  - data/raw/repos/sisyphus/interviewing--rounds--project-deep-dive--README.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--project-deep-dive--study-guide.md
  - data/raw/repos/sisyphus/interviewing--rounds--project-deep-dive--study-guide.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--project-deep-dive--questions.md
  - data/raw/repos/sisyphus/interviewing--rounds--project-deep-dive--questions.md
  - data/raw/repos/sisyphus/interviewing--rounds--project-deep-dive--probe-bank.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--project-deep-dive--sources.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--project-deep-dive--examples--README.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--project-deep-dive--examples--architecture-walkthrough.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--project-deep-dive--examples--decision-defense.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--project-deep-dive--examples--incident-story.md
---

# Project Deep-Dive Interview Study Guide

The standard senior-signal round (45–60 min on one or two projects): did you build what the
resume claims, at the depth claimed? The interviewer drills until they hit the boundary of
your ownership. Core in every senior AIE/MLE/FDE loop; for FDE it doubles as a sample of how
you explain to a customer. 2026 standard probe: "where did you use AI tools, and how did you
verify their output?"

## Three altitudes per project

Shift on the interviewer's signal; practice with someone interrupting, because solo
rehearsal never surfaces the transition gap.

1. **Executive pitch (60 s)** — "We had [problem] costing [stakeholders] [consequence]. I built
   [what], which [mechanism in one sentence]. Result: [number]." Over 90 s means you slipped
   to altitude 2.
2. **Architecture walk (5 min)** — data-flow narrative, three technology choices with
   one-line rationales, one constraint that shaped the design, scale numbers. Draw while
   talking: boxes, cylinders, labelled arrows, read path separated from write path, sync vs
   async marked, scale annotations. If you can't draw it cold in ~3 minutes, you don't own it.
3. **Deep dive (unbounded)** — prepared per component: alternatives and why they lost, one
   implementation surprise, the operational failure mode you'd guard, the number that
   characterizes it.

## Decision defense: constraints, not taste

For each significant decision write down: what you chose; date context (state of the art
then); constraints at the time (team, timeline, budget, infra, data); the alternative
rejected and *the specific thing* that eliminated it; why the winner won; what it cost;
what changed since; would you choose it today. "Postgres because it's reliable" is a
preference; "Postgres because billing needed ACID and the team had no distributed-datastore
operating experience at our scale" is a decision. Under sustained probing, hold the
position on the original constraints, concede trade-offs honestly, and update openly where
the landscape has changed (e.g. a managed vector store chosen for zero-ops at small scale
vs a Postgres-native option once the team already runs Postgres).

## Incident story: Detection → Isolation → Root cause → Fix → Prevention

| Part | Must contain | Weak version |
|---|---|---|
| Detection | How you knew — and why monitoring didn't catch it first | "A user reported it" |
| Isolation | Hypotheses in order, how each was tested, what it ruled out | Jumping straight to the cause |
| Root cause | The mechanism and the assumption it violated | "There was a bug" / "a race condition" |
| Fix | Immediate *and* stabilizing change | Hotfix only |
| Prevention | Named artifacts: alert, test, runbook, architecture change | "We were more careful" |

**Isolation is the hardest part to fake** — someone who didn't debug it can't narrate the
intermediate hypotheses. The worked example (silent RAG quality degradation after a corpus
update) shows the shape: first hypothesis "old vectors weren't deleted" was true but didn't
explain the ranking; retrieval traces with scores led to embedding metadata; root cause was
vectors from two embedding-model versions coexisting in one index. Preventions were three
artifacts — model version pinned in config, a post-ingest check that every vector carries
the same model-version tag, and a golden-set retrieval eval gating the index swap — closed
by the broader lesson: latency and error-rate monitoring existed, a correctness signal did
not (see [[Production Hardening Patterns]]).

## Ownership calibration

"We" for everything is ambiguous, not humble. Use precise verbs — designed and built / led
the design that three engineers implemented / contributed the [component] / reviewed and
flagged — then credit the team. At the edge of your ownership say so ("that component was
another team's; here's how it behaved from our side") rather than guess. Inflated claims
die on the next follow-up.

## Numbers and "differently today"

Write the numbers down before the interview — latency percentiles, error rate, scale, cost
(lead with the delta, anchor with absolutes: "60%, from $28K to $11K/month"), business
impact. No numbers for a project you *led* is a yellow flag; if uninstrumented, say so and
give the qualitative signal. Prepare one architectural and one process "differently today"
answer per project, each tied to the failure that revealed it. "Nothing" is disqualifying;
"more time" is a complaint, not a decision.

## The eight probe chains

Deep-dive questions cluster into eight openers, each followed by a predictable probe chain.
Prepare one project against all eight; the probes are where unrehearsed ownership shows.

| Opener | Probes to expect | Strong answer does |
|---|---|---|
| End-to-end walkthrough | Trace one request from input to output; where does the core logic sit and what feeds it context; riskiest component and why | Business problem first, not a tool list; own role explicit; one level deeper on any component; one concrete metric |
| Nasty bug / incident | How you first noticed; how you formed and tested hypotheses; which signals (logs, metrics, traces, repro); how you verified the fix | symptom → hypothesis → isolation → root cause → fix, named tools, verified with evidence, a systemic prevention |
| Why this design / stack | Alternatives seriously rejected; the deciding constraint; what would have flipped it; where you followed vs broke convention; the choice you're least sure of | "X over Y because Z" tied to a real constraint; admits uncertainty |
| Evaluation — real framework or vibes? | How the golden set was built; why those metrics; how you trusted an LLM judge; how a regression was caught before users; post-deploy drift monitoring | Offline set and/or online signal with real numbers; regression detection and monitoring, not a one-time check; names the eval's own limits |
| Hardest trade-off | What it cost (latency, complexity, cost, flexibility); data, prototype or judgment call; still comfortable today? | A specific trade-off, never "speed vs quality"; quantified; honest current view |
| 10× scale and cost | First bottleneck to break and how you know; dominant cost drivers and how measured; levers in order (cache, batch, tier, redesign); detecting degradation before users | Concrete bottleneck, real cost drivers with numbers, ordered levers, scale tied to monitoring |
| Start over / next | Which decision you'd reverse; new information vs a mistake you own; what changes if scale or requirements differ | A specific reversal tied to a lesson; distinguishes new information from error; credible next step |
| What you personally owned | One thing that wouldn't have happened without you; where you disagreed with the team | Clear "I" vs "we" line, at least one owned decision, team credited, a concrete artifact |

The eval opener is the one AI-role loops lean on hardest — have the golden-set provenance
and one caught-regression story ready (see
[[Evals and Observability Interview Study Guide]]).

## AI-tools probe and confidentiality

Have a specific map of where you used AI tools, the verification per use (read every line +
tests for code; check claims against docs for architecture suggestions; hand-labelled
sample for analysis), one concrete case where it was wrong, and where you chose not to use
it (security-critical or load-bearing correctness). Describe clients by **shape** —
scale, problem, constraint ("strict data residency meant the model ran in the client's own
cloud") — and rehearse it so a name doesn't slip mid-story.

## See Also
- [[AI Role Interview Loop Map]] — extends (the deep-dive is one of the rounds self-made lists miss)
- [[System Design Interview Study Guide]] — prerequisite-for (your own systems rehearsed as design drills)
- [[Behavioral Interview Study Guide]] — alternative-to (story-shaped answers about behavior vs about systems)
- [[Customer Simulation Interview Study Guide]] — extends (altitude matching, live)
- [[Evals and Observability Interview Study Guide]] — prerequisite-for (the "how did you measure success" story)
- [[Production Hardening Patterns]] — extends (embedding model version pinning)
