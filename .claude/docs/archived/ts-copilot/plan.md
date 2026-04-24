# Plan: TypeScript Copilot Upgrades

**Status:** Ready for execution
**Scope:** `v2/ts_google_adk/` — agent, tools, schema, and hooks
**Updated:** 2026-04-14 — research pass complete; plan corrected and extended
**Research:** `.claude/docs/in-progress/ts-copilot/research.md`
**Related plan:** `.claude/docs/backlog/py-copilot/plan.md` (Python port — architectural decisions cross-affect this plan)

---

## Research Findings (corrections to original draft)

### Structural corrections
- `src/agents/accounting-ts` is a **single `.ts` file**, not a directory. All new tools go in `src/agents/tools/*.ts`.
- The original "File Change Summary" listed `.py` extensions — this is a TypeScript project. All new files are `.ts`.
- Current tool count is **18** (not 17+1 as implied): getInvoice, listInvoices, getInvoiceSummary, createInvoice, editInvoice, createInvoiceFromQuote, sendInvoiceByEmail, sendQuoteByEmail, listCustomers, createCustomer, editCustomer, listProducts, createProduct, editProduct, listQuotes, createQuote, inviteUser, fetchSupportKnowledge.

### Blocking risk: model string may be wrong
The live model string is `gemini-3-flash-preview`. **`gemini-3` does not correspond to any known Gemini release.** The Python plan uses `gemini-2.5-flash-preview-04-17`. Before adding any tools, verify the actual model being served — check the ECS task definition or the deployed env. If the string is silently falling back to a default, quality benchmarks in this plan are against the wrong baseline.

**Action (do first):** Confirm the correct model string and update `accounting-ts` if needed.

### Blocking risk: Gemini Flash tool-count degradation
The live model is Gemini Flash (pending model name confirmation above). The plan itself flags quality degradation at 25+ tools on Gemini Flash. Adding 10 tools brings the total to 28 — well past the threshold. **This risk must be resolved before adding all tools in Part 1.** Decision: add tools in two tranches, evaluate quality after each.

- **Tranche A** (priority, add first): bills tools + schema change. These unlock the `expenseManagement` quick action which is the most visible gap.
- **Tranche B** (add only if quality holds or after agent split): transactions, VAT, reports.

### Hooks gap: zero TypeScript coverage
All existing PostToolUse/PreToolUse hooks gate exclusively on `.py$`. The TS codebase (`v2/ts_google_adk/`) has:
- No `tsc --noEmit` check on edit
- No ESLint check on edit
- No `console.log` guard (equivalent of `[no-print]`)
- No SDK pattern lint for TS (hardcoded model strings, bare `new LlmAgent`)
- No tool-count guard (warn before hitting Gemini Flash degradation limit)
- `review_gate.sh` does not gate `.ts` / `.tsx` files — edits bypass the review step
- Pre-commit hook only runs `uv run pytest` — does not run `npx tsc` or the TS test suite
- No pre-commit Next.js build check (`npm run build`)

### Test framework
Only `src/agents/__tests__/quotes.test.ts` exists. Tests run via `npx tsx --env-file=.env.local <path>` — manual invocation, not a test runner. No vitest/jest installed. The pre-commit hook runs `uv run pytest` which skips TS entirely.

### Agent architecture: Option B transition is pre-wired
`src/agents/index.ts` already exports `rootAgent` as an alias for `accountingAgent`. Switching to multi-agent only requires making `rootAgent` a real `LlmAgent` router and registering sub-agents — the export interface stays unchanged.

### `@google/adk` version
Currently `^0.5.0`. Multi-agent (sub_agents + LLM routing) is supported in 0.5.x. No version bump required for Option B.

---

## Part 0 — Hooks: TypeScript Coverage [Do Before Code Changes]

These hooks protect the TS codebase the same way the Python hooks protect `src/agents/`. Add them to `.claude/settings.json` alongside the existing Python hooks.

### 0a. TypeScript type check (PostToolUse)

```bash
path=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.file_path // empty')
[ -z "$path" ] && exit 0
echo "$path" | grep -qE '/v2/ts_google_adk/src/.*\.(ts|tsx)$' || exit 0
cd /Users/ramsey.wise/Workspace/v2/ts_google_adk
npx tsc --noEmit 2>&1 | grep -E 'error TS' | head -5 >&2
exit 0  # advisory only — tsc errors shown but don't block
```

### 0b. ESLint check (PostToolUse)

