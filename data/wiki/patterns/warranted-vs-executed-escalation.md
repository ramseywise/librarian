---
title: Warranted vs Executed Escalation
tags: [patterns, eval, pattern]
summary: "An escalation grader that mixes detection with judging and scans one side of the conversation conflates two events — the user asking for a human (escalation warranted) and the agent routing to one (escalation executed); attribute every signal to a side, let only agent-side signals set executed, and feed user-side signals to the judge as context."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/project-g/docs/documents/VIR-259-extend-escalation-grader.md
  - data/raw/claude-docs/project-g/docs/stakeholders/agent-comparison-findings.md
---

# Warranted vs Executed Escalation

Finding from auditing and rebuilding the escalation grader for a Danish-language support
agent (project-g). The original grader looked reasonable, scored plausibly, and was wrong in
a way no aggregate number exposed: it could not tell *who* escalated.

## The original shape — two jobs, one side

`EscalationGrader.grade()` mixed two responsibilities:

1. **Signal detection** — infer from the agent's response whether escalation happened.
2. **Appropriateness judging** — an LLM judge scoring whether escalating was the right call.

Detection was heuristic: any email address in the response (matched a user's own address
quoted back, example emails in KB articles), plus a bilingual keyword list substring-matched
against the response only. Three defect classes fell out:

- **No side attribution.** "Please reach out to our support team" (agent routing decision)
  and "I want to talk to a human agent" (user need) set the same boolean.
- **One-sided scan.** Only the response was scanned, so a user explicitly asking for a
  person was invisible unless the agent echoed it — a silent false-negative source.
- **Over-broad tokens.** `specialist` and `manager` fired on "you need a tax specialist" and
  "Manager settings" in the UI. Both were dropped; precision beat recall for these.

## The fix — attribute every signal to a side

| Flag family | Side | Scans | Effect |
|---|---|---|---|
| `explicit_human_request_{en,da}` | user | query + response | Injected into the judge prompt as a `human_request_note` — escalation is **warranted** |
| `escalation_keyword_{en,da}` | agent | response only | Contributes to `agent_escalated` — escalation was **executed** |
| `contact_email` (domain/local-part filtered), `contact_phone_da` | agent | response | Contributes to `agent_escalated` |
| `oos_intent` | query | query | Topics the agent fundamentally cannot handle (loans, refunds, account closure, payment rails, phishing) |

Two composite properties keep the semantics apart: `agent_escalated` (agent-side signals
only — drives `escalated=True/False`) and `escalated` (any side — explicitly *not* used for
the executed/warranted call). A user asking for a human while the agent answered normally is
correctly `escalated=False`; the judge is told escalation was warranted and scores the miss.

This lets the judge reason differently per case: *user asked for a human → escalation is
almost always warranted*; *agent escalated on its own → was the query actually complex
enough?* The EN/DA split is an implementation detail, not a semantic one.

Ambiguous phrases that appear on both sides ("human agent", "live agent") belong in **both**
families — each flag has an independent responsibility, so duplication is not a conflict. Leaving
them only in the user family meant agent-said instances never set `agent_escalated`.

## Precedence and gates

- **A structured self-report outranks heuristics.** The agent's own `contact_support: bool`
  field, when populated, overrides all regex detection; keywords are the fallback for older
  outputs or agents that do not fill it reliably.
- **Infrastructure failures bypass judging.** When `failure_reason` is a backend error or
  unknown, the grader short-circuits to a neutral 0.5 rather than judging a scenario the
  agent could not have handled.
- **Structural enforcement at runtime.** The comparison audit proposed the mirror image on the
  agent side: a post-process check that forces `contact_support=True` when the agent's own
  `relevance_score` is below a floor (0.35) and it forgot to set the flag — closing the gap
  between the prompt instruction and actual behaviour.

## One machine, two measurements

Because `contact_support` is the override, the caller decides what it means — no code change:

| Data | `contact_support` passed | `alignment` measures |
|---|---|---|
| Single-turn agent outputs | Agent's own field | Agent quality — was the decision right? |
| Labelled multi-turn golden set | Ground-truth label | **Grader calibration** — does the judge agree with GT? |

The same grader becomes a calibration harness for itself when fed labels instead of agent
output. See [[LLM Grader Calibration Insights]].

## Mining patterns from real conversations

Pattern extensions came from EDA over ~10.6K human-support conversations, not from guessing:
verbatim user phrasings for "transfer me / connect me / talk to a real person" in Danish
roughly doubled user-side recall. Two lessons:

- Accept a known false positive when the domain makes it rare (a Danish token meaning both
  "talk with" and "number with" — accounting queries use other words for amounts), and write
  the reasoning down.
- Some OOS is **structural** (a conversation-type label such as "ops action required" — 13% of
  conversations and the dominant escalation signal) and cannot be detected by query regex at
  all. Regex covers only intent-based OOS; a word like "cancel" that is in-scope for invoices
  and OOS for accounts must not be a standalone signal.

## See Also
- [[project-g Eval Architecture]] — instance-of (the Strand F friction/escalation grader this rebuilt)
- [[LLM-as-Judge Evaluation]] — extends
- [[Confidence That Is Not a Probability]] — extends (`relevance_score` as an escalation trigger)
- [[Safeguards Architecture — Five Protection Layers]] — extends
- [[RAG Eval Gate Contract]] — extends (infra-failure rows excluded from judging)
