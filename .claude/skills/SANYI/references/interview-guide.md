# Interview Guide — `init` heuristics and question bank

How to draft a layer assignment automatically, what only a human can answer,
and how to push back. Used by `/sanyi init` (and its closing audit).

## 1. Auto-draft heuristics

Read these sources before asking the human anything. Two of the three layers
are largely inferable from code; draft them first so the interview spends its
questions where machines are blind.

| Signal                                                                                                            | Suggests                                                            | Why                                                                                                                                                                          |
| ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Target repo's `CLAUDE.md` conventions (e.g. prompts-in-`prompts.py`, tunables-in-`config.py`, state-in-`states/`) | 变易 Bianyi / 简易 Jianyi entries, directly                         | Layer conventions are often already declared — promote them into contract entries rather than re-deriving them.                                                              |
| Contents of `config.py`, settings modules, `prompts.py`                                                           | Bianyi candidates                                                   | Someone already decided these must be tunable; the contract makes the decision enforceable.                                                                                  |
| `TypedDict` / dataclass / pydantic models, tool schemas, inter-agent interfaces                                   | Jianyi candidates (shape)                                           | Shared shapes are where entropy accretes one innocent field at a time. Measure current size on the spot to seed `current`.                                                   |
| Execution graph — LangGraph `StateGraph`, node wiring, `add_conditional_edges`, retry/reflect loops               | Jianyi candidates (control flow)                                    | For agent systems the graph is usually the **dominant** complexity source, not the schema. A perfect state shape can wrap a hellish graph. Budget new edges/branches/cycles. |
| Security / auth / PII / compliance / escalation-fallback code; `try/except` safety nets around agent output       | Buyi **candidates** (confirm in interview — never auto-assign Buyi) | The code shows where invariants live, but not which guarantees the business actually depends on.                                                                             |
| Hardcoded prompt strings or literal thresholds in business logic                                                  | Pre-draft BN-1 debt                                                 | "Should-be-Bianyi that isn't" — note for the closing audit.                                                                                                                  |

**Integration boundaries get special treatment.** An `integrations/` module
typically contains all three layers in one file — which is exactly why it is a
cross-layer violation hotspot. Split each integration into separate entries:

- retry/timeout/backoff policy → Bianyi
- the wrapper interface other code calls → Jianyi
- credential and secret handling → Buyi

## 2. Confirmation protocol

Present draft assignments **one component at a time**, as a multiple-choice
question: accept the proposed layer / move to a different layer / park in
Pending. Record genuine disputes in `## Pending` — parking is honest,
forcing is not — and remind the user that Pending is enforced as Buyi until
resolved.

## 3. Buyi question bank

Buyi is the one layer machines cannot infer: business and safety intent is not
in any AST. Ask, one at a time, adapting to the domain.

**Apply the admission test to every candidate answer:** it is Buyi only if
violating it causes a **security, legal, financial, or trust failure**. If the
worst case is "a bit messy" or "harder to operate", it is not Buyi — it is
Jianyi or Bianyi. This consequence gate, not a headcount, is what keeps the
layer scarce.

1. What must this agent **never do, say, or promise**? (refunds, discounts,
   legal/medical advice, commitments on behalf of the company)
2. Which **compliance constraints** apply? (PII handling, GDPR/CCPA, sector
   rules — healthcare, finance, insurance)
3. What are the **escalation fallbacks** that must always fire, no matter what
   the LLM does? (human handoff conditions, confidence floors)
4. Which **data must never leave** the system boundary? (to users, to
   third-party APIs, to logs)
5. Which actions are **irreversible** (sends, deletes, payments, external
   writes), and what guards them today?
6. What would a misbehaving agent **cost you, concretely**? (money, license,
   reputation — the answer ranks the invariants)

## 4. The first-law probe

Run this for **every** Buyi entry before writing it down:

> "Where is this enforced in deterministic code?"

If the only answer is a prompt instruction, apply the First Law of agent
SANYI: prompt-only constraints are soft. Record a BY-4 debt entry immediately
and recommend a code-layer guard (output filter, middleware check, schema
validation). The entry still goes into `## 不易 Buyi` — the declared intent is
real — but the gap between declaration and implementation is now on the books.

## 5. Over-declaration pushback

The real gate is the consequence test in §3 — run it on every entry first.
The entry **count** is only a secondary smell: if Buyi exceeds **~7**, that is
a signal the consequence test is being applied too loosely, so re-challenge
each one:

> "Does violating this actually cause a security, legal, financial, or trust
> failure? If not, it is not Buyi. Buyi must stay scarce, like root access —
> if everything is an invariant, nothing is."

Offer demotion to Jianyi (if the real concern is interface stability) or
parking in Pending (if the team genuinely disagrees). A contract whose every
entry is a blocker produces all-red reviews, and all-red reviews get muted.
Do **not** resolve the tension by inventing softer Buyi sub-tiers — that is an
inflation vector (rejected; see `violations.md` §6). Mis-feeling a "lesser
Buyi" usually means a split is needed: the tunable part is Bianyi, the
must-hold part is Buyi.

## 6. Closing audit

After the contract draft is confirmed:

1. Run the **audit** procedure (see SKILL.md, audit mode) against the fresh
   `SANYI.md`.
2. Write findings into `## Debt` in the debt-record format
   (`contract-spec.md` defines it).
3. Deliver to the user: the finished `SANYI.md` plus a short debt summary —
   "here is your contract, and here is the starting debt it measured."

The seeded debt matters: review mode reports only NEW violations, so the
baseline must be honest on day one.

## 7. Layer migrations

Layer assignment is not permanent. When the interview (or a later review)
finds that a component has outgrown its layer — a prompt hardened over hundreds
of experiments into a compliance rule (Bianyi → Buyi), or a supposed invariant
that turned out merely operational (Buyi → Jianyi) — record it in
`## Migrations` with a one-line rationale. This is the 易经 move: the layers
themselves are allowed to change; what is forbidden is changing them _silently_
(MG-1), and silently weakening an invariant specifically (BY-2).
