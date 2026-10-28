---
title: Technical Breadth Round Playbook
tags: [interview, reference]
summary: "The ML/LLM breadth round grades the follow-up, not the definition. Rehearse every concept as a 60-second answer plus a different layer one level deeper. Use the honest-gap move instead of bluffing. Drill trade-off pairs by their deciding axis rather than their verdict. Audit every resume claim two levels deep."
updated: 2026-10-17
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--technical-questions.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--technical-questions--README.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--technical-questions--study-guide.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--technical-questions--questions.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--technical-questions--mcq-bank.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--technical-questions--sources.md
---

# Technical Breadth Round Playbook

A 30–45 minute verbal fluency check, often folded into the first half of another round.
2026 loops front-load LLM-era topics: attention, tokenization, RLHF/DPO, RAG vs fine-tuning,
hallucination, context windows, CoT, sampling. Classical ML (bias–variance, metrics) is the
sanity-check layer, weighted by role. Typical screen lists run "What is RAG? Graph RAG? CoT?
Reflection? How do you manage memory and context? How do you stop hallucination?" The format
is breadth first, then depth on whatever you claim. Domain content lives in the per-domain
guides ([[LLM Fundamentals Interview Study Guide]], [[RAG Interview Study Guide]],
[[Agents Interview Study Guide]], [[Evals and Observability Interview Study Guide]]); this
page is the method.

## 60 seconds, then one layer deeper

| Mode | Contents | Budget |
|---|---|---|
| **60-second** | One definition sentence → mechanism in plain terms → one example or implication. Stop. | ~60 s |
| **One deeper** | The underlying mechanism or math → the failure mode the short answer ignores → the trade-off it creates | ≤90 s |

**The signal is in the transition.** "Can you go deeper?" should reach a *different layer*
(attention → KV cache; RLHF → reward hacking → DPO), not a longer version of the first answer.
Memorized definitions fall apart at the second "why?". That gap separates candidates who
took a course from candidates who built something. Drill by covering the deeper column and
answering cold.

## The honest-gap move

*"My understanding there is fairly surface-level. I know [the shape], but I haven't gone deep
on [the mechanism]. I'd approach it by [method]. What I have solid experience with is [adjacent
thing]."* Use it when answering would mean speculating for more than one sentence. Don't use
it for core topics of the target role. Those are prep gaps to close beforehand. A confident,
detail-free answer is the tell interviewers listen for, and most candidates bluff, so honesty
stands out.

## Trade-off pairs: drill the axis, not the call

The verdict depends on context. The **axis that decides it** is what lets you reason live.
Flashcard front: the pair. Back: the axis plus a one-line default.

| Pair | Deciding axis | Default |
|---|---|---|
| RAG vs fine-tuning | Missing knowledge or missing behaviour? | RAG for knowledge, FT for behaviour |
| LoRA vs full FT | Compute and data volume | LoRA unless both are large |
| Precision vs recall | Cost of a false positive vs a false negative | Domain-dependent |
| On-prem vs API | Data sensitivity, cost at scale, ops burden | API until compliance or scale forces on-prem |
| Dense vs sparse retrieval | Semantic vs exact match | Hybrid |
| Bi- vs cross-encoder | Speed vs accuracy | Bi to retrieve, cross to rerank |
| Single vs multi-agent | Context length + specialization / parallelism | Single agent unless the task outgrows the window |
| Workflow vs agent | Predictability vs flexibility | Workflow until decisions can't be enumerated |
| LLM judge vs human eval | Scale vs ground-truth quality | Judge for scale, human to calibrate |
| RLHF vs DPO | Need for online exploration | DPO |
| Injection defence: structural vs filter | Completeness vs ease | Structural first, filter as a supplement |
| F1 vs PR-AUC | Class balance | PR-AUC when imbalanced |

## Claim audit

Everything on the resume is in scope. For each ML/LLM line, answer cold: what exactly you
built (stack, scale), why you made the key decisions, what didn't work, the metric, and one
more layer for "go deeper?". If you can't answer, go deeper on it or soften the claim.

## Drill design note

The multiple-choice bank that goes with this round builds its distractors from the
confusions each domain guide flags (prefix vs semantic caching, pass@k vs pass^k, CRAG vs
Self-RAG). You review the rationale for questions you got wrong *and* for questions you
guessed right, because a lucky guess teaches nothing. A one-sentence, under-ten-seconds
"distinction drill" covers the same pairs aloud. See [[Graded Rehearsal Drill Harness]] for
the rehearsal side.

## Role weighting

AIE: LLM fundamentals → RAG → agents → context/cost → evals → security → classical ML.
MLE: classical ML first, then LLM fundamentals and evals. DS: the round folds into the
stats/SQL screen. FDE: context/cost and security first.
[[AI Role Interview Loop Map]] has the full matrix.

## See Also
- [[AI Role Interview Loop Map]] — instance-of
- [[LLM Fundamentals Interview Study Guide]] — prerequisite-for
- [[RAG Interview Study Guide]] — prerequisite-for
- [[Graded Rehearsal Drill Harness]] — extends (how the banks get rehearsed)
- [[Durable vs Performative Knowledge Split]] — instance-of (method here, content in domain guides)
- [[Recruiter Screen Playbook]] — extends (one-liners named there get audited here)
