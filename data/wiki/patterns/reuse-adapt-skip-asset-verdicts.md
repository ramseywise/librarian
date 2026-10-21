---
title: REUSE/ADAPT/SKIP Asset Verdicts
tags: [patterns, llm, pattern]
summary: A research-scout output contract that forces every existing asset to a three-way verdict with a mandatory "salvageable at lower cost" column — so SKIP is a claim made after inspection rather than the default a fresh agent reaches by not looking.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/agents/research-scout.md
  - data/raw/claude-docs/playground/agents/research-scout.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-09_friction-learning-loop_hook-emission.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-09_friction-learning-loop_prior-art.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-09_friction-learning-loop_telemetry-sinks.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-19_tooling-ledger_pattern-key-mapping.md
  - data/raw/claude-docs/galactus/agents/research-scout.md
  - data/raw/claude-docs/galactus/docs/research/2026-08-15_ml-parity_credit.md
  - data/raw/claude-docs/galactus/docs/research/2026-08-15_ml-parity_fraud.md
  - data/raw/claude-docs/galactus/docs/research/2026-08-15_ml-parity_ltv.md
  - data/raw/claude-docs/galactus/docs/research/2026-08-15_ml-parity_segmentation.md
  - data/raw/claude-docs/galactus/docs/research/2026-08-10_voice-tooling_framework-patterns.md
  - data/raw/claude-docs/galactus/docs/research/2026-08-10_voice-tooling_skill-audit.md
  - data/raw/claude-docs/galactus/skills/proto-research/SKILL.md
  - data/raw/claude-docs/sisyphus/docs/plans/2026-08-08-ml6-genai-prototyping-loop.md
  - data/raw/repos/sisyphus/.claude--docs--plans--2026-08-08-ml6-genai-prototyping-loop.md
---

# REUSE/ADAPT/SKIP Asset Verdicts

The `research-scout` agent (identical definition in guacamayo and playground) researches
**one angle per scout** and returns a fixed four-section report:

```
# Angle
## Findings
## Asset verdicts
## Open questions
```

The `## Asset verdicts` section is the part that earns its place. Every existing asset
the scout touched — a module, a log file, a prior-art repo, a cron job — gets a row:

| Asset | Verdict | Salvageable at lower cost | Reason |
|---|---|---|---|

with the verdict drawn from exactly three values:

- **REUSE** — use as-is.
- **ADAPT** — use with a named change; the change and its rough cost go in the salvage
  column.
- **SKIP** — do not use. **The salvage column is still mandatory**: what in this asset is
  worth keeping even though the asset as a whole is not?

## Why the salvage column is the mechanism

The failure this prevents is the fresh agent's default of rebuilding. An agent that has
not read an existing asset will, if asked "reuse?", answer "no" — not from judgement but
from absence of information, and the answer reads identically to a considered rejection.
The scout definition states the rule as: *"nothing" only after checking; it is a claim,
not a default.* Requiring a salvage entry on SKIP rows makes the check observable: a SKIP
row whose salvage column says "nothing" has to defend that, and in practice the column is
rarely empty.

Observed in the guacamayo research corpus:

- A falsification-study repo (its framework measurably *harmed* reasoning on frontier
  tasks) was SKIPped as a tool, with the salvage column keeping its **experimental
  design** — pre-registration and token-matched filler controls — as the template for
  validating future mechanisms. The negative result became a constraint, the method
  became an asset.
- A rotating pass-log was SKIPped (rotation destroys recurrence history past ~10 days),
  salvaging its context-trimming logic to feed per-signature counter files instead.
