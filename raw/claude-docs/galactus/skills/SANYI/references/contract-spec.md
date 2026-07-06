# Contract Spec — the `SANYI.md` file format

This document defines the format of `SANYI.md`, the change contract that the
SANYI skill creates (`init`), enforces (`review`), and re-measures (`audit`).
Read this before writing or parsing any `SANYI.md`.

## Purpose

`SANYI.md` declares, for each significant component of a system, which change
layer it belongs to — 变易 Bianyi (the ever-changing), 简易 Jianyi (the
simple), or 不易 Buyi (the invariant) — and what contract that assignment
implies. It is a **contract, not documentation**: both humans and agents read
it, and review/audit runs write back to it (stamps, debt records). It lives at
the **target repo root, sibling to `CLAUDE.md`** — never buried in `docs/`.

## File header

```markdown
# SANYI.md — change contract

project: <name>
version: <integer> # bump on structural change (entries added/removed/re-layered)
last-audit: YYYY-MM-DD # refreshed by every audit run
```

## The six sections

Section names are exact. The three **layer** sections keep the Chinese term
plus pinyin (`## 不易 Buyi`, `## 简易 Jianyi`, `## 变易 Bianyi`); the three
**bookkeeping** sections are plain English (`## Migrations`, `## Pending`,
`## Debt`). Match them verbatim — they are the parser's anchors.

### `## 不易 Buyi`

Invariants — safety constraints, compliance guarantees, escalation fallbacks.

**The admission test (this, not a count, is the gate):** a thing is Buyi only
if violating it causes a **security, legal, financial, or trust failure**.
Anything that fails this test — logging, naming, retry policy, monitoring,
operational thresholds — is NOT Buyi, no matter how much someone wants to
protect it. This consequence test is what keeps Buyi scarce; an entry-count
heuristic (`interview-guide.md` §5) is only a secondary smell.

The contract for every Buyi entry:

- Any diff touching it gets the highest review level (blocker).
- It must never be bypassable via config, env var, or flag. Making it
  conditional is a _semantic downgrade_ (violation BY-2) even when every
  individual line looks innocent.
- It must have a **deterministic code-layer implementation**. Because LLMs are
  probabilistic, a prompt instruction alone is a soft constraint; a declared
  invariant with prompt-only implementation is violation BY-4. A prompt copy
  is welcome as redundant defense, never as the implementation.

**No sub-tiers.** Buyi is deliberately flat — there is no "critical vs
operational Buyi". Severity is already encoded by _layer_ (Buyi = blocker,
Jianyi = warning, Bianyi = info). The thing that feels like a lesser Buyi
(e.g. "escalate under 60% confidence") is almost always mis-split: the
_threshold value_ 60 is Bianyi, while "a fallback must fire" is the real Buyi.
Splitting it correctly, not tiering it, is the fix. (Considered and rejected
2026-06-13 — tiers are an invariant-inflation vector.)

### `## 简易 Jianyi`

Complexity-budgeted components. The contract: **unjustified, unbounded
complexity is debt**; growth requires justification in the PR and is measured
against an explicit `budget`. Complexity has three carriers, all governed
here:

1. **Shape** — state schemas, inter-agent interfaces, tool schemas. Field /
   parameter count is the _starting_ proxy, not the whole story (see below).
2. **Escape hatches** — an untyped catch-all (`dict`, `Any`, `**kwargs`,
   `metadata: dict`) hides unbounded growth behind a single field and games a
   raw count. These are flagged as JY-3 and treated as _unbounded_, not as
   "one field".
3. **Control flow** — the execution graph itself (LangGraph nodes/edges,
   conditional routing, retry/reflect loops). For most agent systems this is
   the **dominant** complexity source — a perfect schema can wrap a hellish
   graph. A graph file can be a Jianyi entry; new edges, branches, or cycles
   need justification just like new fields.

   _Deferred to route B:_ deterministic flow metrics (max fan-out, depth,
   cycle count) need scripted graph analysis, which exceeds reliable pure-LLM
   measurement. Until then control-flow growth is judged qualitatively
   ("does this PR add an unjustified branch/loop?").

When a component repeatedly pushes its budget, the correct response is
redesign, not budget inflation — and not hiding the growth in an escape hatch.

### `## 变易 Bianyi`

Things that must be easy to change — prompts, policy thresholds, routing
rules, feature flags, model names. The contract: changing them must not
require a deploy, so their values may only live in their declared layer
(config / prompts files). A literal threshold or inline prompt string in
business logic is violation BN-1 — the _reverse_ failure: the changeable made
rigid.

### `## Migrations`

The evolution log. A layer assignment is not permanent: a prompt that survives
500 experiments and becomes a compliance rule should be **promoted** Bianyi →
Buyi; an invariant that turned out to be merely operational can be **demoted**.
This is the part of 易经 that a pure classification misses — 变中有不变, 不变中有变:
the layers themselves move, deliberately and with a recorded reason.

Each migration record:

```markdown
- 2026-06-13: Bianyi → Buyi / Refund guard — prompt-only refund rule hardened
  into an output filter after 6 months of incidents; now a compliance
  invariant. (author: yan)
```

Format: `- YYYY-MM-DD: <from> → <to> / <entry> — <rationale>. (author: <who>)`.

