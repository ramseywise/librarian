# Violations — taxonomy, severities, report template, `--fix` rules

The enforcement vocabulary shared by `review` and `audit`. Codes and
severities here are authoritative; SKILL.md and README.md mirror them.

## 1. Taxonomy

| Code | Meaning                                                                                        | Severity |
| ---- | ---------------------------------------------------------------------------------------------- | -------- |
| BY-1 | Direct modification of Buyi-guarded code                                                       | blocker  |
| BY-2 | Semantic downgrade: Buyi invariant made bypassable via flag/config/env                         | blocker  |
| BY-3 | Buyi evidence test deleted or weakened                                                         | blocker  |
| BY-4 | Declared Buyi invariant has prompt-only implementation, no deterministic code path             | blocker  |
| JY-1 | Jianyi budget exceeded (shape, graph, or other complexity carrier)                             | warning  |
| JY-2 | Anomalous single-PR growth within budget (e.g. +3 fields/edges in one PR)                      | warning  |
| JY-3 | Unbounded escape hatch: untyped catch-all (`dict`/`Any`/`**kwargs`) hides growth               | warning  |
| BN-1 | Bianyi value (prompt string / tunable) hardcoded outside its declared layer                    | info     |
| MG-1 | Unrecorded layer migration: a component's natural layer shifted with no `## Migrations` record | notice   |
| UN-1 | Changed file matches no contract entry (unassigned)                                            | notice   |
| UN-2 | Dangling contract: entry `paths` match no existing file                                        | notice   |

**BY-1 — direct modification.** Any edit inside a Buyi entry's `paths` —
including "harmless" refactors. The point is not that the edit is wrong but
that it must clear the highest review bar. Example: reordering the regexes in
a PII masker. Subsumed when BY-2 or BY-3 fires on the same entry — report only
the more specific code.

**BY-2 — semantic downgrade.** The invariant's code survives but becomes
conditional: a new flag, env var, or config key can now switch it off. This is
the most dangerous decay pattern because **every individual line looks
innocent** — a lint pass and a human skim both approve it; only comparing the
diff against the contract reveals that 不易 Buyi was silently demoted to 变易
Bianyi. Canonical example: `ENABLE_SAFETY_CHECK = os.environ.get(...)` wrapped
around a safety constraint "just for staging".

**BY-3 — evidence weakened.** The entry's `evidence` test is deleted, skipped,
or loosened until it no longer guards the contract. An invariant whose guard
test died is one PR away from BY-2. Example: removing
`test_no_bypass_flag`.

**BY-4 — prompt-only invariant.** The First Law of agent SANYI: LLMs are
probabilistic, so a constraint implemented only in a prompt is soft. A
declared invariant must have a deterministic code-layer implementation.
Canonical example: "never promise refunds" existing only as a sentence in a
system prompt — no output filter, no middleware guard. Extremely common, and
checked by no other tool.

**JY-1 — budget exceeded.** A Jianyi component grew past its declared
`budget`. The fix is redesign or explicit justification — never silent budget
inflation. Field/edge count is the _starting_ proxy, not the definition: the
real target is unjustified, unbounded complexity in any of the three carriers
(shape, escape hatches, control flow — see `contract-spec.md` 简易). Example:
a state schema at 13 fields against "≤ 12 fields", or a graph that adds a third
retry cycle.

**JY-2 — anomalous growth.** Within budget, but a single PR adds enough (≥3
fields/params/edges) to deserve a justification even before the ceiling is hit.
Entropy arrives one sprint at a time.

**JY-3 — unbounded escape hatch.** A field count is easy to game: dump
everything into `metadata: dict`, `**kwargs`, or an `Any`, and the budget never
trips while the real complexity explodes. An untyped catch-all introduced or
widened in a Jianyi component is flagged here and treated as _unbounded_ growth,
not "one field". The fix is to type the thing — make the hidden fields visible
so they count. (This is why raw field count alone is a weak metric.)

**BN-1 — hardcoded changeable.** The reverse failure: a value the contract
says must be tunable without deploy appears as a literal in business logic —
an inline prompt string, a magic threshold. Mechanically fixable (see §4).

**MG-1 — unrecorded layer migration.** A diff (or audit) shows a component's
natural layer has shifted from its contract assignment, with no record in
`## Migrations`. Promotions (Bianyi → Buyi: a battle-tested prompt becomes
a hardened compliance rule) and justified demotions are _good_ — they just must
be logged with a rationale, so the contract evolves on purpose rather than
drifting. Severity is notice precisely because migration is healthy; the one
unhealthy direction — silently making an invariant bypassable — is the more
specific BY-2 blocker, not MG-1.

A common case: a diff that **remediates** a BY-4 (adds the deterministic code
guard a prompt-only invariant was missing) is exactly a Bianyi → Buyi
promotion — report it as MG-1 (record the migration + re-point the entry's
`paths` to where the guard now lives), not as a fresh violation. It is the
cure, not the disease.

**UN-1 — unassigned.** A changed file matches no entry: it has no change
contract, so the layer decision was never made. New components must be
assigned (or parked in Pending) before they calcify.

**UN-2 — dangling contract.** An entry's `paths` match nothing — usually
post-refactor drift. The contract points at a void; re-point or retire it.

