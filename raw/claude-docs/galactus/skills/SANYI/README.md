# SANYI (三易)

**A change-contract system for agent architectures.** SANYI assigns every
component of a system to one of three change layers, records the assignment in
a contract file (`SANYI.md`), and enforces that contract on every diff —
catching the class of architectural decay that no single-PR code review can
see.

The real question it answers is not "is this code correct?" but **"who is
allowed to change what, and did this diff quietly move a boundary?"** — a
_change-authority_ problem that sits closer to architecture governance and
platform engineering than to linting. The three-layer model is borrowed from
the SANYI (三易) framework of the I Ching (易经): it is the **cognitive
layer** — a sticky, memorable way to name the distinction — while the
enforceable core is _architecture as a change contract_. The philosophy
generated the insight and makes it teachable; it is not decoration, but it is
also not the product. The product is the contract.

## The three layers

| Layer                               | What belongs there                                                          | The contract it implies                                                                                                            | What its violation looks like                                                                      |
| ----------------------------------- | --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| **变易 Bianyi** (the ever-changing) | Prompts, policy thresholds, routing rules, feature flags, model names       | Changing these must **not require a deploy** — they live in config/prompt layers only                                              | A prompt string hardcoded in business logic; every wording tweak ships through CI                  |
| **简易 Jianyi** (the simple)        | State schemas, interfaces, tool schemas, **and the execution graph itself** | Unjustified, unbounded complexity is **debt against an explicit budget** — measured across shape, escape hatches, and control flow | A perfect schema wrapping a hellish graph; or four fields quietly dumped into one `metadata: dict` |
| **不易 Buyi** (the invariant)       | Safety constraints, compliance guarantees, escalation fallbacks             | **Never changes without the highest review; never bypassable** via config, env, or flag                                            | A "harmless" environment variable that can switch off a safety check                               |

Each layer has a line from the I Ching behind it — the source the names come
from:

- **变易**: 穷则变，变则通，通则久 — _"When things reach their limit they
  transform; through transformation they find passage; through passage they
  endure."_ Change is how a system survives.
- **简易**: 夫易简而天下之理得矣 — _"Through simplicity, the principles of the
  world are grasped."_ Simplicity is what keeps a system understandable.
- **不易**: 万变不离其宗 — _"Amidst myriad changes, the root remains."_ Some
  things must hold for any of the rest to mean anything.

## Why architecture decays

Most architectural rot is **layer confusion**: what should be invariant gets
made configurable, what should be changeable gets hardcoded, what should stay
simple silently accretes.

The dangerous case is the first one. Imagine a PR that wraps your PII masking
in a switch:

```python
MASKING_ENABLED = os.environ.get("ENABLE_SAFETY_CHECK", "true") == "true"

def mask_pii(text):
    if not MASKING_ENABLED:
        return text
    ...
```

Every line is innocent. The linter passes. The tests pass (masking is on by
default). A human reviewer sees a reasonable-looking staging convenience and
approves. But the system just changed categorically: an invariant became a
configuration option — 不易 Buyi was silently demoted to 变易 Bianyi. **Single-PR
review structurally cannot catch this**, because nothing in the diff is wrong;
what's wrong is the diff's relationship to a long-term commitment that exists
only in people's heads.

SANYI puts that commitment in a file and makes every diff answer to it.

## Why agent systems specifically

Agent systems are where the three layers are under maximum tension — prompts
need ops-speed iteration, schemas feed directly into prompt size and
debuggability, and a misbehaving LLM can promise your customers refunds. They
also add a dimension traditional software lacks: **the same constraint can be
implemented in the prompt layer, the code layer, or the config layer** — and
choosing the layer is itself a contract decision.

> **The First Law of agent SANYI:** LLMs are probabilistic, so a constraint
> implemented only in a prompt is _soft_. A Buyi invariant must have a
> deterministic code-layer implementation; a prompt-layer copy is at best a
> redundant defense.

A team that writes "never promise refunds" into a system prompt and considers
the matter closed has implemented an invariant in the ever-changing layer.
SANYI flags this as **BY-4** — a check no other review tool performs.

Integration boundaries get the same treatment: a typical `integrations/`
module contains all three layers in one file (retry policy = Bianyi, wrapper
interface = Jianyi, credential handling = Buyi), which is exactly why it's a
cross-layer violation hotspot.

## How it works

Two halves sharing one artifact:

```
/sanyi init    →  interview        →  SANYI.md (the contract) + debt baseline
/sanyi review  →  diff + SANYI.md  →  graded violation report
/sanyi audit   →  repo + SANYI.md  →  full re-measure, debt refresh
```

