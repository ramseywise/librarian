---
title: Test-Gated Auto-Fix with Per-Hunk Revert
tags: [patterns, llm, pattern]
summary: "An agent may apply review findings itself only if the repo has a working test harness. It tiers each finding by blast radius, applies only low-radius fixes, one at a time, runs the tests after each, and reverts the hunk on failure. It runs in the main session, never in a subagent, and never commits."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-18-akira-global-port.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-18-akira-global-port.md
  - data/raw/repos/playground/src--agents--akira--findings--findings-20260607.md
---

# Test-Gated Auto-Fix with Per-Hunk Revert

The design of akira's `dao` mode, made when the akira review skill was ported to a
global Claude Code skill. Its other modes (`scan`, `wander`) only read and report. `dao`
is the one that changes code, and the design is a list of conditions under which that is
allowed.

## Split by mutation, not by mode

One `/akira` skill covers several modes, but they do not run the same way:

| Mode | Work | Runs as |
|---|---|---|
| scan | parallel read-only judgment → ranked findings | subagent |
| wander | read the diff, ask 3–5 sharp questions | subagent |
| dao | triage → apply → test → revert, then sync docs | **main-session skill logic** |

Read-only judgment fans out well, because subagents return text and touch nothing. A
loop that **edits the tree, runs tests and reverts** cannot be handed to a subagent
safely. It needs one owner of the working tree, and the loop's state must survive
between steps. The rule: parallelise judgment and serialise mutation.

## The guardrails

1. **Test gate.** Probe for a working harness first (`make test`, `pytest`, `npm test`).
   **No harness means no applies.** Every finding is surfaced and the report says why.
   A repo without tests cannot tell a fix from a regression, so the agent may not
   mutate it. The acceptance test checks this directly: in a test-less repo, `dao`
   refuses.
2. **Blast-radius tiers.** An LLM triage step tiers each finding. *Nit* and
   *mechanical* findings are auto-apply candidates. *Logic* and *behavioral* findings
   are surface-only and never applied, whatever the tests say.
3. **One hunk at a time.** Apply a fix, run the tests, keep it on green, revert that
   hunk on red (`git checkout` / `stash`), then move to the next. Batching fixes would
   make a red run unattributable.
4. **Working tree only, never commit.** The changes stay uncommitted, so the human's
   review-before-commit step stays intact. The report leads with what was applied,
   reverted, surfaced and changed in docs.
5. **Amend the rule, don't route around it.** `dao` also updates human-facing docs,
   which the global docs rule says agents may only flag. Instead of a silent exception,
   the rule file was amended first (phase 0) with a named carve-out: working tree only,
   never committed, and following a doc-style ref when one exists.

## What an early run showed (playground, 2026-06-07)

A five-subagent scan of a support-agent branch produced 12 findings (3 high, 8 medium,
1 low). The result: 3 applied, 6 open, 3 dismissed. Two things are worth keeping:

- **Doc drift was the dominant class.** 7 of 12 findings came from the docs reporter, for
  example a CLAUDE.md overview table that disagreed with `src/README.md` about nesting
  and which modules exist, or a "last updated" date in the future. The schema reporter's
  findings were the riskier kind: a per-agent output model whose field name and source
  type differed from the shared response contract that downstream callers read.
- **Three docs-only fixes were reverted as "tests broke after applying change".** A
  CLAUDE.md edit cannot break a test suite. So the red run almost certainly came from a
  failure that was already there, and the per-hunk gate blamed it on the hunk. **Take a
  green baseline before the first apply.** If the baseline is red, the gate cannot
  attribute anything, and the run should report that instead of reverting fixes.
- Dismissals carried a reason class: *intentional* (a design that skips a CRAG
  grade/rewrite loop on purpose) or *unconfirmed* (a cited line that does not exist,
  probably a scan truncation artifact).

## Acceptance criteria worth copying

- In a test-backed repo, `dao` applies at least one low-radius fix, **reverts a
  deliberately bad fix when the tests fail**, and commits nothing.
- In a test-less repo, it refuses to mutate and only surfaces findings.
- The triage step tiers a seeded nit and a seeded logic finding correctly.

## See Also
- [[Size the Gate to the Blast Radius]] — extends (blast radius decides apply versus surface)
- [[Reversibility Cliff]] — related (the autonomy boundary sits where effects stop being undoable; uncommitted working-tree edits stay undoable)
- [[Cost-Leveled Review Ladder]] — related (the read-only review levels this complements)
- [[Wander — Question-Generating Review Agent]] — related (the read-only sibling mode)
- [[Documentation Boundary — Machine vs Human Docs]] — extends (the amended flag-only rule)