A diff that effectively moves a component's natural layer **without** a record
here is violation MG-1 (an unrecorded migration — record it). The one
direction that is never just "record it" is silently making an invariant
bypassable: that stays a BY-2 blocker, not an MG-1 notice.

### `## Pending`

Components whose layer assignment is disputed. Parking here is honest;
forcing a layer is not. **Pending entries are enforced at the strictest level
(as Buyi) by default** until the team resolves them.

### `## Debt`

The baseline of known, accepted, pre-existing violations (the linter-baseline
pattern). **Review reports only NEW violations; entries recorded here are not
re-reported on every PR** — without this, history floods every report and the
tool gets muted within weeks. Each debt record:

```markdown
- [BY-4] backend/agents/prompts.py#HC_AGENT_PROMPT — "No refund promises" is
  prompt-only, no code-layer guard (recorded 2026-06-13)
```

Format: `- [CODE] <location> — <one-line description> (recorded YYYY-MM-DD)`.

## Entry fields

| Field      | Applies to                              | Meaning                                                                                                                                                                                                                                               |
| ---------- | --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `paths`    | all                                     | Glob(s) locating the component. Symbol targeting: `file.py#PREFIX_*` scopes the entry to matching symbols inside the file.                                                                                                                            |
| `contract` | all                                     | Plain-language contract terms — the enforcement basis the reviewer reasons against. Write it **testable** ("must not X via any Y"), not aspirational ("should be secure").                                                                            |
| `evidence` | optional; strongly recommended for Buyi | Test file(s) guarding the contract. Deleting or weakening an evidence test is violation BY-3.                                                                                                                                                         |
| `budget`   | Jianyi only                             | Ceiling plus growth rule. For shape: "≤ 12 fields; each new field needs justification". For a graph: "new edges/branches/cycles need justification" (qualitative until route B). Untyped escape hatches (`dict`/`Any`) count as unbounded — see JY-3. |
| `current`  | Jianyi only                             | Last measured value with date stamp, e.g. `9 (2026-06-13)`. **Updated by every review/audit run** — this is what keeps the file alive.                                                                                                                |

## Annotated example

A complete `SANYI.md` for a small agent backend:

```markdown
# SANYI.md — change contract

project: sanyi-fixture
version: 1
last-audit: 2026-06-13

## 不易 Buyi

### PII Masking

<!-- An invariant done right: deterministic implementation (mask_pii in the
     outbound middleware) plus an evidence test that asserts no bypass flag
     exists. The contract names the failure mode it forbids. -->

- paths: backend/security/masking.py, backend/middleware/outbound.py
- contract: All outbound messages pass through mask_pii(); must not be
  bypassable via any config, env var, or flag. Requires a deterministic
  code-layer implementation.
- evidence: tests/test_pii_cannot_be_disabled.py

### No refund promises

<!-- A declared invariant whose only implementation is a sentence in a system
     prompt. Audit flags this as BY-4: the invariant lives in the
     ever-changing layer. The cure is a code-layer guard on outbound text. -->

- paths: backend/agents/prompts.py#HC_AGENT_PROMPT
- contract: The agent must never promise refunds or specific reimbursement
  amounts. Requires a deterministic code-layer guard on outbound text.

## 简易 Jianyi

### GlobalState

<!-- The entropy budget makes "just one more field" a visible, measured cost
     instead of an invisible accretion. `current` is re-stamped by every
     review that touches this path. -->

- paths: backend/states/global_state.py
- budget: ≤ 12 fields; each new field needs justification in the PR
- current: 9 (2026-06-13)

## 变易 Bianyi

### Escalation thresholds

<!-- Symbol-scoped glob: only ESCALATION_* constants in config.py are covered.
     The contract makes hardcoding a threshold elsewhere a named violation. -->

- paths: backend/config.py#ESCALATION\_\*
- contract: May only appear in the config layer; a literal threshold in
  business logic is a violation.

### Agent prompts

- paths: backend/agents/prompts.py
- contract: All prompt text lives here; inline prompt strings elsewhere are
  violations.

## Migrations

<!-- The evolution log. Empty at init; fills as layers are promoted/demoted. -->

## Pending

<!-- Empty is fine. Disputed assignments park here and are enforced as Buyi
     until resolved. -->

## Debt

<!-- Filled by init's closing audit and by accepted review findings. -->
```

## Anti-staleness rules

A contract document's #1 failure mode is going stale. These rules are part of
the format, not optional etiquette:

1. **Live stamps**: every review/audit run updates the `current` values (and
   audit refreshes `last-audit`). The file is an active read/write participant
   in the workflow, not a read-only bible.
2. **Dangling detection**: if an entry's `paths` match no existing file,
   report it (UN-2) — never silently skip. This catches post-refactor drift.
3. **Pending = strictest default**: unresolved assignments are enforced as
   Buyi, so parking is safe but not free — pressure to resolve stays on.
4. **Debt = baseline**: known violations are recorded once and excluded from
   future reports, so reviews stay quiet about history and loud about news.
5. **Migrations are recorded, never silent**: a component changing its natural
   layer must leave a `## Migrations` record with a rationale; an
   unrecorded move is MG-1. This is what makes the contract evolve instead of
   ossify.
