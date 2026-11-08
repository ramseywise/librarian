---
title: Jev Decision Model
tags: [infra, concept]
summary: "TypeSafe AI's proprietary hosted model returns typed decisions with probabilities instead of text; its speed and price gains are partly confirmed independently against named comparators, while accuracy and calibration vary by task, and no peer-reviewed evaluation was found."
updated: 2026-11-08
sources:
  - data/raw/web/2026-11-05-jev-typesafe-vendor-sources.md
  - data/raw/web/2026-11-05-jev-independent-evaluations.md
  - data/raw/web/2026-11-05-jev-practitioner-roundups.md
  - data/raw/web/2026-11-05-citation-check-corrections-jev-and-cascades.md
  - data/raw/web/2026-11-05-citation-check-corrections-third-pass.md
  - data/raw/papers/2026-11-05-li-2026-jev-as-judge.md
---

# Jev Decision Model

Jev is a proprietary model from TypeSafe AI, launched in early access on 15 September 2026. It takes
unstructured input and returns a typed decision with probabilities, restricted to a schema the caller
defines (all self-reported). TypeSafe calls this category "System One", a name it takes from Kahneman. That is the
vendor's label. This page separates what the vendor says from what others measured.
Several evaluations below test it as the first stage of a
[[Cheap-First Gating and Model Cascades|cheap-first cascade]].

## What the vendor says

All of this is TypeSafe describing its own product, as read on 2026-11-05.

- **Current version:** jev-latest resolves to jev-1.14.0, available from 14 October 2026 (self-reported).
- **Price:** $0.042 per million input tokens with output free, at launch on 15 September 2026 (self-reported). TypeSafe says it cannot prove this is not subsidised.
- **Speed:** 70–500 ms overall, with the LLMs it compares against at 3–329 s, stated as 40x–200x on queries of the shape it targets (self-reported).
- **Headline multiples:** 193.6x faster and 444.6x cheaper, which Vals reads as a comparison with GPT-6 Astra and Claude Fable 5.1 averaged. They come from four workflows TypeSafe wrote itself. It says it expects them to be at the high end of real gains and that some bias could exist (self-reported).
- **Limits:** a request holds 64k tokens and a question 32k, and a long-context header raises that to 262k. Takes PNG and JPEG images, with audio and video still to come (self-reported).
- **Primitives:** a Choice takes 1–255 criteria and has no built-in abstain; the docs suggest a none-of-the-above option or a companion Noul that asks whether any option fits, and prefer the Noul. A Score has up to 10 levels. Guidance says at least two, though the API schema gives a minimum of one. The docs also list Noul and Box (self-reported).
- **Confidence:** one number from 0 to 1 derived from the distribution; with three options it is (3 × largest probability − 1) / 2 (self-reported).

The vendor claims 0% hallucination, and the launch post says of that figure, "Our number is not
empirical." It reflects guaranteed schema matching. As [[Structured Output]] puts it, a schema
guarantees shape, not truth. A valid choice can still be the wrong one.

TypeSafe's eval page lists these results, read 2026-11-05 (self-reported). The reference labels average
what GPT-6 Astra and Claude Fable 5.1 said at high thinking, so the score is agreement with other
LLMs, not ground truth. These are the `workflow` route, each a mean of four workflows, with Haiku 4.5 and both DS v4 models left out.

| Model | Agreement | Cost as listed | Time |
|---|---|---|---|
| Jev | 67.8% | $0.0004 | 0.4 s |
| Opus 5 | 73.1% | $0.1761 | 37.8 s |
| Terra | 67.9% | $0.0304 | 10.1 s |
| Sol | 74.1% | $0.0836 | 23.3 s |
| Sonnet 5 | 67.8% | $0.1174 | 78.1 s |
| Luna | 66.8% | $0.0033 | 12.9 s |

The SDK is MIT (typesafe-sdk 0.7.5 on PyPI on 2026-11-05) and the model proprietary (self-reported). No weights,
detailed architecture description or vendor paper were found. TechCrunch reported on 18 September 2026 that
it is transformer-based and that people outside the company suspect an open-weight LLM beneath it, which is unconfirmed. The launch
FAQ says "Jev is neither small nor an LLM" (self-reported).

