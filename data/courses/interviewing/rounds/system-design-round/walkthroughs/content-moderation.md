---
imported_hash: 483880651b382799
title: Design a content / policy-violation moderation system
summary: content-moderation-walkthrough · serving · medium
order: 94
kind: reading
section: System design round / Walkthroughs
source: sisyphus/interviewing/rounds/system-design-round/walkthroughs/content-moderation.md
---

# Design a content / policy-violation moderation system

`content-moderation-walkthrough` · serving · medium

## 1. clarify

**Interviewer:** What do you clarify first? Frame the policy, timing, error costs, and modality.

<details><summary>Reference</summary>

Clarify before designing. (1) Policy taxonomy: what counts as a violation? Pin down
categories — a standard set is hate, harassment, sexual content (with a hard line on
minors), violence, self-harm, and illicit activity, each often with sub-categories.
(2) Timing: must we block BEFORE publish (synchronous, latency-critical) or can we
review AFTER publish (async)? Different products differ per category. (3) Error costs:
what's worse here — false positives (censoring legit speech, angry users) or false
negatives (harmful content stays up)? This sets thresholds and varies by category and
region. (4) Modality: text only, or images/video too? (5) Scale, languages, and
adversarial pressure. State assumptions and confirm. [openai-moderation, igotanoffer, threshold-opt]

</details>

## 2. high-level

**Interviewer:** Sketch the architecture. What's the overall shape of a moderation pipeline?

<details><summary>Reference</summary>

A tiered CASCADE, cheap-to-expensive. Content in -> (1) fast, cheap CLASSIFIERS score
it across policy categories, returning per-category scores. (2) A DECISION layer
applies per-category thresholds: clearly safe -> allow; clearly violating -> auto-block/
remove; UNCERTAIN (near threshold) -> escalate. (3) Escalated/ambiguous items go to a
stronger (and costlier) model or LLM, and the hardest or appealed cases go to a HUMAN
REVIEW queue. (4) Human decisions and user appeals feed a FEEDBACK LOOP that retrains
the classifiers. Cross-cutting: this runs both PRE-publish (sync, for high-risk
surfaces) and POST-publish (async sweep), with observability on precision/recall and
latency. Grounding the whole thing: the cascade keeps expensive models off the ~98% of
easy content. [filter-refine, human-raters, threshold-opt]

</details>

## 3. deep-dive

**Interviewer:** Classification: what models do the actual detection, and how do you handle images and many languages?

<details><summary>Reference</summary>

Stage one is a lightweight, high-throughput classifier that maps content to per-category
scores (0-1) and a flagged/not-flagged decision — like OpenAI's Moderation API with its
~13-category taxonomy. Make it MULTIMODAL (text + images; some categories such as
violence/self-harm/sexual need image support) and MULTILINGUAL — moderation quality
drops badly in low-resource languages, so a model tested and tuned across many
languages (OpenAI reports gains across ~40) matters. For ambiguous cases, escalate to a
larger multimodal LLM that reasons with policy context. Keep stage one cheap so it can
run on all traffic in real time; reserve the expensive model for the small uncertain
slice. [openai-moderation, openai-mm-moderation, filter-refine]

</details>

## 4. deep-dive

**Interviewer:** Thresholds & decisions: how do you turn scores into allow / block / review, given policies differ?

<details><summary>Reference</summary>

Don't hard-code one global cutoff. Policies vary by COUNTRY, product surface, and
category, so tune PER-CATEGORY, per-surface THRESHOLDS that map scores to actions:
below a low threshold -> allow, above a high threshold -> auto-act, in between -> route
to human review. Set thresholds from the error-cost trade-off: for a high-harm category
(e.g. sexual content involving minors) bias toward recall (catch everything, tolerate
false positives); for subjective speech bias toward precision to avoid over-censoring.
Optimizing the handoff thresholds lets you adapt to policy changes WITHOUT relabeling
and retraining every time. The pre-filter should be high-recall (forward all likely
violations) and high-specificity (don't flood reviewers with benign content).
[threshold-opt, human-raters]

</details>

## 5. deep-dive

**Interviewer:** Human-in-the-loop & feedback: how do humans and the ML system reinforce each other?

<details><summary>Reference</summary>

Humans handle the ambiguous middle and appeals; the ML handles volume. Route uncertain
and appealed items to a review queue, and use LLM assistance to make reviewers faster
and more consistent — studies show LLM-assisted review reaching ~90% agreement with
human verdicts and improving rater capacity ~41.5% and precision/recall by ~9-11
points, augmenting rather than replacing humans. Every human decision becomes a LABEL:
feed it back to retrain and recalibrate the classifiers (active learning on the
hardest, most informative cases). This closes the loop so the system keeps up with new
slang and evasion. [human-raters, filter-refine]

</details>

## 6. tradeoffs

**Interviewer:** Adversarial evasion and fairness: what goes wrong on hard content, and how do you handle it?

<details><summary>Reference</summary>

Moderation systems systematically UNDER-moderate implicit/coded hate (spelled around
filters, dog-whistles) and OVER-moderate counter-speech and reclaimed slurs, because
they lean on surface identity terms rather than CONTEXT — so they're brittle to
linguistic variation and deliberate evasion. Mitigations: use context-aware models (not
keyword lists), continuously mine adversarial/evasion examples into training, red-team
across languages and communities, and monitor error rates by group to catch unfair
over-blocking. Accept that this is an arms race: attackers adapt, so retraining cadence
and fresh adversarial data are part of the design, not an afterthought. [lost-in-moderation, human-raters]

</details>

## 7. tradeoffs

**Interviewer:** What breaks at scale, how do you detect it, and how does it degrade gracefully?

<details><summary>Reference</summary>

Name failure modes AND detection. (1) Precision/recall drift as content evolves: monitor
per-category precision/recall against human-labeled samples; retrain on fresh labels.
(2) Latency on the pre-publish path under spikes: monitor p95; degrade by allowing
borderline content through to async review rather than blocking publishing. (3) Cost
blowup from over-escalating to the expensive model: watch the escalation rate and tune
thresholds so only the uncertain slice escalates. (4) Human-review backlog: monitor queue
depth; auto-act on high-confidence cases to protect reviewer capacity. (5) Fairness /
over-censoring: monitor appeal-overturn rate by category and group. (6) Evasion spikes:
alert on sudden distribution shifts. Close with the biggest risks (evasion, fairness)
and what you'd measure and improve first. [threshold-opt, filter-refine, lost-in-moderation, human-raters]

</details>

## Sources

- [OpenAI API — Moderation guide](https://developers.openai.com/api/docs/guides/moderation)
- [OpenAI — Upgrading the Moderation API with a multimodal model](https://openai.com/index/upgrading-the-moderation-api-with-our-new-multimodal-moderation-model/)
- [Filter-And-Refine: A MLLM Cascade for Industrial-Scale Content Moderation (arXiv)](https://arxiv.org/abs/2507.17204)
- [Supporting Human Raters with LLM Detection of Harmful Content (arXiv)](https://arxiv.org/abs/2406.12800)
- [Reliable Decision from Multiple Subtasks through Threshold Optimization (arXiv)](https://arxiv.org/abs/2208.07522)
- [Lost in Moderation: How Commercial Content Moderation APIs Over- and Under-Moderate (arXiv, CHI 2025)](https://arxiv.org/abs/2503.01623)
- [IGotAnOffer — Generative AI System Design Interview](https://igotanoffer.com/en/advice/generative-ai-system-design-interview)
