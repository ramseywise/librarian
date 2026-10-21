---
title: Dispatcher Carries the Skill Body
tags: [llm, deep-agents, pattern]
summary: "disable-model-invocation hides a skill from every model instance, including the subagents an orchestration script spawns. A dispatcher that keeps those flags set must build each agent prompt itself: the SKILL.md body read fresh at dispatch time, the target substituted for $ARGUMENTS, and the tool grant taken from frontmatter. Its first acceptance test dispatches one stage by hand and diffs the ledger."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-15-gal-27-band-contract-hitl-gates.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-15-gal-27-band-contract-hitl-gates.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-15-fast-loop-borrowables.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-15-fast-loop-borrowables.md
---

# Dispatcher Carries the Skill Body

From galactus, building a scripted dispatcher (Claude Code's `Workflow` orchestration) to
route between pipeline stages. The scoping decision was "the script dispatches, the model
does not self-trigger", with all the pipeline skills keeping
`disable-model-invocation: true`. Taken literally, that decision cannot be implemented.

## Why the flag blocks the dispatcher

`disable-model-invocation: true` does more than stop auto-invocation. **It removes the
skill's description from the system prompt entirely**, so the model cannot see that the
skill exists unless a user types `/skill-name`. A workflow script dispatches
**subagents**, and those are model instances too. A subagent told "run `/proto-research`"
cannot see the skill for the same reason the main loop cannot. The flag is not a
convention the dispatcher can route around. It removes the skill from every model
instance, including the ones the dispatcher spawns.

So "keep the flags" and "the script dispatches the stages" are mutually exclusive **if
dispatch means invoking skills by name.** The intent, that the model must never
self-trigger the pipeline, was sound. The resolution changed what *dispatch* means rather
than unsetting the flags.

## The dispatcher composes the prompt

`SKILL.md` bodies are plain markdown and readable with `Read`. The dispatched agent is
given the body as its instructions. A failure-pass review then showed that handing over
the raw body is **not** dispatch, because three things a real skill invocation provides
are missing:

| Requirement | What the runtime does | Dispatcher must |
|---|---|---|
| `$ARGUMENTS` | **not expanded**: the agent call takes a plain prompt string | substitute the target explicitly, or the agent reads a literal unexpanded token |
| `allowed-tools` | **not carried**: the agent gets the dispatcher's grant | read the frontmatter line and grant those tools |
| freshness | a body inlined into the script drifts when the skill is edited | `Read` the `SKILL.md` **at dispatch time**, never inline it |

Nested dispatch is available but bounded (one level of workflow nesting).

## First acceptance test: dispatch one stage, diff the ledger

Before attempting a full multi-stage run, dispatch **one** stage by hand against a real
plan doc and diff the transition ledger. An agent that reports success while the ledger
is unchanged is exactly the failure this catches. **An empty ledger looks identical to a
skipped stage.**

## Assert the hook that will run, not that a hook exists

The dispatcher writes `Status:` and depends on the ledger, so it asserts its execution
root. A failure pass sharpened what that assertion means. A registration check passes
just as happily against an *older* hook. That is the exact earlier failure: two vintages
of the hook both registered, and the one that ran had no ledger. So the assertion became
"**the hook that will run emits transitions**" (`grep -q log_transition` on the resolved
path), not "a hook is registered here" (see [[Vendored Hooks Resolve to the Global Copy]]).

## Rejected alternative

Unset the flags on the stage skills and invoke them by name. Rejected because it would
make the whole stateful pipeline model-reachable in every session. The only skills the
model may reach for on its own are cheap, read-only ones that never touch `Status:`, and
the stage skills are none of those. A related audit found the flags were spread unevenly:
two of seven stage skills were *already* model-reachable. That gap was recorded for a
follow-up rather than closed inside a plan whose non-goals forbade frontmatter edits.

## See Also
- [[Skill Discovery Failure Modes]] — extends (disable-model-invocation reaches dispatched subagents too)
- [[Capability vs Phase Skills]] — extends (why phase skills carry the flag and capability skills do not)
- [[Auditable Track Router]] — alternative-to (naming uninvocable skills as plan steps instead of dispatching them)
- [[Vendored Hooks Resolve to the Global Copy]] — extends
- [[Hoist Irreversible Decisions to the Attended Band]] — extends (the band pipeline this dispatcher drives)
