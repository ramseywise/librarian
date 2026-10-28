---
title: Strict Parsers for Alarm Config
tags: [patterns, infra, pattern]
summary: "Every config parser in an alerting tool must refuse a value it does not understand rather than fall back — a zero threshold makes `slice(0,0).every()` vacuously true and fires every run, a negative one makes the alarm unsatisfiable, an unknown `--ack` id silently does nothing, and `yes` reads as false — and the tool's exit codes must separate 'alarm fired' (1) from 'the check itself failed' (2)."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/reviews/2026-09-16-dis276-pipeline-health-check.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-16-dis276-pipeline-health-check.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-16-dis276-pipeline-health-check.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-16-dis276-pipeline-health-check.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-16-dis276-pipeline-health-check.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-20-dis343-venue-open-facts.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-20-dis343-venue-open-facts.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-20-dis343-venue-open-facts.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-20-dis343-venue-open-facts.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-20-dis343-venue-open-facts.md
---

# Strict Parsers for Alarm Config

A pipeline health-check CLI in akira was reviewed with four separate findings that turned out
to share one root cause: **every parser fell back silently instead of refusing.** In an alerting
tool, silent fallback is the very defect class the tool exists to end, so all four were fixed
together.

## How each lenient parser inverted or muted an alarm

| Input | Lenient behaviour | Effect |
|---|---|---|
| streak threshold `0` | accepted (any finite number) | `runs.slice(0, 0).every(...)` is vacuously true, so the alarm fires on **every** run |
| streak threshold `-1` | accepted | `slice(0, -1)` drops the last element instead |
| supply threshold `-1` | accepted | `supply < -1` is unsatisfiable, so the alarm can **never** fire |
| `--ack qc-not-runnin` (typo) | `Set<string>` cast to `Set<AlarmId>` with no membership check | matches nothing; operator sees exit 0 and believes the override worked |
| `CRON_ENABLED=yes` | only `1`/`true` are true | reads false, so the missed-schedule alarm is never evaluated and the check reports healthy while the cron is dead |

The vacuous-truth case is the same logic as [[Vacuous Check Turns Backwards on Policy Change]]:
`every()` over an empty population passes.

## The fixes

- **Refuse, naming the variable and value.** `requirePositiveInt` exits non-zero with the env
  name and the bad value. Booleans accept a small explicit set both ways
  (`1/true/yes/on`, `0/false/no/off`, case-insensitive) and refuse anything else.
- **Validate membership against a runtime list.** Declare `const ALARM_IDS = [...] as const`
  and derive `type AlarmId = (typeof ALARM_IDS)[number]`, so the type and the validator cannot
  drift; an unknown id exits listing the valid ones.
- **Separate exit codes.** The CLI exited 1 for a blocking alarm *and* from its `.catch`
  handler, so a scheduled caller could not tell a real alarm from a connection timeout. The
  contract became **0 = clean or warn-only, 1 = blocking alarm, 2 = the check itself failed**,
  documented in the file header. See [[A Check Must Say Why It Could Not Check]].
- **Make override semantics match the word.** `--ack` was merged with the env value although
  the plan called it an override; it was changed to replace it. (Merging fails toward noise, not
  silence, so this was only a suggestion.)
- **Test each parser's invalid cases** with an `it.each(['0', '-3', 'abc'])` table; none of the
  parsers had tests, so a refactor dropping a validation would stay green.

## The same class elsewhere

A corpus-generation CLI in the same repo took `--limit` with `Number(arg)`: `Number('abc')` is
`NaN`, which sampled nothing and exited cleanly, and the value was unclamped, so a large number
ran unbounded billed calls with no spend ledger. The rule generalises to any CLI whose flags
gate cost or alerting: parse into a validated domain type at the edge, and treat "could not
parse" as a failure, never as a default.

## See Also
- [[Known-Gap Alarms Ship as Warn]] — extends (severity design for the same health check)
- [[Vacuous Check Turns Backwards on Policy Change]] — related (vacuous truth over an empty slice)
- [[A Check Must Say Why It Could Not Check]] — extends (exit 2 = the check could not run)
- [[Silent Failure Catalogue]] — instance-of
