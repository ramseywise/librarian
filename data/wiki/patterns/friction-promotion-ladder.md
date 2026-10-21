---
title: Friction Promotion Ladder
tags: [patterns, context-management, pattern]
summary: Where a recurring friction learning should live, ranked by always-on context cost — ledger row at N=1, conditional warn-hook at N=2, on-demand ref at N=3, always-on rules/CLAUDE.md text only as the exception — because a hook that fires 5% of the time costs ~20× less context than the same sentence loaded every session.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-09_friction-learning-loop_promotion-design.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-09_friction-learning-loop_funnel-ingest.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-09_friction-learning-loop_prior-art.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-09_friction-learning-loop_hook-emission.md
  - data/raw/claude-docs/guacamayo/skills/meta-retro/SKILL.md
  - data/raw/repos/guacamayo/README.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-09-friction-learning-loop.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-09-friction-learning-loop.md
---

# Friction Promotion Ladder

When an agent workflow hits the same friction twice — a shell gotcha, a branch-naming
slip, a forgotten lint mirror — the instinct is to write a sentence about it in
`CLAUDE.md`. The guacamayo friction-learning-loop research measured what that costs and
proposed a ladder instead.

## The budget being spent

- Always-on text in the audited setup: `CLAUDE.md` 255 lines / 14.9 KB + `rules/`
  48 lines / 2.8 KB = **17.7 KB loaded every session**. An audit judged ~15% of
  `CLAUDE.md` to be hard rules and ~85% design knowledge that only some sessions need.
- A pre-registered falsification study of a metacognition framework (prior-art review)
  found a 25k-character always-on overhead scored **0.30 vs 0.65** for a token-matched
  filler control on frontier tasks — always-on context is not free, it is actively
  harmful past a point. Treated as a hard constraint on promotion.
- Meanwhile the on-demand `refs/` directory held 26 files / 105 KB with **zero**
  always-on cost, and most repos' `CLAUDE.md` named none of them.

## Five promotion targets

| Target | Always-on cost | Fires when | Verifiable? | Reversible? |
|---|---|---|---|---|
| Warn-style hook (stderr, exit 0) | ~0 — stderr only when the condition fires | condition met during a tool call | yes — `log_pass`/`log_event` | yes — unregister in settings |
| `rules/` line | 100–300 words every session | session start | no — indirect nudge | yes |
| `CLAUDE.md` line | 200–400 words every session + skill entry | session start | no — weak signal | yes |
| `refs/` file | 1–5 KB, only when a `Refs:` line names it | explicit opt-in per repo | yes — coverage query | yes |
| Ledger row | ~0.5 KB, read at retro only | human reads it | yes — metric after ~2 rounds | yes |

The warn hook is the key row: its stderr is prepended to the *next* model message as
context, not history, and only when the condition fires. A friction that occurs in 5%
of sessions costs 5% of the hook's text via a hook and 100% via `CLAUDE.md` — the
research puts the ratio at ~20×.

## The ladder

1. **N = 1 — ledger row.** Record the hypothesis with a typed metric
   ([[Falsifiable Hypothesis Gate]]). Zero context cost; starts the observation clock.
2. **N = 2 — conditional injection.** If the friction is detectable from a tool call,
   add a warn hook; if it is a heuristic the model must hold, a `rules/` line is the
   fallback. Hooks are the default; always-on text is the exception.
3. **N = 3 — on-demand ref.** Knowledge that is domain-wide but not every-session goes
   in `refs/` and is pulled by a `Refs:` line in the skills or repos it applies to.
4. **Always-on `CLAUDE.md`** is reserved for conventions that *block* (git rules, issue
   tracking, strict gates) — things where a miss is expensive and the text is short.

The threshold N = 3 for "systemic" came from the corpus: a branch-sprawl defect was
promoted after its documented "third instance". A proposed ledger column, **promotion
target** (`hook | rule | ref | skip`), makes the intended landing spot explicit when a
row moves from `hypothesis` to `verified`.

## The four levers a retro may pull

The guacamayo self-improvement loop names exactly four levers a retro is allowed to change,
and ranks them by enforcement strength: **instructions** (`CLAUDE.md`, `rules/`, `refs/` —
the context budget), **capabilities** (skills, agents, MCP, and which model tier runs them),
**enforcement** (hooks, `settings.json`), and **persistence** (memory files, plan docs, the
wiki). The ordering rule is hooks > skills > rules: a learning graduates to the *strongest*
lever that can express it, because prose in a rules file is advice the model may skip and a
hook cannot be skipped. "A rule that only warns is not a control." Write authority narrows
in the opposite direction: memory files are loop-writable, skills and the ledger need
per-diff approval, and global hooks and settings are never written by the loop at all.

The ladder above and the lever ranking pull in different directions on purpose: the ladder
minimises always-on *context cost*, the lever ranking maximises *enforcement*. A warn hook
satisfies both, which is why it is the default landing spot.

## What the ladder needs from instrumentation

The hook substrate was found to be comprehensive in coverage but weak in signal: three
advisory hooks logged nothing on success, the pass-log rotated away recurrence history
after ~10 days, log writes were wrapped in `|| true`, and free-form context embedded
volatile paths that defeated grouping. The fixes — every hook logs a pass entry, a
structured `category` field per hook, per-signature counters instead of a rotating
log — are prerequisites for step 2 to be *verifiable* rather than assumed
(see [[Silence Reads as Clean]]).

## Plan-time decisions (friction learning-loop plan)

- **Fix the capture format before aggregating.** The growth entries being counted were
  outcome records ("did X"), not learnings ("X recurs because Y"). No aggregation can
  recover a learning that was never captured.
- **Count recurrence by named signature, not by category.** See
  [[Category Is a Bucket, Not a Recurrence Signature]].
- **Hooks propose, they do not act.** A hook may propose a promotion; a retro applies it.
- **Audit for obsolescence.** A verified rule can become obsolete. Each retro runs a
  stale-enforcement check, capped at the 5 oldest rows, so the review cost stays bounded.
- **Split the CLAUDE.md prefix last.** Changing always-on context mid-experiment would
  confound the loop's own measurements.
- **Keep warn hooks narrow.** When a hook matches an `except` line, check the handler
  body too, not just the line itself, or the hook fires on legitimate handlers.

## See Also
- [[Claude Code Hook Architecture]] — extends (warn hooks as the conditional injection point)
- [[Falsifiable Hypothesis Gate]] — prerequisite-for (the N = 1 row)
- [[Context Engineering]] — instance-of (always-on vs on-demand budget as a context decision)
- [[Friction Is Rework, Not Error Rate]] — prerequisite-for (what counts as the friction being promoted)
- [[REUSE/ADAPT/SKIP Asset Verdicts]] — extends (the ladder was assembled from five scouts' verdict tables)
- [[Retro Open-Hypotheses Loop]] — prerequisite-for (the retro that decides what to promote)
- [[Trend on Occurrence Date, Not Run Date]] — extends (rising-but-not-promotable gets the cheaper rung)
- [[Telemetry Claim Verification Gate]] — prerequisite-for (only verified claims climb)
- [[Stability-Graded Canon Writing]] — related (promoting findings to conventions after three implementations)
- [[Category Is a Bucket, Not a Recurrence Signature]] — extends (why category counts never reached N=3)
