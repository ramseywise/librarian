---
title: Blind Labels Judge No Prompt
tags: [eval, pattern]
summary: "When one labelling tool hosts both a blind instrument (the human rates the item's own evidence and is the κ_HH ceiling) and an output-judgment instrument (the human compares model outputs), enforce the split in the schema: blind rows carry no prompt identity at all, only an evidence hash. That is what lets every future prompt version be re-scored against the same labels."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-15-dis275-human-label-persistence.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-15-dis275-human-label-persistence.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-15-dis275-human-label-persistence.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-15-dis275-human-label-persistence.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-15-dis275-human-label-persistence.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-15-dis275-human-label-persistence.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-15-dis275-human-label-persistence.md
---

# Blind Labels Judge No Prompt

From akira's plan to persist human enrichment labels in the app. The admin rating tool
served two instruments over the same attributes (vibe tags, energy, sociality):

- **Absolute (blind).** The rater sees the item's evidence and assigns values. This is
  the primary instrument. It sets the human–human agreement ceiling (κ_HH) that gates the
  LLM judge's threshold, `κ_judge ≥ 0.8 × κ_HH` (see [[Human Agreement Ceiling Protocol]]).
  The protocol's blinding rule says the rater sees **no model output at all**.
- **Pairwise (output judgment).** The rater compares two enrichment rows' tags and picks
  the better one. It is informational only and feeds model comparison. The existing UI
  already showed the model's own values and asked "which set of vibe tags better fits?"

A review of the plan found that the first draft treated these as two UI modes over one
row shape. Both would have snapshotted `model` / `prompt_version` / `prompt_hash`.

## The rule

**Encode the instrument split in the schema, not only in the UI.**

| Instrument | Snapshots | Enforced by |
|---|---|---|
| `pairwise` | prompt identity for **both** compared enrichment rows (a `compare_*` column set), since either can be re-enriched later | CHECK: populated iff `instrument = 'pairwise'` |
| `absolute` | `content_hash`, the identity of the *evidence* the model would see. Prompt identity is NULL | CHECK: prompt columns NULL for `absolute` |

The point of the NULL is not tidiness. **A blind label judges no prompt, so every prompt
iteration can be re-scored against it.** The judge-vs-human ratio ρ = κ_MH / κ_HH joins a
blind label to *whichever* enrichment row saw the same content hash. If a write-path bug
leaked output identity into a supposedly blind row, even as inert metadata, that row would
look attached to one prompt version. The CHECK makes that bug impossible instead of merely
unlikely.

Blinding was then enforced twice more. The UI component's type would not accept
model-output fields, and the corpus route strips model-output fields server-side when it
serves the absolute mode. A type-level guarantee alone does not stop a route from sending
the data.

## Companion rules from the same plan

- **Never narrow the label vocabulary to match the producer's current schema.** A parallel
  issue was about to drop `social_intensity` from enrichment output. The label table's
  `dimension` CHECK still lists it. Labels describe what a human judged, a construct, and
  are not a foreign key to a live enrichment column. Historical rows must stay valid, and
  the blind instrument measures the construct whether or not the model still emits it.
- **A repeated item is a second observation, not a correction.** Intra-rater consistency
  needs some items shown twice. The append-only "latest row is current" rule would have let
  the repeat retire the rater's first judgment. Supersession was therefore scoped to an
  assignment occurrence (`assignment_id`, `is_repeated`), and the parity export filters
  repeated occurrences out.
- **Two exports: parity and raw.** The parity export reproduces the agreement script's
  two input shapes exactly and reads only current rows, the same thing the script's own
  dedup would collapse to. The raw export reads every row, for repeated-item and
  intra-rater analysis that the script's dedup would silently discard. A parity test proves
  that the DB export equals an equivalent hand-authored JSONL.
- **Rater identity uses opaque codes checked at the database.** The rater ids are codes
  (`r01`…). The mapping from code to person lives outside the app and the repo.
  `check (rater_id ~ '^r[0-9]{2}$')` sits on the label table, and the picklist parser drops
  and logs (by count, never by value) anything that does not match. Real names would have
  been "reversible at zero schema cost" only until the first row landed. An append-only
  table makes them permanent. See [[Study-Scoped Pseudonymous Attribution]].
- **Key labels to enrichment rows, so resolve that first.** The rating corpus's item id
  was the event's content id, not an enrichment id. A resolution step had to come before
  the write path could key to the row a rating actually judged.
- **Fire-and-forget writes need a visible failure count.** Per-pair writes never block
  the rater. A `failedWrites` counter and the old JSONL download stay as the fallback of
  record.
- **Read env vars lazily in testable modules.** A module-scope `process.env` read for the
  rater picklist defeated `vi.stubEnv`. The parser was made lazily re-evaluated.

## See Also
- [[Append-Only Human Labels]] — extends (the table design this plan built)
- [[Human Agreement Ceiling Protocol]] — prerequisite-for (the κ_HH study the blind rows feed)
- [[Frozen Version Stamps on Logged Results]] — related (stamp versions on output-judgment rows, but not on blind rows)
- [[Study-Scoped Pseudonymous Attribution]] — related (pseudonymous rater identity)
- [[Positive-Only Judge Fixtures Measure Recall]] — related (the judges these labels will calibrate)
- [[Human Verdicts as Judge Fixtures]] — prerequisite-for (exporting these labels into judge fixtures)
