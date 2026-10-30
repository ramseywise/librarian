---
title: Golden Set Mechanics
tags: [eval, llm, reference]
summary: The shape of a golden case (input/expected/metadata), sizing by purpose (20–50 at spec time, 100–1000 for CI), sourcing priority, and the anti-staleness practices that keep a set measuring.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-02_eval-driven-development.md
  - data/raw/claude-docs/guacamayo/skills/workflow-plan/references/golden-set-authoring.md
  - data/raw/claude-docs/guacamayo/skills/workflow-plan/SKILL.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--03-eval-datasets.md
---

# Golden Set Mechanics

The practitioner detail behind [[Eval-Driven Development (EDD)]] — what a golden
case actually looks like, how many you need, and how to keep the set alive.
Converged advice across Langfuse, DeepEval, and Arize.

---

## Case shape

A "golden" is a **pending test case**: input plus expected result, which becomes
a full case only once the app produces `actual_output` at eval time. Minimum
fields:

- `input` — the question/request
- `expected_output` — literal answer, gold reference, **or a list of criteria**
- `metadata` — source, date added, tags (needed for slicing and staleness review)

The closed/open split governs how you assert:

| Question type | Expected field | Grader |
|---|---|---|
| Closed ("what's the refund window?") | exact fact — "must contain 30 days" | code / exact match |
| Wording varies, meaning matters | gold reference | embedding similarity |
| Open-ended | **rubric of 2–4 criteria** | LLM-judge |

---

## Sizing — reconciling two numbers

Anthropic says 20–50; Langfuse says 100–1,000 for CI. Not a contradiction —
different jobs:

| Purpose | Size |
|---|---|
| Single-issue exploration | ~10 |
| **Discovery-exit / initial spec** | **20–50** |
| PR gate (must stay fast) | tens–low hundreds |
| Full CI on larger changes | 100–1,000 |

The spec-time threshold is 20–50. The set grows toward the CI numbers *after*
launch, fed by production failures — it is not a genesis-time obligation.
Over-speccing at discovery is the known failure mode of ATDD adoption.

---

## Sourcing priority

1. **Production traces** — real traffic beats invented examples
2. **Existing manual tests / bug reports**
3. **Synthetic generation — last resort**, and only reviewed by a domain expert

⚠️ At discovery-exit there *is* no production traffic, so a greenfield set is
necessarily rows 2–3. That is acceptable — it is the spec, not the regression
suite — but synthetic cases must not be presented as validated. Every case
should cite a real scope risk, which is the traceability that keeps an
invented set from encoding wishful thinking.

---

## Keeping it alive

Treat the set as an **append-mostly log tracking production**:

- wire thumbs-down / failures in automatically
- date every item; review quarterly
- archive (don't delete) retired cases
- dedupe near-duplicates — they silently overweight one case in every average
- **version the set and pin a version per experiment**, or comparisons are meaningless

This is Anthropic's "watch for saturation" with concrete mechanics: a suite
everything passes has stopped measuring.

---

## Portability note

A golden set kept as plain JSONL in git is diffable, framework-neutral, and
readable by any runner. Keeping a specific harness (promptfoo, DeepEval,
Langfuse, Braintrust, Phoenix) as *a* runner pointed at that set — rather than as
the source of truth — decouples the spec from any vendor. This mattered
concretely when Promptfoo was acquired by OpenAI (2026-03-09, with an
open-source-under-current-license commitment): not urgent, but a reason not to
let a vendor tool own the specification.

---

## Traceability and the authoring gate

guacamayo's plan stage authors goldens from design-table rows with a `source_risk` field:
the in-scope or open-question bullet the case traces to, quoted verbatim. A case that
traces to nothing is a case nobody asked for, and the gate fails on an empty or unmatched
`source_risk` at any count — which also makes padding visible as duplication. Grader is
chosen per case, cheapest that can decide (`code` for substring/regex/enum/boolean,
`judge` only for tone, completeness or reasoning); a case neither can decide is not ready.
Gate thresholds: **<10 cases FAIL, 10–19 WARN, ≥20 PASS**, with positive and `must_not`
cases balanced. As of 2026-08 no gate skill enforced this — the thresholds were an
authoring target applied by hand.

## Two pools and per-row metadata (course synthesis)

Keep two pools: a **regression suite** of known, fixed failures that must keep passing, and a rolling
**discovery set** of new production failures that shows where the system currently breaks. The flow:
production failure → triage (real failure or eval bug?) → label with the [[Eval Failure Taxonomy]] →
discovery set → once fixed, move to the regression set.

Every row should carry:
- **Labels** for slicing (intent, language, difficulty, source type, segment) — so results can be reported per slice.
- **Eligibility** per gate (e.g. `retrieval`, `generation`) — a downstream gate never silently scores rows an upstream gate marked ineligible.
- **Provenance** (source, date added, who added it) — for trust and staleness review.
- Optionally **per-row graders** — the cheapest grader that can decide that row.

Sizing and its uncertainty are on [[Eval Error Bars and Sample Size]]; leak defenses on
[[Eval Contamination Defenses]].

## See Also
- [[System Design — Unified Eval Harness]] <!-- auto-linked -->
- [[Eval-Driven Development (EDD)]] — prerequisite-for
- [[Eval vs Test Distinction]]
- [[Anthropic Three-Tier Eval Taxonomy]] — extends
- [[Synthetic Dataset Generation for RAG Eval]] — alternative-to
- [[HITL Annotation Pipeline]]
- [[Scope-POC Design Interview]] — prerequisite-for (design-time metric targets become evals/targets.yaml)
- [[Skill Pipeline Dryrun Testing]] — alternative-to (fixed unambiguous cases for a skill chain rather than a model)
- [[Eval Ladder]] — part-of (rung 2 of the maturity progression)
- [[Manual Review as Eval Bootstrap]] — prerequisite-for (failure patterns become the first golden cases)
- [[User Feedback Loops]] — feeds (thumbs-down cases expand the set post-deploy)
- [[Conversational Test Fixture Design]] — alternative-to (fixture authoring when the input is dialogue)
- [[Eval Suite Maintenance]] — extends (the eight authoring rules, incl. negative cases and the two-expert test)
- [[Eval Non-Determinism]] — complements (a golden row is scored over k trials, not one)
- [[Answer Criteria with Named Wrong Answers]] — extends (named wrong answers as adversarial case seeds)
