---
title: Due-vs-Acked Trigger Counters
tags: [infra, meta, pattern]
summary: Hand a trigger across session or process boundaries as a pair of cumulative file counters — a dumb producer bumps "due", the actor bumps "acked" only after verifying the action landed — because a bare cumulative count is always true and a prose flag dies at the boundary.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/skills/meta-grow/SKILL.md
  - data/raw/claude-docs/guacamayo/skills/meta-dream/SKILL.md
  - data/raw/claude-docs/guacamayo/skills/grow/SKILL.md
  - data/raw/claude-docs/guacamayo/skills/meta-wake/SKILL.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-19-metacognition-automation.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-19-metacognition-automation.md
---

# Due-vs-Acked Trigger Counters

guacamayo's identity lifecycle needs a weekly-ish tooling retro to fire reliably across
sessions. The mechanism that finally worked is a pair of counters in a state file.

## The bug it replaced: a trigger relayed as prose

The capture skill used to set `retro-worthy: true` in its *prose* signal summary and leave
the session-close skill to act. But the close skill reads files, not transcripts — so the
flag crossed a session boundary as text and **was lost every time**. Meanwhile the insights
step fired reliably precisely because the capture skill spawned it *itself*.

## Mechanism

- **Producer only counts.** A PreCompact hook bumps `compacts`, `grows_due`,
  `insights_due`, `retro_due` in `cascade-state.json`. Compaction is the cadence signal: it
  fires on context pressure, so it tracks real work rather than wall-clock. Hooks are shell,
  not agent contexts — they cannot spawn agents, so acting is a skill's job.
- **Actor compares due vs acked.** Fire when `retro_due > (retro_acked // 0)` — never
  `retro_due >= 1`. The counter is cumulative, so an unacked bare count is *always* true and
  therefore never actionable.
- **Ack only after verifying it landed.** Spawn synchronously, then check for evidence (a
  ledger header dated today). Only then set `retro_acked = retro_due` (write-to-tmp, then
  `mv`). If nothing landed, leave the counter so the next session retries. The same rule
  applies to every tier: after acting, bump the matching `*_acked` key.
- **Idempotent fallback.** The close skill re-reads the file and skips if
  `retro_due == retro_acked` — the earlier skill already handled it.

## Cadence is not the only trigger

Two independent triggers sit alongside the counter, because cadence-overdue ≠
content-overdue:

- **Content-driven:** more than 3 ledger hypotheses overdue by 14+ days triggers the retro
  regardless of compaction count.
- **Change-driven:** a diff touching hooks, skills, rules or settings during the session
  triggers it regardless of cascade state — the capture step may have run before the
  tooling work happened.
- Plus a wall-clock floor: last retro ≥7 days ago.

## Reachable in code, not yet reached in data

The metacognition automation plan wired an event-driven loop with one human gate. Its spawns
run from cron, not hooks, so they cost no tokens per session. Auditing it showed the retro
auto-spawn was *reachable in code but not yet reached in data*: its threshold needed 27
compactions, and the cascade state showed 7. A trigger that has never fired is not evidence
that it works. Report the distance to threshold alongside the rule.

## See Also
- [[Re-Derive, Never Re-Read]] — prerequisite-for (the ack depends on verifying, not trusting the agent report)
- [[Identity Memory: Revision vs Accretion]] — extends (the lifecycle these counters drive)
- [[Puffin Consciousness Development Skills]] — instance-of
- [[Append-Only Log Writer Invariants]] — extends