```bash
path=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.file_path // empty')
[ -z "$path" ] && exit 0
echo "$path" | grep -qE '/v2/ts_google_adk/src/.*\.(ts|tsx)$' || exit 0
cd /Users/ramsey.wise/Workspace/v2/ts_google_adk
npx eslint --fix "$path" 2>&1 | head -10 >&2
exit 0
```

### 0c. No console.log in src/agents/ (PostToolUse, blocking)

```bash
path=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.file_path // empty')
[ -z "$path" ] && exit 0
echo "$path" | grep -qE '/v2/ts_google_adk/src/agents/.*\.(ts|tsx)$' || exit 0
line=$(grep -n 'console\.log(' "$path" 2>/dev/null | grep -v '// noqa' | head -1 || true)
[ -n "$line" ] && { echo "[no-console-log] use structured error returns or remove: $line" >&2; exit 2; }
exit 0
```

### 0d. SDK pattern lint for TS (PostToolUse, blocking)

Checks two rules:
- No hardcoded model strings outside `accounting-ts` (the agent definition file)
- No bare `new LlmAgent(` outside `accounting-ts` (must use the agent file)

```bash
path=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.file_path // empty')
[ -z "$path" ] && exit 0
echo "$path" | grep -qE '/v2/ts_google_adk/src/.*\.ts$' || exit 0
echo "$path" | grep -qE 'accounting-ts$' && exit 0  # allow in agent definition
issues=""
line=$(grep -n 'model.*gemini-\|model.*claude-' "$path" 2>/dev/null | grep -v '// noqa' | head -1 || true)
[ -n "$line" ] && issues="$issues  [sdk-model] hardcoded model string — use settings: $line\n"
[ -n "$issues" ] && { printf "TS SDK lint violations in %s:\n%b" "$path" "$issues" >&2; exit 2; }
exit 0
```

### 0e. Tool count guard (PostToolUse, advisory)

Warns when the accounting-ts tool array length approaches the Gemini Flash degradation threshold.

```bash
path=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.file_path // empty')
[ -z "$path" ] && exit 0
echo "$path" | grep -qE 'accounting-ts$' || exit 0
count=$(grep -c 'FunctionTool\|fetchSupportKnowledge\|inviteUser' "$path" 2>/dev/null || echo 0)
[ "$count" -gt 22 ] && echo "Tool count advisory: $count tools in accounting-ts — Gemini Flash degrades at 25+. Consider agent split." >&2
exit 0
```

### 0f. Extend review_gate.sh to cover .ts/.tsx

Change line 25 of `review_gate.sh`:
```bash
# Before:
echo "$path" | grep -qE '\.(py|yaml|yml|toml|json|sh)$' || exit 0
# After:
echo "$path" | grep -qE '\.(py|ts|tsx|yaml|yml|toml|json|sh)$' || exit 0
```

### 0g. Pre-commit: run tsc + TS tests

Extend the Bash PreToolUse `git commit` hook to also run TS type check:
```bash
cmd=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.command')
echo "$cmd" | grep -qE 'git commit' || exit 0
# Only if TS project files staged
git diff --cached --name-only | grep -qE '^v2/ts_google_adk/' || exit 0
cd /Users/ramsey.wise/Workspace/v2/ts_google_adk
npx tsc --noEmit 2>&1; rc=$?
[ $rc -ne 0 ] && { echo 'TypeScript type errors — fix before committing.' >&2; exit 2; }
exit 0
```

### Implementation note
These hooks should be added as new entries in the `PostToolUse` Write|Edit matcher array (0a–0e) and the `PreToolUse` Bash matcher array (0g), and `review_gate.sh` edited for 0f. They live in `.claude/settings.json` or as separate `.claude/hooks/ts_*.sh` scripts following the existing pattern.

---

## Part 1 — Missing Execution Tools

### Tranche A: Bills (Expenses) — Add First

Billy.dk bills are the supplier-side mirror of invoices. These unlock the `expenseManagement` quick action.

| Tool | Billy.dk API | Notes |
|---|---|---|
| `list_bills` | `GET /v2/bills` | Filter by state, date, supplier |
| `get_bill` | `GET /v2/bills/{id}` | Lines + supplier sideloaded |
| `create_bill` | `POST /v2/bills` | Needs defaultExpenseAccount lookup |

**Schema change required:** `tableType` in `accounting-schema.ts` gains `"bills"` enum value.

**New tool file:** `src/agents/tools/bills.ts` — follows same `FunctionTool` pattern as `invoices.ts`.

**Tool count after Tranche A:** 21. Still under the 25-tool degradation threshold.

