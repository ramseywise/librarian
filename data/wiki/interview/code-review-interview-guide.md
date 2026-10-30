---
title: Code Review Interview Study Guide
tags: [interview, reference]
summary: "Method guide for the live code-review round — orient on intent and contracts first, read in consequence order (security → correctness → maintainability → style), severity and confidence as independent axes, questions over verdicts, and the agent-PR checklist whose sharpest item is a safeguard that exists only in prose."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--code-review-round--README.md
  - data/raw/repos/sisyphus/interviewing--rounds--code-review-round--README.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--code-review-round.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--code-review-round--study-guide.md
  - data/raw/repos/sisyphus/interviewing--rounds--code-review-round--study-guide.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--code-review-round--questions.md
  - data/raw/repos/sisyphus/interviewing--rounds--code-review-round--questions.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--code-review-round--sources.md
  - data/raw/repos/sisyphus/interviewing--rounds--code-review-round--sources.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--code-review-round--examples--README.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--code-review-round--examples--ai-generated.md
  - data/raw/repos/sisyphus/interviewing--rounds--code-review-round--examples--ai-generated.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--code-review-round--examples--conventions.md
  - data/raw/repos/sisyphus/interviewing--rounds--code-review-round--examples--conventions.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--code-review-round--examples--correctness.md
  - data/raw/repos/sisyphus/interviewing--rounds--code-review-round--examples--correctness.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--code-review-round--examples--security.md
  - data/raw/repos/sisyphus/interviewing--rounds--code-review-round--examples--security.md
---

# Code Review Interview Study Guide

30–60 min reviewing a PR or small service live (or async, discussed in the round). Mostly
senior/staff loops; AIE variants increasingly hand you AI-generated code, and "reviewing
generated code is now a core job skill" is a fair thing to say out loud. The question being
asked: **do you have a method, or just an eye?** The worked drill is
[[Code Review Drill — SANYI]].

## The method

1. **Orient before judging.** The first question is "what is this change supposed to do,
   and what contracts/invariants does the code it touches declare?" — PR description, then
   the surrounding file's conventions.
2. **Read in consequence order:** security & data boundaries (auth, PII, irreversible
   writes) → correctness & interfaces (signature/schema drift, error paths) →
   maintainability (hardcoded tunables, convention breaks) → style last, if at all.
3. **Hunt the dangerous class** — changes where every line looks innocent: a flag wrapped
   around a safety check, a threshold inlined "temporarily", a literal `0.42` ten lines below
   an env-driven-constant convention. Line-by-line reading approves these; diffing against
   conventions and contracts flags them.
4. **Severity from consequence, not taste:** invariant → blocker; interface drift →
   warning; tunable made rigid → info; style → nit or silence.
5. **Confidence is a separate axis:** *verified* (reproduced or traced end to end),
   *supported* (code path or docs strongly indicate it; an assumption remains),
   *hypothesis* (plausible mechanism, key context missing). A suspected leak is
   high-severity/low-confidence until traced. A high-severity hypothesis is phrased as a
   question or test request — "this could double-charge if the provider retries — worth
   checking?" — never asserted. A question is how you *communicate* a hypothesis, not a
   fourth tier. Same split as [[Merge Impact and Evidence State]], and as Conventional
   Comments' `issue`/`question` vs `blocking`/`non-blocking`.
6. **Report news, not history.** Don't re-litigate pre-existing debt; a reviewer who flags
   everything gets muted.
7. **Voice:** questions over verdicts (but not accusations dressed as questions),
   acknowledge good decisions, propose the mechanical fix with each flag.

## Recurring defect classes (from the worked examples)

| Pass | Class | Shape |
|---|---|---|
| Security | Tool over-permissioning | wildcard commands, write where read suffices, credentials in metadata |
| Security | Trust-boundary violation | untrusted content placed in the system/developer message |
| Security | Auth dropped by refactor | a decorator removal silently removes the permission check |
| Security | Memory poisoning | user input persisted to long-term memory with no validation or TTL |
| Correctness | Tool schema drift | function signature changed, tool schema not — the agent can no longer call it |
| Correctness | Swallowed error in an agent loop | the agent gets a fake success, compounds it across turns, and with no circuit breaker it loops (denial-of-wallet) |
| Correctness | Shared-schema drift | a renamed field on a shared type; grep the whole repo, because a diff-scoped read never shows the downstream serializer that silently drops it |
| Maintainability | Hardcoded tunable / prompt in code | threshold or prompt string moved out of the swappable config layer |
| Maintainability | Eval threshold lowered | quality bar changed with no calibration evidence or version bump |
| AI-generated | Hallucinated API | a plausible parameter that doesn't exist, or an intent/return-type mismatch |
| AI-generated | Demo-grade RAG | no relevance filter, no attribution, no token budget |

## Stock questions

- **"Tests pass and it lints clean — approve?"** Checks verify what is *encoded*, not what is
  *intended*: still look for contract/convention violations, missing edge cases, interface
  drift, security boundaries.
- **"How do you review a 2,000-line PR?"** Push back on size first; if it can't split, read
  the description, pick the high-risk files (entry points, writes, auth, interface changes),
  review those in consequence order, skim the rest, zero style feedback, and **say explicitly
  what you reviewed deeply vs. skimmed**.
- **"What do you check first in an agent PR?"** Tool permissions → trust boundaries →
  irreversible actions (HITL) → memory writes → error recovery → tunables in code →
  **documented safeguards without code backing**: a prompt or doc that *claims* an
  escalation path or validator — go find the deterministic code path, or it is a sentence the
  model can ignore under adversarial input. This is the item a line-by-line reviewer misses;
  see [[Agent Quality Review Checklist]].
- **Know your linter boundary** — refusing to spend review time on what a formatter catches is
  itself a maturity signal.

## Practice

Review merged OSS PRs blind and compare with the real comments; time-box 5 min orientation →
15 min consequence-ranked review → 5 min written summary with severity labels; prepare one
"small diff, lints clean, tests pass, convention violated" story.

## See Also
- [[Code Review Drill — SANYI]] — extends (the worked contract-diff example this method generalizes)
- [[Merge Impact and Evidence State]] — instance-of (the severity × confidence split)
- [[Agent Quality Review Checklist]] — extends (agent-specific review checks)
- [[Prompt Injection]] — prerequisite-for (trust-boundary findings)
- [[AI Role Interview Loop Map]] — extends
- [[Coding Challenge Interview Study Guide]] — extends (the reviewer lens graders apply to submissions)
