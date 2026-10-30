---
title: Rationale-Blind Worst-Case Review
tags: [patterns, llm, pattern]
summary: A read-only advisor that deliberately ignores a plan's stated rationale and asks only "what is the worst plausible outcome, how reversible is it, and does nothing-happening look like success?" — ranking by consequence rather than probability so the one failure worth fixing first surfaces instead of a padded list.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/guacamayo/agents/fog-advisor.md
  - data/raw/claude-docs/galactus/agents/fog-advisor.md
  - data/raw/claude-docs/galactus/skills/fog/SKILL.md
  - data/raw/claude-docs/galactus/skills/fog/evals/README.md
  - data/raw/claude-docs/galactus/skills/decide-shared/SKILL.md
  - data/raw/claude-docs/guacamayo/skills/fog/SKILL.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-orchestrator-design.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-orchestrator-design.md
---

# Rationale-Blind Worst-Case Review

The `fog-advisor` agent in the guacamayo repo is a review role with an unusual contract: it
is **rationale-blind**. It is handed a plan, a brief, or a diff and told not to evaluate
whether the approach is a good fit, not to propose alternatives, and not to fix anything.
Its only job is to answer: *if this goes wrong, what is the worst plausible thing that
happens, and would anyone notice?*

The reason for blinding it to rationale is that rationale is persuasive. A reviewer who
reads "we chose X because Y" tends to argue with Y. Fog's value is that it never engages
the argument; it only follows the mechanism to its worst defensible endpoint.

## The four passes

Each pass is a different question put to the same artefact. Findings are numbered
`FA-001…` and carry the pass that produced them.

1. **Empty-input collapse.** For every step, ask: *is nothing distinguishable from
   success?* A job that reads zero rows, a scan that finds zero files, a token that
   expired and reads as "no PRs" — if the empty case produces the same exit code and the
   same report as the healthy case, the plan has a silent-failure site. This pass is the
   one most often non-empty; it is the same defect family as [[Silence Reads as Clean]].
2. **p99 ranking.** Enumerate plausible failures, then **rank by consequence, not
   probability** — `decision_impact` first, `confidence` second. A 2% chance of
   corrupting the only copy of a log outranks a 40% chance of a flaky test. Most
   reviewers unconsciously sort by likelihood, which buries the catastrophic-but-rare.
3. **Reversibility / least commitment.** For each irreversible or hard-to-reverse step,
   **name the rollback mechanism** — not "we can revert" but the specific command, file,
   or backup that undoes it. If none can be named, that is the finding. This is the
   question that [[Reversibility Cliff]] later turns into a policy boundary.
4. **Determinism of chained probabilistic steps.** A pipeline of four steps each "about
   95% reliable" is ~81% reliable end to end; a plan that treats each as effectively
   certain has mis-estimated the whole. Fog multiplies the chain and reports the product.

## What it refuses to do

- Does not evaluate fitness of the approach or propose alternatives — that is a
  different reviewer's job (see [[Wander — Question-Generating Review Agent]], which
  asks the open questions fog deliberately skips).
- Does not fix. Read-only; the output is a report.
- Does not pad. If a pass finds nothing, it says so in one line. The closing section has
  exactly two items: **the one to fix first** and **what could not be evaluated** (inputs
  it did not have, steps too vague to trace).

## Operational notes

- Runs on the cheapest model in the fleet (haiku-class) — the four questions are
  mechanical enough that a strong model adds cost without adding findings.
- Findings are emitted against the shared claim schema used by the review family
  (`review-defense/references/claim-schema.md`), so they can be merged into a verdict
  alongside defect scanners rather than read as a separate memo.
- Dispatched by a `/fog` skill, typically before a plan is executed rather than after a
  diff lands, because passes 3 and 4 are cheapest to act on before commitment.

## Why it is its own role

Defect scanners find what is wrong in code as written; question generators find the
decision never made. Neither asks "what does the empty case look like?" or "multiply the
chain." Those are consequence questions, not correctness questions, and bundling them
into a general reviewer dilutes both — the general reviewer argues with the rationale,
and the consequence questions get one bullet at the bottom.

## Dispatch discipline (galactus variant)

The galactus copy of the advisor is dispatched as **stage 4 of the `/fog` pass** (see
[[Collapse Site Detection]]) and adds rules about *how* the caller must treat it:

- **Pass design and scope only — never the caller's own stage 1–3 findings.** *"If you
  brief it on what you already found, its agreement stops being evidence."* The advisor's
  passes deliberately overlap the caller's inline empty-input and reversibility stages;
  *that overlap is the check, not waste*. Where it independently finds what you found,
  confidence rises; where it finds what you missed, you missed it.
- **Resolve before dispatch, and read the exit code.** `resolve-capability fog` with an
  explicit repo root (CWD-relative resolution can silently check the wrong tree); exit 1
  means the agent is not loaded.
- **Dispatch failure is recorded, not papered over.** The stage is written as
  `dispatch failed — <reason>`; the caller **must not run the advisor's contract inline**
  — an advisor contract executed by the caller is not an independent advisor. *"A /fog run
  whose stage 4 did not happen is a fog pass with a hole in it"*, and the hole must be
  visible to the reader.
- **The eval checks the briefing, not just the findings.** A judge invariant verifies the
  advisor received spec and scope only; a run that briefs the advisor and then reports its
  agreement as corroboration has broken the check while appearing to pass it.

This is the **Isolation** reason an agent exists at all — see
[[When a Lens Earns Agenthood]]: corroboration is evidence only when the parties could
not see each other, which is also why skills orchestrate agents and never the reverse.

## Generalized: pass the output, not the deliberation

The galactus control-plane design lifted the advisor's withholding rule to every phase
handoff: "an advisor who has read the justification evaluates the justification." **An
orchestrator that hands a phase agent the previous phase's reasoning gets an agent that
grades the reasoning** — a plan agent given research's confidence levels inherits them
instead of testing them. Each phase receives the prior phase's *output*, not its
deliberation (the same reason the plan skill compacts before execute).

The repo's subagents differ precisely in what context they get: **shared ground truth**
(review reporters all get one brief, so their findings describe the same code — see
[[Shared Context Brief]]), **divergent angles** (research scouts get one angle each, because
the value is non-overlap), and **deliberate withholding** (this advisor). Choosing among the
three is the real context-engineering decision for any dispatch.

## See Also
- [[Wander — Question-Generating Review Agent]] — alternative-to (open questions vs worst-case consequences)
- [[Deterministic Review Substrate]] — extends (another read-only reporter feeding the same verdict)
- [[Silence Reads as Clean]] — extends (pass 1 is a systematic hunt for this defect)
- [[Reversibility Cliff]] — prerequisite-for (pass 3 is where the cliff is first located)
- [[Scope-Gated Reporter Dispatch]] — instance-of (one reporter among several, run or skipped by scope)
- [[Collapse Site Detection]] — related (part of; stage 4 of the fog pass)
- [[When a Lens Earns Agenthood]] — instance-of (the Isolation case)
- [[Two-Axis Claim Schema]] — extends (the FA- claim format)
- [[Adversarial Plan War Game]] — alternative-to (multi-angle isolated attackers on the same plan)
- [[Plan Epistemic State Axis]] — extends (where this advisor's outcome is recorded)
- [[Size the Gate to the Blast Radius]] — extends (when this advisor is dispatched)
- [[Decision-Seat Inventory for a Control Plane]] — extends (phase handoffs inherit the withholding rule)