**Quality gate before Tranche B:** After adding Tranche A, test the agent on:
1. A multi-turn invoice+customer creation flow (regression check on existing tools)
2. Bill listing and creation
3. The `get_invoice_summary` financial overview query

Only proceed to Tranche B if response quality is acceptable.

### Tranche B: Transactions, VAT, Reports — Add After Quality Gate

#### 1b. Transactions / Bank Reconciliation (Read-Only)

| Tool | Billy.dk API | Notes |
|---|---|---|
| `list_transactions` | `GET /v2/bankTransactions` | Filter by account, date, state |
| `get_unmatched_transactions` | `GET /v2/bankTransactions?isMatched=false` | Primary reconciliation surface |

Agent guides to Transactions page (`navButtons: route: "transactions"`), does not attempt automated matching.

**New tool file:** `src/agents/tools/transactions.ts`

#### 1c. VAT Declarations (Read-Only)

| Tool | Billy.dk API | Notes |
|---|---|---|
| `list_vat_declarations` | `GET /v2/vatDeclarations` | Period, state, amounts due |
| `get_vat_declaration` | `GET /v2/vatDeclarations/{id}` | Full breakdown by VAT type |

**New tool file:** `src/agents/tools/vat.ts`

#### 1d. Financial Reports (Read-Only)

| Tool | Billy.dk API | Notes |
|---|---|---|
| `get_profit_and_loss` | `GET /v2/reports/profitAndLoss` | Period + currency params |
| `get_balance` | `GET /v2/reports/balance` | Balance sheet as of date |
| `get_aged_debtors` | `GET /v2/reports/debtors` | AR aging (30/60/90+ days) |

**New tool file:** `src/agents/tools/reports.ts`

**Tool count after Tranche B:** 28. At this point the agent split (Part 2, Option B) is no longer optional — it is blocking.

---

## Part 2 — Agent Design: Split at 28 Tools

At 28 tools the agent must be split. The existing `rootAgent` alias in `index.ts` makes this a contained change.

### Target architecture (Option B)

```
rootAgent (LlmAgent — routes only, no tools, no outputSchema)
  ├── accountingAgent  (execution: invoices, bills, customers, products, quotes — ~12 tools)
  ├── analystAgent     (insights: reports, summaries, VAT, transactions — ~8 tools)
  └── helpAgent        (knowledge: fetchSupportKnowledge — 1 tool)
```

### Routing heuristic (rootAgent instruction)

- "create", "edit", "send", "invite", "add", "record" → `accountingAgent`
- "analyze", "compare", "how much", "trend", "forecast", "who owes", "P&L", "balance", "VAT", "reconcil" → `analystAgent`
- "how do I", "what is", "explain", "support", "help", "where can I find" → `helpAgent`

### Implementation steps

1. Create `src/agents/accounting.ts` (rename from `accounting-ts` logic) — keeps execution tools only
2. Create `src/agents/analyst.ts` — reports, VAT, transactions, getInvoiceSummary
3. Create `src/agents/help.ts` — fetchSupportKnowledge + escalation instruction
4. Create `src/agents/root.ts` — routing-only `LlmAgent` with `sub_agents: [accountingAgent, analystAgent, helpAgent]`
5. Update `src/agents/index.ts` to export the new `rootAgent` — no other file changes needed

### Risks

- **Latency**: one extra LLM routing call per turn. Acceptable if routing is correct >95% of the time.
- **Cross-mode turns**: "create an invoice, then explain my P&L" splits across agents. The ADK runner maintains session history — the second agent has context from the first. Test this explicitly.
- **outputSchema**: routing agent should NOT have `outputSchema` (it just delegates). Sub-agents keep their own schemas.

---

## Part 3 — Smart Features

### 3a. Proactive Status Summary

Add `get_status_summary` tool that consolidates:
- Overdue invoices count (from `list_invoices` with `state=approved&isPaid=false&dueDate<today`)
- Unmatched bank transactions count (from `get_unmatched_transactions`)
- Next VAT deadline

Surfaced on session start (first turn, no user message) and when user asks for a status check.

**Implementation:** New tool in `src/agents/tools/status.ts`. Belongs in `accountingAgent` (or `analystAgent` after split).

### 3b. Context-Aware Object Interaction

`parentUrl` is already passed via `postMessage` and threaded through `useChat`. Currently unused beyond logging.

**Enhancement:** Parse `parentUrl` in the API route and inject a context prefix before the user message:
```
[Context: User is on /invoices/INV-2024-00042]
```

