---
title: Consequence-Flagged KB Audit
tags: [patterns, rag, eval, pattern]
summary: Before indexing a help-center corpus for a support chatbot, audit every article into four fields (topic, must-be-exact facts, conditions/exceptions, financial-consequence flag) — the pass surfaces a recurring taxonomy of corpus defects (conflicting, near-duplicate, outdated, placeholder, non-article IDs, time-decaying figures) and a list of "must not imply" negative constraints that retrieval alone will never enforce.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/chat-agent/docs/kb-analysis/intercom_kb_analysis.md
---

# Consequence-Flagged KB Audit

From the chat-agent project: an LLM-assisted structured audit of ~450 help-center
article IDs for a fintech/invoicing support chatbot (French market, banking + invoicing +
company-creation + tax content). The audit was done before retrieval tuning, and it
turned out to be the cheapest way to find what the chatbot would get wrong.

## The per-article schema

Every article gets the same four fields — nothing else:

1. **Topic** — one line.
2. **Key facts a chatbot must get exactly right** — numbers, dates, plan names, limits,
   UI paths, deadlines. Not a summary: the values whose paraphrase would be an error.
3. **Conditions / exceptions / edge cases** — plan gating, eligibility, "only if",
   non-retroactivity, jurisdiction scope.
4. **Financial-consequence flag** — None / Low / Moderate / HIGH (/ VERY HIGH), with a
   one-clause statement of *what wrong answer causes what harm* ("wrong first filing month →
   late-declaration penalties").

A closing table lists only the HIGH-risk articles with that harm clause. That table, not the
per-article dump, is the actionable output: it becomes the eval priority list and the
`financial_risk` stratum in the golden set (see [[Synthetic Dataset Generation for RAG Eval]]).

## What the audit surfaces

Distribution in this corpus: roughly 195 "None", 70 "Low", ~46 HIGH flags. The defects
found fall into a stable taxonomy that should be expected in any vendor help center:

| Defect class | Example shape | Consequence for RAG |
|---|---|---|
| **Conflicting articles** | Two articles disagree on which plans include a feature | Retriever returns either; answer depends on chunk order. Pick an authoritative article and suppress the other. |
| **Near-duplicates** | Same procedure in two articles, one with a missing special-case list | Inconsistent answers across rephrasings ([[RAG Knowledge Preparation]] consistency pass) |
| **Outdated / legacy** | Legacy plan names and prices, defunct agencies, a tax guide from years ago with specific form box numbers | Confident, well-cited, wrong. The retriever has no staleness signal. |
| **Time-decaying figures** | Annual revenue thresholds, contribution rates | Even a correct article goes stale yearly — answer must carry "verify current figure" |
| **Placeholder / test / stub** | Formatting-template articles, "Untitled", "Draft", stubs with literal `xxxx` | Must be excluded from the index; a stub on a high-stakes topic is worse than no article |
| **Non-article IDs** | Collection IDs and a regulatory registration number that look like article IDs | Inflates corpus counts; breaks URL-cited ground truth |
| **Silent-failure facts** | Unsupported payment instruments rejected with no notification; untagged transactions silently excluded from an estimate | High harm because the user never sees an error — the chatbot is the only warning |

## Negative constraints are the hidden spec

About two dozen articles yielded a **"chatbot must not imply…"** rule: a card payment
cannot be cancelled; an outgoing transfer is only cancellable before it reaches the network;
wrong-IBAN recovery is not guaranteed; business customers are excluded from the consumer
mediation path; uploaded receipts have no legal probative value. These are not retrievable
facts — they are absences a fluent model will fill with a plausible "yes, you can". They
belong in the system prompt or a guardrail checklist, and as adversarial golden items,
not just in the index.

## Rules

- **Audit before tuning.** A corpus ceiling (stale, duplicate, missing content) caps what
  any retriever can reach; see [[VA vs HCA Retrieval Evaluation]] where data-ops fixes
  dominated model-level gains.
- **Flag consequence, not difficulty.** A trivial fact with financial harm outranks a
  complex fact with none. The harm clause is what makes the flag reviewable.
- **Record the authoritative side of every conflict** in the audit itself, so the indexer
  and the eval set agree on ground truth.
- **Exclude, don't fix, at index time.** Placeholders, non-articles and superseded
  duplicates are filtered out; content fixes go back to the docs owner as a list.

## See Also
- [[RAG Knowledge Preparation]] — extends (concrete audit schema and defect taxonomy for the "remove redundant and outdated" and consistency steps)
- [[Synthetic Dataset Generation for RAG Eval]] — prerequisite-for (supplies the financial_risk stratum and authoritative-article choices)
- [[VA vs HCA Retrieval Evaluation]] — extends (explains where the corpus ceiling comes from)
- [[Silence Reads as Clean]] — extends (silent-failure facts are the user-facing analogue: no error shown, so the chatbot is the only signal)