**`init`** drafts what machines can infer (Bianyi from config conventions,
Jianyi from schemas — your `CLAUDE.md` conventions are often half a contract
already) and interviews you for what they can't: Buyi is business and safety
intent, which lives in no AST. Disputed assignments park in `## Pending`
(enforced strictly until resolved); pre-existing violations are recorded as a
`## Debt` baseline so future reviews stay quiet about history.

**`review`** glob-matches your diff against the contract and reports by
severity — for example:

```markdown
# SANYI Review — fixture-1-safety-downgrade — 2026-06-13

Contract: SANYI.md v1 (last audit 2026-06-13)

## Verdict

Yes — this diff changes the change-contract structure: a Buyi invariant
becomes environment-configurable.

## Findings

### [BLOCKER] BY-2 — PII masking made bypassable

- Entry: 不易 Buyi / PII Masking
- Where: backend/security/masking.py:8
- What: New MASKING_ENABLED env switch can disable mask_pii() entirely;
  the invariant is demoted to a config option.
- Decision options: revert | redesign | amend contract via architecture review

### [BLOCKER] BY-3 — evidence test deleted

- Entry: 不易 Buyi / PII Masking
- Where: tests/test_pii_cannot_be_disabled.py
- What: test_no_bypass_flag (the guard against exactly this change) removed.
```

**`audit`** re-measures the whole repo: prompt-only invariants (BY-4),
hardcoded changeables (BN-1), entropy vs budget, dangling contract entries.

The full violation taxonomy (BY-1…4, JY-1…3, BN-1, MG-1, UN-1…2) lives in
[references/violations.md](references/violations.md); the contract format in
[references/contract-spec.md](references/contract-spec.md).

## Layers evolve — the I Ching part

A classification system would sort components once and freeze them. The I Ching
is not that: 变中有不变, 不变中有变 — the layers themselves move. A prompt that
survives hundreds of experiments and becomes a compliance rule should be
**promoted** Bianyi → Buyi; an "invariant" that turns out merely operational can
be **demoted**. SANYI records these in a `## Migrations` log with a
rationale and a date. The discipline is not "never change a layer" — it is
"never change a layer _silently_": an unrecorded migration is **MG-1**, and the
one genuinely dangerous direction (quietly making an invariant bypassable) stays
a **BY-2** blocker. This is what keeps the contract a living document rather than
an ossified taxonomy.

## Design rationale

**Report-only by default; Buyi is never auto-fixed.** A blocker's "fix" is a
human decision — revert, redesign, or amend the contract through architecture
review. Auto-fixing a safety constraint is itself a Buyi violation: _the
enforcer must not rewrite the verdict._ Jianyi fixes require redesign or
justification, not field deletion. Only Bianyi violations have a mechanical,
behavior-preserving fix (move the literal to its declared layer), so
`review --fix` applies exactly those and nothing else.

**Anti-staleness is built into the format.** Contract documents die by going
stale, so SANYI.md is a live participant: every run re-stamps Jianyi `current`
values; entries whose paths match nothing are reported as dangling rather than
skipped; the Debt baseline keeps reviews loud about news and quiet about
history.

**Buyi must stay scarce, and flat.** The admission test is a consequence test,
not a headcount: a thing is Buyi only if violating it causes a **security,
legal, financial, or trust failure**. Everything else is Jianyi or Bianyi. We
deliberately reject Buyi _sub-tiers_ ("critical vs operational invariants") —
they are an inflation vector, and severity is already encoded by layer. The
thing that feels like a lesser invariant is almost always mis-split: the
tunable part (a threshold value) is Bianyi, the must-hold part (a fallback must
fire) is Buyi.

**Field count is a starting proxy, not the metric.** Counting fields is easy to
game — dump growth into `metadata: dict` and the budget never trips. So Jianyi
measures _unbounded complexity_ across three carriers: shape (fields), escape
hatches (untyped catch-alls, flagged JY-3), and control flow (the graph).
Deterministic flow metrics (fan-out, depth, cycles) need scripted analysis and
are deferred until the contract format proves out; for now control-flow growth
is judged qualitatively.

## Quick start

```
cd your-agent-repo
/sanyi init          # ~20 min interview → SANYI.md at repo root, next to CLAUDE.md
/sanyi review        # on your next PR branch
/sanyi review --fix  # same, plus auto-relocation of hardcoded changeables
/sanyi audit         # quarterly, or after a big refactor
```
