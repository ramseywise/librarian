---
title: Evolve Loop
tags: [llm, agents, infra, pattern]
summary: "A slow loop pointed at a fast one that rewrites files rather than weights — four edit targets, a 5–10 run cadence, and the anti-busywork rule that makes 'no change needed' a first-class success."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--04-loop--evolve-loop.md
---

# Evolve Loop

The **practitioner-scale** version of capability level 4 in [[Loop Engineering]].
[[Recursive Self-Improvement]] covers the frontier version. *Same shape, different altitude:
here the thing being rewritten is a config file, not a model.*

## The Definition

> **An evolve loop is a loop with a second, slower loop pointed at it. The fast loop does the
> work. The slow loop edits the fast loop.**

The critical distinction from RSI as usually discussed: **it does not retrain weights, it
rewrites files.** What improves is the *scaffolding* — the contract, the state, the triggers,
the procedure. **The model is fixed.** That is why it is available to any practitioner today.

## Cadence and Inputs

The slow loop runs roughly **every 5–10 runs of the fast loop** — often enough to catch drift,
rare enough that there is real evidence to read. A dedicated session reviews three inputs:

1. **The loop's configuration** — its contract, goals, boundaries. *What did we say success
   was?*
2. **State and logs** — what the agent believed versus what actually happened. *Where did the
   model of the world diverge from the world?*
3. **Raw conversation history** — where the agent flailed. **This is the richest input: the
   thrash itself reveals cheap structural fixes that no metric surfaces.**

The third input is why an evolve loop needs trace retention, not just metrics — see
[[Observability and Runtime Patterns]].

## The Four Edit Targets

| Target | What gets rewritten | Symptom that triggers it |
|---|---|---|
| **Contract** | The definition of success | Loop "succeeds" on runs you'd call failures |
| **State** | Stale or wrong entries | Agent acts on facts that expired |
| **Trigger logic** | When the loop wakes | Wakes constantly, finds nothing to do |
| **SOP steps** | Mechanical procedure | Same manual correction, every run |

**Worked example (a support triage loop).** An expensive trigger was waking the agent
repeatedly to find no work. The evolve run wrote a JavaScript trigger script: fetch Intercom
updates from the last 30 minutes, wake the agent only when real work exists. **No human
designed that fix** — the slow loop read the logs, saw the empty wakeups, and rewrote its own
trigger.

Note the shape: the improvement was **structural and deterministic, not a better prompt.** That
is the recurring signature of a working evolve loop, and it matches the bilevel finding in
[[Recursive Self-Improvement]] that parameter tuning without mechanism change yields nothing.

## The Anti-Busywork Rule

The most important guardrail, and it came out of a production failure:

> **Agents default to doing something even when nothing needs doing.**

An evolve session asked *"what should change?"* will **always** answer. It will manufacture
plausible edits to justify having run, and those edits degrade a working loop.

**The fix is explicit permission to change nothing** — make `no change needed` a first-class
success outcome, stated in the evolve session's contract, not an implicit non-event.

> If "no change" is silent failure, you have built a machine that damages itself on a schedule.

This generalizes past evolve loops to **any reviewer or critic agent**:

> *A reviewer that cannot return "clean" is a reviewer that invents findings.*

Which is the false-positive economics of [[Verification Loops]] running in the other direction:
there the danger is a gate that fires too often and gets clicked through; here it is a reviewer
that fires too often and gets *obeyed*.

## Failure Modes

1. **Invented improvements** — changes manufactured to justify the run. Countered by the
   anti-busywork rule.
2. **State rot** — unmaintained state poisons every subsequent evolve run, because state is one
   of the three inputs. **Rot compounds: bad state → bad diagnosis → worse state.**
3. **Compounding errors** — one bad evolve run degrades all future runs, since the next session
   reads a config that is already wrong and reasons forward from it.
4. **Scope limit** — an evolve loop can improve a loop but **cannot decide whether the loop
   should exist at all.** That judgment stays human. *A well-tuned loop doing useless work will
   tune itself further into uselessness.*

Failure 4 is the boundary of the whole technique, and it is the same boundary as
[[Iterative Harness Simplification]]: a mechanism that optimizes within a frame cannot
interrogate the frame.

**Human review of early diffs is essential.** The evolve loop earns autonomy the same way every
other loop does — start at rung 1 of the [[Loop Autonomy Ladder]] with a human approving each
config rewrite, and climb only once **the diffs are boring**.

## Design Checklist

- [ ] Is the evolve cadence tied to *runs* (5–10) rather than wall-clock time?
- [ ] Does the evolve contract explicitly bless "no change needed" as success?
- [ ] Is state pruned/expired as a maintained step, or does it just accumulate?
- [ ] Are evolve diffs reviewed by a human, and **are they getting more boring over time**?
- [ ] Who decides whether this loop should exist — and when do they revisit it?

## See Also
- [[Loop Engineering]] — part-of
- [[Recursive Self-Improvement]] — extends
- [[Loop Autonomy Ladder]] — depends-on
- [[Iterative Harness Simplification]] — complements
- [[Verification Loops]] — complements
