---
title: Eval Suite Maintenance
tags: [eval, llm, agents, pattern]
summary: "Fix the evaluation system before changing the agent — a dropped score is a claim about the eval as much as about the agent, and a suite everyone passes is saturated rather than solved."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--eval-harness.md
---

# Eval Suite Maintenance

An eval suite is a living artifact with its own failure modes. Two rules carry most of the
weight, and both cut against the instinctive response.

## Rule 1 — Fix the evaluation system before changing the agent

> When an agent's score drops, do not immediately assume the agent has become worse.

The evaluation system may be producing a noisy or incorrect signal. Common causes:

- Infrastructure failures — out-of-memory crashes, timeouts
- **Grader bugs** marking correct outputs as failures
- Test cases that no longer reflect production usage
- Aggregate metrics hiding a regression in one task category

**Debugging order — strictly:**

1. Check infrastructure errors, timeouts, and resource limits.
2. Inspect failed traces and grader decisions.
3. Check whether failure is **concentrated in one task category**.
4. *Only then* modify the model, prompt, tools, or agent logic.

Step 4 is the one everyone starts with, and starting there means tuning a real agent against
a broken measurement — which reliably makes the agent worse while the number improves. Both
LangChain's readiness checklist and OpenAI's grading guidance make the same point
independently: rule out infrastructure and grading-logic bugs first.

## Rule 2 — Read traces, not only scores

> Aggregate metrics tell you that performance changed; they rarely tell you why.

Inspecting complete trajectories is what surfaces:

- Grader bugs
- Unexpected tool use
- Environment contamination
- **Successful outcomes reached through unsafe behavior**
- Failures hidden by misleading aggregate scores

Manually reviewed traces do double duty — they create ground truth *and* align automated
evaluators with human judgment.

## Building the suite: eight rules

1. **Define success before collecting more data.**
2. **Start small, with real failures** — 20–50 real user-reported failure cases, manually
   reviewed, beats a large noisy benchmark.
3. **Include negative cases, not just positive ones.** Positive examples test capability;
   negative examples test **restraint**. *Without negative cases, the system can improve
   recall by simply taking the same action too often* — the eval rewards a trigger-happy
   agent.
4. **Write unambiguous tasks with reference solutions.** The test: *two domain experts would
   independently reach the same pass/fail verdict.* Ambiguity in task specs becomes noise in
   metrics, and the same applies to LLM grader rubrics.
5. **Reset the environment for every trial** — otherwise one trial affects the next and an
   environment problem looks like an agent failure. Non-negotiable once you run k trials
   ([[Eval Non-Determinism]]).
6. **Choose the simplest reliable grader** — code where correctness is deterministic, LLM
   where judgment is required, human for ambiguous cases and judge calibration.
7. **Read traces, not only scores** (rule 2 above).
8. **Keep expanding the frontier** with new use cases, edge cases, and failure cases.

## Saturation is not success

> When pass rates approach 100%, the suite may be **saturated**. That does not mean the
> agent solved the real problem — it may mean the current tasks no longer expose its
> capability boundary.

The structural answer is **two suites running side by side**:

| Suite | Contents | Target |
|---|---|---|
| **Regression** | Known failures, now fixed | ~100% pass |
| **Rolling discovery** | New production failures | Low pass — that is the point |

A regression suite at 100% and no discovery set means you have stopped learning anything
about the agent. This is the [[Eval Harness Anatomy]] capability→regression promotion
running continuously rather than once.

## The maintenance loop

```
Collect real failures
        ↓
Define clear success criteria
        ↓
Build isolated tasks
        ↓
Run repeated trials
        ↓
Grade with code, models, and humans
        ↓
Inspect traces
        ↓
Add new failures and harder cases
```

## See Also
- [[Context Failure Modes]] <!-- auto-linked -->
- [[Manual Review as Eval Bootstrap]] <!-- auto-linked -->
- [[Eval vs Test Distinction]] <!-- auto-linked -->
- [[Eval Ladder]] <!-- auto-linked -->
- [[Eval Harness Anatomy]] — extends (maintaining what that page defines)
- [[Eval Non-Determinism]] — depends-on (environment reset is what makes k trials comparable)
- [[Eval Maturity Ladder]] — complements (eval rows seeded from observed failures is the level-3 property)
- [[Golden Set Mechanics]] — complements (curation rules for the rows themselves)
- [[Online Eval Sampling]] — extends (where new discovery rows come from in production)
- [[Eval-Driven Development (EDD)]] — complements
