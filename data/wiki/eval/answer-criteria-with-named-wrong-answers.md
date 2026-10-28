---
title: Answer Criteria with Named Wrong Answers
tags: [eval, rag, pattern]
summary: "A per-topic answer rubric for a support RAG bot that lists, next to what a complete answer contains, the specific wrong answers to fail — and those wrong answers cluster into five predictable classes (collapsed distinctions, irreversibility, per-tier numbers, silent exclusions, capabilities the product lacks) worth seeding into any judge rubric or golden set."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/chat-agent/docs/kb-analysis/answer_quality_criteria.md
---

# Answer Criteria with Named Wrong Answers

Written for a customer-support RAG chatbot over a fintech help centre (French invoicing,
payments, cards, tax). Derived from an analysis of the knowledge base, the document gives
each of 15 topic areas two lists: **what a complete, correct answer contains**, and
**what a partial or wrong answer looks like**, stated as concrete claims to fail
("saying annual billing is available at sign-up", "giving only the bank's BIC for an
international transfer").

The second list is the useful one. "Correct" is open-ended; a named wrong answer is a
checkable assertion a judge or a regex can apply, and it encodes where the knowledge base
is easiest to misread.

## The five classes the wrong answers fall into

Across all 15 topics the failure lists reduce to a small set of shapes:

1. **Collapsed distinctions.** The KB distinguishes two cases and a fluent answer merges
   them: receiving vs. emitting e-invoices (different deadlines by company size); consumer
   vs. business direct debits (8-week contest window vs. no refund at all); price excluding
   vs. including VAT; a legally *required mention* of a penalty rate vs. *optional
   collection* of it. The wrong answer is the merged one.
2. **Irreversibility.** Facts where the answer must say "cannot be undone": a card blocked as
   lost is never reactivated, a deleted virtual card is gone, a sent invoice cannot be
   deleted (only countered with a credit note), annual billing is non-refundable. A helpful
   model defaults to suggesting recovery.
3. **Exact numbers that vary by tier.** Limits, fees and quotas per plan (instant-transfer
   caps with and without a primary device, ATM 30-day limits, replacement-card fees, foreign
   payment percentages). The wrong answer is usually a neighbouring tier's number.
4. **Silent exclusions.** A feature that looks universal but skips a subset: automatic VAT
   detection ignores transactions without an attached receipt. The wrong answer says the
   feature covers everything.
5. **Capabilities the product does not have.** No overdraft, no self-service account lock,
   no chequebooks, no foreign-currency balances, no personal accounts. A model fills the
   gap with what a typical bank offers.

Classes 2 and 5 are where a wrong answer causes direct financial or security harm (telling
a user to approve an unknown 3-D Secure prompt, or that a refund is possible), so they
deserve the strictest grading.

## How it plugs into the eval stack

- **Judge rubrics.** A per-topic "fail if the answer says X" list is a narrower, more
  reliable instruction than "is this answer correct?" — see [[LLM-as-Judge Evaluation]].
- **Golden-set authoring.** Each named wrong answer is a seed for an adversarial case whose
  reference answer must contain the distinction, the irreversibility, or the exact number —
  the same "specific, never generic" rule the [[Synthetic Dataset Generation for RAG Eval]]
  prompts impose on reference answers.
- **Time-bound facts.** Several criteria carry dates (reform deadlines, a verification
  scheme that started on a given day, a provider not yet on an official list "at time of
  writing"). Criteria derived from a KB snapshot go stale with it and need the same
  fingerprint-driven refresh as the dataset.

## See Also
- [[Golden Set Mechanics]] — extends (named wrong answers as adversarial case seeds)
- [[LLM-as-Judge Evaluation]] — extends (fail-if lists as the rubric)
- [[Synthetic Dataset Generation for RAG Eval]] — related (same bot; specific reference answers)
- [[Grounding Claim Methodology]] — related (grounded is not the same as complete; class 1 answers are often grounded)
