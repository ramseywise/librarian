---
title: Eval Ladder
tags: [eval, llm, planning]
summary: A four-rung progression — manual review, golden-set grading, LLM-judge, user feedback — sequenced so each rung's failures supply the next rung's test cases, with an explicit "most POCs reach rung 2–3 and that's sufficient" stopping point.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/eval-approaches.md
---

# Eval Ladder

Evaluation approaches ordered as a **progression tied to project maturity**, not a menu.
The eval approach is chosen early — during discovery/scoping — because it determines what
data you must collect from day one.

| Rung | Phase | Approach | What it buys |
|---|---|---|---|
| 1 | Week 1 (prototype) | [[Manual Review as Eval Bootstrap]] | Intuition about what "good" means |
| 2 | Week 2–3 (building) | [[Golden Set Mechanics]] via `make eval-heuristic` | Automated regression catching |
| 3 | Week 4+ (refining) | [[LLM-as-Judge Evaluation]] + `make eval-gate` in CI | Subjective quality criteria |
| 4 | Post-deploy | [[User Feedback Loops]] | Real signal; failures expand the golden set |

## The compounding property

Each rung's output is the next rung's input, which is what makes this a ladder rather than
four independent options:

- Manual review over 10–20 real queries surfaces **failure patterns** → those patterns
  become the first golden QA pairs.
- Golden-set failures reveal what heuristic grading **can't** express (tone,
  completeness) → those become LLM-judge rubric criteria.
- Deployed thumbs-down cases are **real failures** → they expand the golden set, feeding
  rung 2 permanently.

Skipping a rung means inventing its output instead of harvesting it. A golden set written
without rung 1 encodes what you *imagine* users ask.

## Where to stop

> *"Most DSSG POCs reach step 2–3 by demo day — that's sufficient to prove the system
> works reliably."*

The ladder is not an obligation to reach rung 4. Rung 4 is unavailable pre-deployment by
construction, and rung 3 costs money per run. The stopping rule mirrors the sizing advice
in [[Golden Set Mechanics]] — the CI-scale numbers arrive *after* launch, fed by
production, not at genesis.

## Decision shortcut

| Question | Answer → Approach |
|---|---|
| Can you define "correct" objectively? | Yes → golden-set grading |
| Is quality subjective (tone, style, completeness)? | Yes → LLM-as-judge |
| Do you have real users yet? | Yes → user feedback loops |
| Is this still a prototype? | Yes → manual review, for now |

Running alongside all four: [[Heuristic Pipeline Metrics]] — latency, error rate, token
usage. These measure operational health, never answer quality, and complement rather than
replace any rung.

## See Also
- [[Skill Eval Pipeline (Blind Comparison + Grading)]] <!-- auto-linked -->
- [[Eval vs Test Distinction]] <!-- auto-linked -->
- [[Skill Pipeline Dryrun Testing]] <!-- auto-linked -->
- [[ADK Eval Guide]] <!-- auto-linked -->
- [[Golden Set Mechanics]] — extends (rung 2, with full case-shape mechanics)
- [[Manual Review as Eval Bootstrap]] — part-of
- [[LLM-as-Judge Evaluation]] — part-of
- [[User Feedback Loops]] — part-of
- [[Heuristic Pipeline Metrics]] — complements
- [[Complexity Floor]] — related (eval maturity tracks project tier)
- [[Six-Pillar Agent Engineering Assessment]] — extends (the eval pillar is one of six scored the same way)
- [[Verification Loops]] — complements (evals as the harness gate the agent cannot skip)
- [[Harness Maturity and Failure Modes]] — depends-on (no binary eval is failure mode 5)
- [[Iterative Harness Simplification]] — depends-on (subtraction is unmeasurable without a binary eval)
