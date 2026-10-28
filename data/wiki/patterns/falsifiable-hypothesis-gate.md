---
title: Falsifiable Hypothesis Gate
tags: [patterns, eval, pattern]
summary: A skill that refuses to add an experiment row unless the metric resolves to a registered signal, the claim is falsifiable, the due date is computed in review rounds rather than calendar days, the plane is named, and friction rows carry a pattern key — emitting the collection change first when the metric does not yet exist.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-19-telemetry-decision-log-and-hypothesis-skill.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-19_tooling-ledger_pattern-key-mapping.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-07-29_dashboard-tabs_experiments.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-07-31_LIB-59-ledger-metric-chart-mapping.md
  - data/raw/claude-docs/guacamayo/skills/track/SKILL.md
  - data/raw/claude-docs/guacamayo/docs/tooling-ledger.md
  - data/raw/repos/atlas/.claude--skills--debug--SKILL.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-19-pattern-key-backfill.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-19-pattern-key-backfill.md
---

# Falsifiable Hypothesis Gate

The guacamayo `/hypothesis` skill is the only sanctioned way to add a row to the tooling
ledger (the experiment table that drives workflow changes). It exists because the ledger,
written freehand, accumulated 49 rows that could never be scored
([[Signal Registry with Resolution States]]). The skill is a gate, not a form: it rejects
rows rather than warning about them.

## The gates

1. **Metric resolves to a registered signal.** The metric string is parsed and looked
   up in the signal registry. Unregistered → reject with the registry path. Registered
   but `needs-collection` → the skill **emits the collection change first** (the resolver
   or column that would make the metric observable) and only then the row, so the row
   never lands ahead of its instrument.
2. **Falsifiable.** The row must state what observation would mark it `failed`, not
   only what would confirm it. "Fewer bash antipatterns" is not a row;
   `count-drop:bash-antipatterns < 15 per session` is.
3. **Due date computed, not guessed.** Due is **two review (retro) rounds** from entry,
   not "14 days". Calendar due dates expired while no retro had happened to score them,
   producing 18 overdue rows on the audit day; round-based due dates expire only when a
   scoring opportunity has actually passed.
4. **Plane named.** Every row declares `plane ∈ work | metacognition | control` — is
   this about the work product, about the agent's self-monitoring, or about the loop's
   control machinery? Plane counts per dashboard strip expose when one plane is
   starved of experiments.
5. **Pattern key for friction rows.** Rows whose metric starts with `absence:` or
   `count-drop:` describe a friction that is supposed to stop recurring. If the friction
   is a *code-corpus* pattern (something a review sweep would flag — hardcoded URL,
   silent swallow), the row must carry a `pattern_key` that exists in the recurrence
   scanner's `PATTERNS` table; if the key is missing the skill runs the change text
   against the pattern regexes and proposes matches. *Workflow* friction (skill
   compliance, PR metadata, ledger hygiene) is accepted without a key — it has no corpus
   counterpart. The decision tree:

   ```
   if metric.startswith(("absence:", "count-drop:")):
       key = extract_pattern_key(change_text, metric_text)
       if key and key in PATTERNS:        pass
       elif key:                           REJECT  # key not in PATTERNS — add the signature first
       elif match_against_patterns(...):   PROMPT  # confirm or reject each match
       else:                               PROMPT  # code-corpus friction? YES → new signature first; NO → accept
   ```

   New signatures are added to `PATTERNS` only once the pattern appears in the review
   corpus with n ≥ 3 — adding a regex before the corpus shows it violates the
   derivation-from-corpus principle the scanner is built on.

## Metric vocabulary

Four typed prefixes, each with a scoring semantics:

| Prefix | Meaning | Scorable when |
|---|---|---|
| `absence:` | the named friction has not recurred | a hooklog/corpus resolver exists for the signature |
| `presence:` | the named behaviour is observed | a resolver exists; otherwise `unobservable` |
| `ratio:` | fraction over a denominator (`ratio:execution-sessions-with-skills`) | both numerator and denominator are store-backed |
| `count-drop:` | count falls below a threshold | the count is a continuous series |

`absence:` rows are the ones a timeseries dashboard cannot draw as a line — they are
step functions ("days since") and were excluded from chart annotation for that reason.

## Why a gate rather than a lint

A lint over the ledger reports debt; the debt had already reached 66% and nothing paid
it. A gate at entry keeps the denominator honest from now on and converts each rejected
row into either a collection task or a sharpened claim — the row's author is the one
person who knows what they meant.

## Why the gate exists — measured

Against the live ledger on 2026-08-19, **49 of 59 hypotheses could not be scored at all**
and 39 of 59 were unfalsifiable as written — they could never fail, so they could never
close, which is why the ledger only grew. Every unscorable row was written in good faith
by someone who never checked observability, so the check moved to design time in the
`track` skill. Two further rules from it:

- **Gate 2b — the signal is not already claimed.** If another open row already measures
  the signal, supersede it or fold in; never write a second row on the same signal.
- **Overdue sweep.** Calendar due dates written ~14 days out against a ~5-day retro cadence
  let 20 rows go past due, 18 sharing one stale deadline. Every overdue row gets a
  decision in the round it surfaces (graduate, fail, or rewrite), and a hypothesis with no
  due date is flagged — a row without one never comes up for audit.
- `absence:` claims fail most often: silence is also what a broken collector, an empty
  window and an unobservable event produce, so an absence claim needs a registered
  signal whose resolver returns a real zero.

## The same discipline in debugging (atlas `/debug`)

A debugging skill applies the gate at a smaller scale. Form **three or more** falsifiable
hypotheses before investigating any of them ("the loader returns an empty frame when the
env var is unset", not "something is wrong with the data"). Test them one change at a time,
in order of likelihood. The root cause is usually the *first* exception in a chained
traceback. Escalate to research → plan when the fix needs more than three files or three
fixes have failed, since that means the mental model is wrong. "Works but don't know why" is
not fixed.

## Backfilling the key (GUA-145)

When Gate 5 landed, only 2 of 40 active ledger rows carried a `pattern_key`, so the link from
experiment to signature was broken for every other row. The backfill had three rules:

- **New signatures must be corpus-derived.** Each must clear the recurrence threshold (n≥3)
  on its own phrasing, or be named directly by a ledger row. Every signature ships with one
  positive and one boundary non-match test.
- **Borderline signatures wait** until the corpus reaches n≥3.
- **Do not widen a regex to reach threshold.** If the live corpus shows false positives,
  tighten the regex instead.

One key absorbing 3 of 7 backfilled rows was flagged as a possible sign of an over-broad
regex, not as evidence of a hot pattern.

## See Also
- [[Signal Registry with Resolution States]] — prerequisite-for (the lookup this gate performs)
- [[Experiment Tracking Schemas]] — extends (typed metrics as run identity)
- [[Eval-Driven Development (EDD)]] — instance-of (the write-the-measure-first discipline, applied to workflow changes)
- [[Cross-Sweep Finding Fingerprint]] — extends (the recurrence corpus that `pattern_key` points into)
- [[Re-Derive, Never Re-Read]] — prerequisite-for (scored rows are verified by re-running, not reading)
- [[Telemetry Claim Verification Gate]] — extends