## 2. Severity semantics

| Severity    | Meaning                                        | Tool behavior                                                                                                            |
| ----------- | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **blocker** | The change-contract structure is being altered | Report + present decision options: **revert / redesign / amend the contract via architecture review**. Never auto-fixed. |
| **warning** | Entropy contract under pressure                | Report + bookkeeping (update `current` stamps).                                                                          |
| **info**    | Changeable made rigid                          | Report; auto-fixable with `--fix`.                                                                                       |
| **notice**  | Contract hygiene signal                        | Report only.                                                                                                             |

## 3. Report template

Reproduce this structure for every review/audit run. Omit empty sections
except `## Verdict`.

```markdown
# SANYI Review — <diff identifier> — <date>

Contract: SANYI.md v<N> (last audit <date>)

## Verdict

<one line: does this diff change the system's change-contract structure?>

## Findings

### [BLOCKER] BY-2 — <title>

- Entry: 不易 Buyi / <entry name>
- Where: <file:line>
- What: <what the diff does, in contract terms>
- Decision options: revert | redesign | amend contract via architecture review

### [WARNING] JY-1 — <title>

- Entry: 简易 Jianyi / <entry name>
- Where: <file:line>
- What: <growth vs budget, e.g. "fields 9 → 13, budget ≤ 12">

### [INFO] BN-1 — <title>

- Entry: 变易 Bianyi / <entry name>
- Where: <file:line>
- What: <the literal and where it should live>

### [NOTICE] UN-1 — <title>

- Where: <file>
- What: <no contract entry matches; assign a layer or park in Pending>

## Bookkeeping

- Updated current: <entry> <old> → <new> (<date>)

## Debt candidates

<accepted violations the team may record into ## Debt, in debt-record
format: - [CODE] <location> — <one-line description> (recorded YYYY-MM-DD)>
```

For audit runs, title the report `SANYI Audit — <repo> — <date>`, scan the
whole tree instead of a diff, and replace the verdict question with: _does the
repo match its declared change-contract structure?_ Everything else is
identical.

## 4. `--fix` rules

`--fix` auto-fixes **BN-1 only**. Procedure:

1. Move the literal/prompt to the declared layer file (`config.py` /
   `prompts.py`, per the target repo's conventions).
2. Name it consistently with its neighbors (`SCREAMING_SNAKE` constants,
   `*_PROMPT` suffix for prompts).
3. Replace the usage site with an import.
4. Confirm the change is behavior-preserving (same value, same call sites).

Before:

```python
# backend/agents/router.py
def route(intent: str, confidence: float) -> str:
    if confidence < 0.6:
        return "human_escalation"
    ...
```

After:

```python
# backend/config.py
ESCALATION_HUMAN_THRESHOLD = 0.6

# backend/agents/router.py
from backend.config import ESCALATION_HUMAN_THRESHOLD

def route(intent: str, confidence: float) -> str:
    if confidence < ESCALATION_HUMAN_THRESHOLD:
        return "human_escalation"
    ...
```

Naming caveat: when the covering contract entry is symbol-scoped (e.g.
`backend/config.py#ESCALATION_*`), the new constant's name must match that
glob — otherwise the relocation moves the value out of contract coverage.
Here `ESCALATION_HUMAN_THRESHOLD`, not `HUMAN_ESCALATION_THRESHOLD`.

**Why BY-_ and JY-_ are never auto-fixed.** A Buyi "fix" is a human decision —
revert the change, redesign the approach, or amend the contract itself through
architecture review. Auto-fixing a safety constraint is itself a Buyi
violation: **the enforcer must not rewrite the verdict.** A Jianyi fix
requires redesign or a justification, not field deletion — a tool that deletes
schema fields to satisfy a budget is a disaster generator. Only BN-1 has a
mechanical, unique-direction, behavior-preserving fix: move the value.

## 5. Self-application

The tool applies SANYI to its own output:

- Reports are **Bianyi** — freely generated, regenerate at will.
- Contract bookkeeping (`current` stamps, `last-audit`) is **Jianyi** —
  minimal necessary writes, always on, never optional.
- Code modification is restricted to the lowest-risk layer (BN-1) and opt-in
  (`--fix`) — the closest the tool gets to **Buyi** territory, treated
  accordingly.

## 6. Scope notes — deferred and rejected

Kept here so they don't silently re-enter (the tool eating its own dogfood:
recording what was cut, not pretending coverage is total).

- **Deferred to route B (needs scripts):** deterministic Flow Budget metrics —
  counting graph fan-out, depth, and cycles. The control-flow _principle_ is
  live now (a graph is a Jianyi component; new edges/loops need justification),
  but reliable counting exceeds pure-LLM measurement. Until route B, control
  flow is judged qualitatively.
- **Rejected (2026-06-13): Buyi sub-tiers** (critical / important / operational
  Buyi). They are an invariant-inflation vector and fight Buyi scarcity.
  Severity is already encoded by layer; the consequence test (security / legal /
  financial / trust failure) is the admission gate. A "lesser Buyi" is almost
  always a mis-split — the tunable part is Bianyi, the must-hold part is Buyi.
