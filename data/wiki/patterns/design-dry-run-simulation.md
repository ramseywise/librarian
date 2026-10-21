---
title: Design Dry-Run Simulation
tags: [llm, pattern]
summary: Before building, attack a design's own unvalidated premises (an unrun experiment becomes the first component, and the spec needs a failure branch), then role-play nominal, malformed and plausible-wrong scenarios turn by turn, stop at the first blocker, record it as a finding and revise the spec; a dry run with no revisions was lucky or not adversarial.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/skills/proto-design/SKILL.md
  - data/raw/claude-docs/ai-project-template/docs/reviews/AIT-34-review.md
  - data/raw/repos/ai-project-template/.claude--docs--reviews--AIT-34-review.md
---

# Design Dry-Run Simulation

Stage 2 of the galactus `/proto-design` skill simulates a five-layer agent design
(prompt, context, harness, loop, graph, plus HITL) before any code exists.

## 2a — Attack the design's own premises

A design whose value depends on an unrun experiment is treating that experiment as a
foundation, and that is a risk. For each load-bearing premise:

1. **Name the experiment that would test it.** If none exists, the experiment is the
   design's **first component**, not a follow-up.
2. **Write the failure branch.** What does the design look like if the premise fails? The
   honest outcome may be "this is a finding, not a feature," and the spec must survive that
   answer. "A design with no failure branch has not been stressed — it has been assumed."
3. Log each unvalidated premise as a Grounding-layer finding.

**Evidence (diskoe).** A relational thesis gated a whole workstream and had never been run.
A feasibility doc's decisive A/B test was written but never executed, while downstream
design went ahead as if it had passed.

## 2b — Three scenarios, turn by turn

1. **Nominal.** What the requirement literally describes.
2. **Malformed.** Empty, truncated, wrong-typed or adversarial input. Prompt injection goes
   here for anything that reads external data.
3. **Plausible-wrong.** The agent produces confident, well-formed, *incorrect* output. This
   is the scenario that finds real bugs, because it is the failure the acceptance baseline
   is supposed to catch and usually doesn't.

Role-play each turn:

```
Turn N:
  Agent sees:    <what is actually in the window>
  Agent wants:   <the action it selects>
  Available?     <yes / NO — a finding>
  Result:        <what comes back, including failure>
  Verifier says: <pass / fail — by which deterministic check>
```

**Stop at the first point where the design cannot proceed.** That stopping point *is* the
finding. Do not repair it inline and carry on. Record it, start the next scenario, then
revise the spec and show the diff. **"A dry run that produces no revisions either got lucky
or was not adversarial enough — say which."**

## Around the simulation

- **Stage 0b puts numbers on it** before the layers are walked: rate, latency budget and who
  is waiting, cost per run and its ceiling, loop bound. "An accepted default is a resolved
  answer," and an unstated number silently assumes the demo case. A live caller is a third
  latency case, not a stricter version of a human watching a spinner.
- **Stage 3 closes with measurement.** Name what breaks first as usage grows, and hunt for
  silent staleness, because slow, wrong and error all announce themselves. Give success
  metrics as numbers ("p95 under 2s while faithfulness stays above 0.9"), and list
  deliberate deferrals so a reviewer can tell *chosen* simplifications from *overlooked*
  ones.
- At the harness layer, rollback is the part most often missing, and the acceptance baseline
  is the part most often faked. At the graph layer, "most 'we need a graph' is an
  overloaded verifier" (see [[Loop-to-Graph Escalation]]).

## Self-simulation is the weakest evidence

A plan that added new interview questions validated them with a dry run that was a
*manual simulation*: the author traced the skill text against a scenario they had also
read, evaluating their own questions — and every checkpoint passed, including the one the
plan named as where the design "bites hardest." The plan disclosed this honestly, and the
review credited the disclosure, but still flagged it: self-simulation covering the plan's
highest-likelihood risk needs one real run in a fresh session before the design counts as
validated. Prompt text has no automated test, so the dry run is the only functional check
it gets.

## See Also
- [[Scope-POC Design Interview]] — extends (the scoping stage this design consumes)
- [[Adversarial Plan War Game]] — alternative-to (attackers on a written plan rather than a role-played design)
- [[Harness Engineering]] — prerequisite-for
- [[Loop-to-Graph Escalation]] — extends
- [[Duplex Voice Breaks Discrete-Turn Assumptions]] — extends (the streaming-loop layer)