- A verdict-scoring engine was SKIPped for friction recurrence with salvage "nothing" —
  stated and defended ("orthogonal concern: scores hypotheses against columns, not
  cross-row patterns"), which is what the rule asks for.
- ADAPT rows carry a cost estimate ("~1 hour to redesign, test on existing logs") so the
  downstream planner can rank them.

## Scoping rules that make the table honest

- **One angle per scout.** A scout asked to cover two angles merges their verdicts and
  the table stops being auditable. Parallel angles get parallel scouts and the caller
  synthesises (see [[Shared Context Brief]] for how the caller grounds them once).
- Findings cite `file:line` and carry a per-finding confidence; verdicts inherit the
  confidence of the findings they rest on.
- Open questions are things the scout could not resolve from the assets it had — not
  suggestions, and not a second verdict list.

## Verdicts on machinery are not verdicts on parts (galactus corpus)

The same scout definition in the galactus prototyping repo produced verdict tables where
most rows were *not* about code volume:

- A "run" that was a dataset plus two empty directories — its code lived in a different
  tree. SKIP on the shells, ADAPT on the data (path-specific ignore rule, pinned
  provenance); salvage was a single `git mv`.
- A pipeline whose headline was a refusal, not a metric ([[Data Sufficiency Refusal]]):
  explicitly *not* worth registering as a reproducible result, because the run itself says
  its number must not be read.
- A fragment of a private notebook whose reported metrics scored an upstream process's
  baked-in forecasts rather than its own models — unfalsifiable from the artifact, so the
  *unverifiability was the finding*; salvage: the domain framing and a feature taxonomy
  worth porting as config.
- A clean clustering run whose only gaps were wiring (argparse, run record), but whose
  record would carry an internal-validity index rather than a refutable claim — the
  "weaker justification" was itself recorded.

The voice-tooling scouts applied the vocabulary to **patterns** rather than files: a
202-async-polling API is *actively wrong* for duplex voice (the constraint inverts); a
deterministic validator *survives with modification* (repair loops cannot run
mid-utterance, so constraints must hold up front); a one-method provider port *reuses*
unchanged — see [[Duplex Voice Breaks Discrete-Turn Assumptions]]. An unrunnable notebook
can still hold a 250-line taxonomy; an empty `src/` can be a free destination. An empty
salvage cell is indistinguishable from the scout not having looked — the same collapse as
[[Collapse Site Detection]] at research altitude.

## In the galactus /proto-research skill

`/proto-research` keeps the verdict table with the "Salvageable at lower cost" cell
mandatory on every row, SKIP rows included. In fan-out mode, an angle that touches existing
assets must be **explicitly told** to emit verdicts, and the merge preserves each row's
salvage cell verbatim. A requirement left unspecified (no stated cost of being wrong, no
answer at one of the five design layers) is logged as a FRAME gap and routed to
`/proto-design`, not filled in by research.

## Origin: a yes/no scout missed the separable part

In a take-home prototyping plan, a scout assessed a project template only as scaffolding to
run and concluded "too heavy" — right about the machinery, but it missed that the
template's intake question set was reusable *without* the machinery that consumed it. The
brief had asked about repos as things you run, so nothing prompted "is any part of this
separable?" The fix went into the scout prompt, not the plan: **when a scout rejects an
asset as too heavy, it must name what remains salvageable at lower cost** — the job the
REUSE/ADAPT/SKIP vocabulary does that yes/no cannot.

## See Also
- [[Claude Workflow System]] — instance-of (the research phase that dispatches scouts)
- [[Shared Context Brief]] — prerequisite-for (the grounding every scout receives)
- [[Stage-Scoped Scout Agents]] — extends (the sibling scouts for build and plan stages)
- [[Friction Promotion Ladder]] — extends (a decision assembled from several scouts' verdict tables)
- [[Capability Parity Audit]] — alternative-to (have/partial/gap for a template vs REUSE/ADAPT/SKIP for assets)
- [[Collapse Site Detection]] — extends (an empty salvage cell is a collapse site)
- [[When a Lens Earns Agenthood]] — instance-of (scouts exist for Parallelism)
- [[Data Sufficiency Refusal]] — extends
- [[Duplex Voice Breaks Discrete-Turn Assumptions]] — extends (verdicts applied to patterns, not files)