## What others measured

Vals AI (6 October 2026, not peer reviewed) tested Jev
1.13.0 among 12 systems. The preprints below are unrefereed, and were read as abstracts plus the passages quoted in the citation checks. These
tests predate the 1.14 release, apart from Subramanian's below.

| Source | Setup | Result |
|---|---|---|
| Vals | 400 claim-verification items from 10-Ks of 48 companies | Both Jev and GPT-6 Luna scored 0.975, for $0.02 and $0.08 per 1,000 cases |
| Vals | Preregistered LegalBench slice, 396 questions | Jev last of twelve on class-balanced accuracy: 0.730 against GPT-5.6 Terra's 0.932. Vals says the slice does not represent the full benchmark |
| Ibrahim & Zaki, Sep 2026 | 18 social science tasks, 7,977 items, 19 LLMs | Trailed each task's best LLM on 14 of the 15, median 11.6 macro-F1 points, at median 44 times lower measured cost than that LLM |
| Deußer et al., Sep 2026 | jev-1.13.0, 37 datasets, 346,009 requests | Scored 95–99% accuracy on SST-2, IMDB, ARC and HellaSwag |
| Li et al., Oct 2026 | Safety classification, no attack | Caught 62% of phishing emails, where GLM judges caught 77–81%; flagged 27% of benign requests |
| Zhong et al., Sep 2026 | Arithmetic problems, explicit rejection option | 99% accuracy when the answer is present, 7% correct rejection when absent; 79% with a threshold, keeping 97% when present |
| Subramanian, Oct 2026 (Scale AI author) | 14 decision models including Jev 1.14, as judges, 80–1,925 items per set | Jev 1.14 "attains the lowest calibration error of any judge (ECE 0.019)" |
| Tang & Zheng, Sep 2026 | 28 papers reviewed | Latency and cost gains stand out, while harder tasks still show accuracy gaps |

Practitioner notes are leads rather than evidence, with no audited method behind them. A Valyu guide
(September 2026) reports that Jev does not count reliably and treats dates as text. A roundup by xbill
(September 2026) reports probabilities rounded to 0.01.

## Where the sources disagree

- **Cost depends on the comparator.** On claim verification, Vals measured 1/498th of GPT-6 Astra's cost, close to the vendor's figure. Against GPT-6 Luna, Vals puts Luna at $0.08 per 1,000 cases on claim verification, which it calls about three times Jev's price. The rounded $0.02 and $0.08 look like a ratio of four, but its other figures imply about 3.3 by this wiki's arithmetic. Denney & DiGiuseppe (unrefereed, October 2026) saw Jev gain no cost edge on GPT-6 Luna when Luna was priced at OpenAI's batch rate. These can all be true because the comparators and price basis (list or batch) differ; Denney's task was not read.
- **Speed varies with setup.** Against GPT-6 Astra, Vals measured 194x with 32 judgments requested and 47x on single judgments under load, with an isolated single-call median about 0.10 s. The xbill roundup collects 0.5x to 12.1x in other setups, against whichever LLM each test used.
- **Calibration depends on the task.** TypeSafe describes the probabilities as calibrated (self-reported) and Deußer et al. agree, but Vals measured the lowest ECE of twelve on one task and the highest on another. Vals puts part of that rise down to mechanics, as error climbs when accuracy drops. Details are in [[Confidence-Gated Escalation]].

## Open questions

- Current waitlist status could not be confirmed.
- No vendor paper and no peer-reviewed evaluation were found.
- How version 1.14 performs beyond Subramanian's single-run, pilot-scale test.

## See Also
- [[Cheap-First Gating and Model Cascades]] — prerequisite-for (the pattern Jev is sold into)
- [[Confidence-Gated Escalation]] — related (how to set and check a threshold on it)
- [[Structured Output]] — prerequisite-for (shape is not truth)
- [[Three-Band Confidence Routing]] — related (the wider decision layer around a score)
- [[JEV-as-a-Judge Cascade]] — extends (a preprint that tests it as the first stage of a judge cascade)
