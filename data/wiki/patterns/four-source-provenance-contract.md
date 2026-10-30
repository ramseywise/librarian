---
title: Four-Source Provenance Contract
tags: [infra, memory, pattern]
summary: Every stored claim in an AI system is tagged with one of four provenance sources — verified fact, deterministic inference, AI interpretation, human decision — in named columns, and consequential changes keep the chain agent_run → proposal → human edit → approval → state transition → external effect.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/playground/skills/design-system/SKILL.md
  - data/raw/claude-docs/akira/skills/design-system/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/design-system/SKILL.md
  - data/raw/claude-docs/diskoe/skills/design-system/SKILL.md
  - data/raw/claude-docs/akira/skills/design-product/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/design-product/SKILL.md
  - data/raw/claude-docs/diskoe/skills/design-product/SKILL.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--plans--2026-10-07-r8-draft-persistence.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--plans--2026-10-07-r12-provenance-chain.md
  - data/raw/repos/nonprofit-success-ai/.claude--skills--design-product--SKILL.md
  - data/raw/repos/nonprofit-success-ai/.claude--skills--design-system--SKILL.md
---

# Four-Source Provenance Contract

## The four sources

akira's system-design skill requires that any value an AI system stores or shows carries
which of four sources produced it:

1. **Verified fact** — observed from an authoritative source.
2. **Deterministic inference** — derived by code from facts.
3. **AI interpretation** — produced by a model.
4. **Human decision** — set or approved by a person.

Provenance is a **data-model rule, not a UI feature**: a provenance badge with no column
behind it cannot answer "where did this sentence come from?" six months later. The columns
are named — `source_type`, `generated_by`, `model`, `model_version`, `prompt_version`,
`run_id`, `approved_by`, `approved_at`.

## The chain

For any consequential change, the record links:

`agent_run → proposal → human edit → approval → state transition → external effect`

so an external effect can be traced back to the model run that proposed it and the human
who approved it.

## Product-stage quality bars that go with it

- Every retrieved item carries provenance.
- **Separate the audit trail from agent telemetry.** The audit trail answers "who did what,
  and can it be disputed"; telemetry answers "how did the model behave". One table for both
  makes retention and access rules collide.
- **Memory promotion is a gate, not a side effect** — name what approves a promotion into
  durable shared memory and what scopes it.
- **Immutable events get their own entity.** Signatures, approvals and stage transitions must
  reject later writes, including from admins; "immutable" with no enforcing entity is not
  immutable yet.

## Postgres implementation (nonprofit-success-ai)

- A `provenance_source` enum (`verified`, `derived`, `ai`, `human`) is a non-null
  `source_type` on every draft table, with model, model version, prompt version, run id,
  approver and approval time beside it. Existing rows backfill to `derived`.
- Pick the invariant to match what is guaranteed. For drafts, `ai → model is not null`,
  because a fallback-recorded run row may be missing. For routing decisions, where the
  route always returns a run id, a check enforces `(source = 'ai') = (run_id is not null)`.
- **A human edit is a new row with `supersedes_id`, never an overwrite.** Update policies
  allow only status columns to change in place.
- A `provenance_chain` view (`security_invoker`, select granted to `authenticated` only)
  is the reconstruction query: agent run → draft (and the drafts it supersedes) →
  approval → lifecycle transition event → audit row. The transition event carries the
  approval id, so the chain joins without inference.
- A public insert policy forces the provenance value (`derived`) for anonymous
  submissions, so a client cannot claim `ai` or `verified` provenance.

## See Also
- [[Every Column Names Its Reader]] — related (provenance columns are columns that must name their reader)
- [[Principal Write-Surface Matrix]] — related (who is allowed to cause each step of the chain)
- [[Graded-Uncertainty Enrichment Contract]] — related (confidence on AI-interpreted fields)
- [[Four-Stage Design Pipeline with Backflow]] — related (part of; system stage)
- [[Evidence Classification Model]] — alternative-to
- [[Computed-Correctness Lesson Loop]] — extends (provenance retained through memory promotion)
- [[Single-Writer Transition Command]] — extends (the transition event that links approval to audit)
- [[Advisory Enrichment Breaks Ties Only]] — extends (server-fetched facts stored with a status, never client-claimed)
