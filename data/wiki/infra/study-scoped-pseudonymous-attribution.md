---
title: Study-Scoped Pseudonymous Attribution
tags: [infra, eval, decision]
summary: When an evaluation study needs to follow named testers across sessions, attribute only an explicitly enrolled, time-bounded study via a random per-account pseudonym on the parent record — not a user_id on all telemetry — and treat the pseudonym as personal data whose erasure must delete every linked row, replay copy and export, not just the mapping.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-09-16-dsk-309-tester-journey-attribution.md
  - data/raw/claude-docs/akira/docs/research/2026-09-16-dsk-309-tester-journey-attribution.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-16-dsk-309-tester-journey-attribution.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dsk-309-tester-journey-attribution.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dsk-309-tester-journey-attribution.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dsk-309-tester-journey-attribution.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dsk-309-tester-journey-attribution.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dsk-309-tester-journey-attribution.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis310-labelled-session-export.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis310-labelled-session-export.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis310-labelled-session-export.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis310-labelled-session-export.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis310-labelled-session-export.md
---

# Study-Scoped Pseudonymous Attribution

From research in diskoe (2026-09-16) on attributing tester journeys across sessions for a
pre-beta study, in a recommender whose telemetry deliberately had result-set identity but
no account, session or tester key.

## Name the reader before adding identity

The identity need was a **study** requirement (two testers' labelled runs), not a **ranker**
requirement. The downstream benchmark needed explicit rater IDs on judgments, not browsing
identity. Neither justified tracking every signed-in account — and the absence of a user ID
alone also doesn't prove the rest of the telemetry is legally anonymous.

## Options considered

| Option | Cross-session study? | Verdict |
|---|---|---|
| Nullable `user_id` on every result set | Yes | Reject — collects far beyond the reader's need |
| **Random per-account study pseudonym**, mapping held server-side | Yes, within one bounded study | **Recommend**, explicit enrolment only; re-enrolment after withdrawal gets a new pseudonym |
| Cohort flag | No | Useful for aggregate traffic separation only |
| Session-only ID | No | Changes the question to within-visit analysis |
| Salted HMAC of account ID | Yes | Global key lifecycle and erasure harder than a bounded study needs; never reuse an existing signing secret |
| Manual labelled run manifests | Declared runs only | Smallest benchmark-only alternative |

Attribution lives on the **parent** result set; children inherit scope through existing
joins rather than a repeated identity column.

## Traps the research surfaced

- **A signed token authenticates a result set, not a person.** The token signed the
  result-set ID with no account binding or expiry; interaction routes verified it without a
  session. On attributed sets, require the authenticated account to own the parent study
  membership and **derive identity from the parent, never from a submitted tester ID**.
  A valid signature must never grant journey read access.
- **A pseudonym is not anonymous** (GDPR recital 26, Art. 4(5)): while additional
  information permits re-identification it is personal data, and an app-level opt-in is not
  by itself valid consent — purpose and lawful basis are a controller decision.
- **Erasure must delete linked rows, not just the mapping.** The permanent replay corpus kept
  the original result-set ID — an indirect join handle that survives destroying the mapping.
  Exclude attributed sets from replay and delete the whole parent/child trace on withdrawal,
  erasure or study expiry. **Exported files have their own deletion owner**; deleting the DB
  can't recall a download.
- **Cadence bounds the real retention.** A weekly cleanup with a 90-day cutoff retains rows
  up to ~97 days even when every run succeeds; it doesn't prove "≤ 90 days". A purge that
  skips study rows must also update the archive-count reconciliation, not just add a filter.
- **Aggregate-reader rules conflict with one-person inspection.** An existing k≥5 minimum
  for admin readers can't be met by a named one-tester journey. Prefer authenticated
  **self-export** voluntarily shared; any operator inspection is an explicit study-only
  exception, never bolted onto the aggregate dashboard.
- **Absence of action is not a dismissal**, and a save interaction isn't a relevance grade.

## What the build added (plan and execution, 2026-09-22)

- **Retention got simpler once the controller decided.** The processing decision set no
  study-specific deletion cutoff and no dedicated cleanup job or alarm. Membership expiry
  (30 days by default) **stops collection only**. Attributed rows age out under the
  ordinary 90-day sweep, and that sweep now **purges** tagged parents instead of archiving
  them. That purge is the only cleanup logic left. Withdrawal and account deletion still
  erase the whole trace through one FK cascade, and integration tests prove both paths.
- **Enforce at the database boundary.** The FK and grant boundary plus session-checked
  handlers carry the guarantee. Real-DB regression tests prove it, and documentation alone
  is not enough. Collection ships inert behind an arming flag that is off by default.
- **A required field on the log type finds every producer.** Adding the pseudonym field to
  the result-set log struct broke the type-check on a serving surface the plan never
  listed: a "similar items" path with no session concept. That surface now stamps null, so
  it is absent from every study trace.
- **The export's completeness claim has to name what it leaves out.** Review caught the
  participant notice promising a "complete study trace" while that surface was never
  tagged. The fix was a completeness-limitations list inside the export plus softened
  notice wording. No behaviour changed.
- **Withdrawal can race an in-flight serve.** A serve that resolved the pseudonym just
  before the membership row was deleted hits a foreign-key violation on insert. The
  recorder retries once, untagged, only when the error is that exact shape (FK violation
  code, naming the pseudonym column, on a tagged write) and logs a warning. Every other
  error still throws.
- **Ban tests can be tripped by prose.** A test asserting the export never contains the
  substring `pseudo_user_id` failed on a new limitation sentence that named the column.
  The sentence was reworded, and the ban stayed strict.
- **Rollback order:** disable enrolment first. Never drop the mapping table before existing
  traces and copies are processed, because it is the only erasure index.
- **Pseudonym namespaces multiply.** A separate save log had already pseudonymized with
  `sha256(user_id)`, which does not join to the study's random pseudonym. Downstream
  exporters must bridge server-side on the real id
  ([[Write-Time Deterministic Holdout]]).

## See Also
- [[PII Masking Approaches]] — extends
- [[Every Column Names Its Reader]] — instance-of
- [[Append-Only Human Labels]] — extends
- [[Frozen Version Stamps on Logged Results]] — extends
- [[Write-Time Deterministic Holdout]] — related (the labelled-session exporter joins both pseudonym namespaces)