**Security note:** The regex must be strict — extract only known resource types and numeric/UUID IDs, never pass raw URL segments. Example pattern: `/(invoices|bills|quotes|clients|vat-declarations)\/([A-Za-z0-9_-]{6,})`.

**Implementation:** Extract in `src/app/api/chat/route.ts` (or equivalent), inject as a `context_hint` prefix. Agent instruction gains a "Context-Aware Lookup" section.

### 3c. Receipt Upload (Navigation-Only)

Correctly scoped to Level 1. Mark `uploadReceipt` quick action as navigation-only. No tool implementation needed. Close this item from the missing-tools backlog.

### 3d. Frustration → Feedback Pipeline

The `contactSupport: true` path already generates an Intercom summary. Feed frustrated sessions into the `message_feedback` table (alongside thumbs-down) so they appear in the eval pipeline.

---

## Part 4 — Infrastructure

### 4a. Session Namespace

If the Python port (`py-copilot-service`) and this TS service share the same Postgres instance during the comparison phase, the ADK session tables must be namespaced. Verify the TS `DatabaseSessionService` config uses an `app_name` or equivalent key of `"copilot-ts"`. The Python service uses `"copilot-py"`. Without this, session records from both services collide.

### 4b. Knowledge Tool Future: RAG Swap

`fetchSupportKnowledge` currently calls Bedrock KB directly. The Python plan's Phase 2 replaces this with the playground LangGraph CRAG endpoint (`POST /query`). The same swap applies to TS. **Constraint:** the tool signature and return shape must stay identical so the agent instruction requires no changes. When the playground RAG endpoint ships, this is a one-line body swap in `src/agents/tools/support-knowledge.ts`.

### 4c. Session Summary API

`navigation.ts` calls `/va-agents/api/sessions/{sessionId}/summary`. Add a `GET /api/sessions/[sessionId]/summary` Next.js route that:
1. Loads session history from the session store
2. Runs a one-shot ADK call with `helpAgent` (no tools), short "summarize for support agent in 3 bullets" instruction
3. Returns the summary JSON

### 4b. TS Test Coverage

Currently only `quotes.test.ts` exists (manual `npx tsx` runner, no test framework). Before adding new tools:
- Add a `vitest` or keep the `npx tsx` pattern consistently documented
- Add `__tests__/bills.test.ts`, `__tests__/reports.test.ts` following the `quotes.test.ts` pattern
- Extend the pre-commit hook (0g above) to run available test files

---

## File Change Summary (corrected)

| File | Change |
|---|---|
| `.claude/settings.json` | Add TS hooks (0a–0e, 0g) |
| `.claude/hooks/review_gate.sh` | Extend to `.ts\|.tsx` (0f) |
| `src/agents/tools/bills.ts` | New: `list_bills`, `get_bill`, `create_bill` |
| `src/agents/tools/transactions.ts` | New: `list_transactions`, `get_unmatched_transactions` |
| `src/agents/tools/vat.ts` | New: `list_vat_declarations`, `get_vat_declaration` |
| `src/agents/tools/reports.ts` | New: `get_profit_and_loss`, `get_balance`, `get_aged_debtors` |
| `src/agents/tools/status.ts` | New: `get_status_summary` |
| `src/agents/accounting-ts` | Add Tranche A tools; expand instruction for insight/knowledge modes |
| `src/agents/accounting-schema.ts` | Add `"bills"` to `tableType` enum |
| `src/agents/root.ts` | New (after split): routing LlmAgent |
| `src/agents/analyst.ts` | New (after split): insight-mode agent |
| `src/agents/help.ts` | New (after split): knowledge-mode agent |
| `src/agents/index.ts` | Update rootAgent export after split |
| `src/app/api/sessions/[sessionId]/summary/route.ts` | New: session summary for Intercom |

---

## Execution Order

1. **Part 0** — Add TS hooks (no code changes, pure config). Gate all subsequent work behind these.
2. **Part 1, Tranche A** — bills tools + schema + instruction update. Run quality gate.
3. **Part 1, Tranche B** — transactions, VAT, reports (only if quality gate passes).
4. **Part 2** — Agent split (required before or when tool count hits 28).
5. **Part 3a/3b** — Status summary + context-aware lookup.
6. **Part 4** — Session summary API + test coverage.

## Out of scope

- Automated reconciliation writes — read-only first
- VAT submission — read-only first
- Analyst persona as standalone surface (Option C) — design preserved in Part 2 for later promotion
- Feedback → eval export pipeline — deferred to after eval tooling decision
