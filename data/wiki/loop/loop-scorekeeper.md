---
title: Loop Scorekeeper
tags: [loop, eval, pattern]
summary: "The scorekeeper (verifier/grader) decides whether a loop's cheap repeated motion becomes value or slop — it must be objective, automatic, fast, clear and hard to fake, live outside the loop's write scope, anchor on deterministic checks, and be written before the loop's first pass."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--04-loop-engineering--notes--03-the-scorekeeper.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--04-loop-engineering--notes--09-failure-modes-and-guardrails.md
---

# Loop Scorekeeper

Capability level 2 of [[Loop Engineering]]. In a loop the generator runs cheaply, over and over;
the **scorekeeper** — test suite, build, linter, checklist, or rubric another agent grades
against — turns each pass into a result the loop can read. Without it the loop cannot tell
progress from noise.

> **Build the verifier before you scale the generator.** A generator that can't check itself
> just produces plausible-looking work faster.

Anthropic's long-running-agent example makes the point empirically: results improved once the
agent had browser automation and was told to test features as a human would — verification,
not a better prompt, made the difference. The cost is real (latency and spend per run), and
worth paying whenever quality matters more than speed.

## Five traits

| Trait | Why |
|---|---|
| **Objective** | Same work, same result |
| **Automatic** | One command or CI trigger |
| **Fast** | Cheap enough to run every pass |
| **Clear** | One unambiguous score |
| **Hard to fake** | A loop that can lower the bar will take the easiest path to green |

Defences for the fifth: **held-out checks** run only at the final gate (stops overfitting to
visible tests); **tamper-proof location** (another repo, protected CI job, read-only paths);
**auditable artifacts** (immutable or diffable logs); **watch the trend** — a sudden jump is a
reason to look, not celebrate.

## The write boundary

> An agent that can edit its own evaluator does not have a verifier; it has a negotiation.

In the `autoresearch` example the agent writes the training file, nobody writes the evaluation
file, and the human writes the contract (`program.md`) — see [[Recursive Self-Improvement]].
Enforce the boundary **structurally** (file permissions, a write-blocking hook, a separate repo),
not by prompt instruction: instructions are suggestions, permissions are rules
([[Execution Boundaries and Guardrails]]).

## Deterministic first, judgement above the floor

| Layer | Example | Gameable? |
|---|---|---|
| Deterministic | `pytest`, `tsc`, link checker, "diff touches only `src/auth/`" | Only by editing the check — so protect it |
| Rubric + separate model | "Does the PR description explain *why*?" against written criteria | Somewhat; needs a fixed rubric and a grader that isn't the maker |
| Human | Taste, architecture, "should this exist?" | No, but slow and unscalable |

If "done" can only be described as "looks right", there is no scorekeeper yet — stay at rung 1
of the [[Loop Autonomy Ladder]] until you can write one.

## Maker and checker

The maker trusts its own output. Split roles: the **checker** is a fresh agent with its own,
stricter instructions, often a stronger model, and **without the maker's history**. The pattern
appears as implementer/verifier sub-agents, LangChain's `RubricMiddleware` / `after_agent`
grader, and ADK's `RefinerAgent`/`CriticAgent`. **A checker must be allowed to return
"clean"** — a reviewer that cannot pass the work will invent findings (the same anti-busywork
rule protects the [[Evolve Loop]]).

## The two ratchet rules

What makes a repeating engine safe to leave alone:

1. **The score only goes up.** A change that lowers the score is undone automatically.
2. **Fix breaks before adding more.** New work on a broken base compounds damage.

With a worktree per try and a commit per green pass, rollback is a `git reset` or
`git worktree remove`.

## Write it first — checklist

- [ ] Tests or rubric written before the loop's first pass
- [ ] Scoring runs automatically (one command / CI job)
- [ ] Some checks held out for the final gate
- [ ] Scoring logic outside the loop's write scope
- [ ] Checker is a different agent from the maker, and can return "clean"
- [ ] Score trends visible across runs

The harness-side machinery (termination checks, asymmetric QA, loop detection, retry taxonomy)
is in [[Verification Loops]]; this page is *what* to measure.

## See Also
- [[Loop Engineering]] — extends
- [[Verification Loops]] — extends
- [[Recursive Self-Improvement]] — prerequisite-for
- [[Loop Termination Design]] — prerequisite-for
- [[Multi-Agent Failure Modes at Scale]] — prerequisite-for
