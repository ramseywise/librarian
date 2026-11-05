---
title: Cheap-First Gating and Model Cascades
tags: [infra, pattern]
summary: "Send each request to a cheap model and let a gate decide whether it escalates; published savings run from modest to large by task and date, simple baselines often match learned routers, and routers fail on unfamiliar or adversarial queries."
updated: 2026-11-05
sources:
  - data/raw/web/2026-11-05-model-cascades-routers-and-calibration.md
  - data/raw/web/2026-11-05-jev-independent-evaluations.md
  - data/raw/web/2026-11-05-citation-check-corrections-jev-and-cascades.md
  - data/raw/web/2026-11-05-citation-check-corrections-third-pass.md
---

# Cheap-First Gating and Model Cascades

A cascade tries a cheap model first and spends on a costlier one only when a gate says the
cheap answer will not do. The saving depends on two things: how many requests stop early, and
whether the gate can tell which ones are safe to stop. This wiki's view is that the second is the
hard part, covered in [[Confidence-Gated Escalation]].

The mechanism is old. Viola and Jones (CVPR 2001) chained increasingly complex classifiers so
that image background was discarded quickly and computation went to promising regions. Their
paper has nothing to do with LLMs; treating it as an ancestor of LLM gating is this wiki's
analogy.

## Where the gate sits

| Shape | What decides | Example |
|---|---|---|
| Answer, then score | A scorer reads the cheap answer; per-stage thresholds decide on escalation | FrugalGPT |
| Answer, then self-check | The small model verifies its own answer, which its authors note can be noisy | AutoMix |
| Route before answering | A classifier picks the model before any answer exists | RouteLLM, Hybrid LLM |
| Route by similarity | Vector match; a threshold miss returns no route | Aurelio Labs semantic-router (its README publishes no benchmark) |
| Typed decision model first | A schema-restricted model answers, with low-confidence items sent to an LLM | [[Jev Decision Model]] |

Fixed per-step tiering, as in [[Loop Engineering]], is the same idea with no gate: the step
decides the model, not the request. Anthropic's agent guidance describes routing as a workflow
pattern ([[Agentic Workflow Patterns]], December 2024) but gives no measured savings.

## What the savings look like

All are the authors' own figures, for their tasks, models and dates. None is a typical saving.

| Source | Setup | Reported result |
|---|---|---|
| FrugalGPT (May 2023, unrefereed arXiv preprint) | 12 LLM APIs at 2023 prices, narrow tasks | Against GPT-4: HEADLINES 98.3%, OVERRULING 73.3%. Against GPT-3: COQA 59.2% |
| RouteLLM (ICLR 2025) | GPT-4 against Mixtral-8x7B, at the paper's CPT(50%) and CPT(80%) points | Inverse of the GPT-4-call ratio against a random router (higher saves more), CPT(50%) then CPT(80%): 3.66 and 2.49 on MT Bench, 1.41 and 1.14 on MMLU, 1.49 and 1.27 on GSM8K. Quality at CPT(50%) was 95%, 92% and 87% of GPT-4's |
| AutoMix (NeurIPS 2024) | Self-verification cascade | Over 50% lower computational cost at comparable performance; the abstract read does not restate the baseline |
| Hybrid LLM (ICLR 2024) | Complexity router, against all-at-large | Quality drop at a 40% cost advantage: 0.0–0.2% for Llama-2 7b against 13b, 2.9–3.5% for Llama-2 13b against GPT-3.5-turbo, 10.3–13.8% for FLAN-t5 800m against Llama-2 13b |

RouteLLM's spread is the lesson: the best router on the same model pair saves more than twice
as much on one benchmark as on another, and each benchmark's figure comes from its own router and training data. A 2026
preprint (Ibrahim & Zaki, unrefereed, abstract read) escalated a decision model's low-confidence items to an LLM and
equalled or bettered that LLM on its own while costing a quarter to half as much, on computational social science tasks.

## Failure modes

- **Unfamiliar queries.** A router fed nothing but Arena data was no better than random on MMLU,
  where most questions fell outside what it had seen. Adding some 1,500 golden samples, under 2%
  of its training data, helped (RouteLLM). [[Drift Seen and Unseen in an Automated Router]]
  shows the classical version of this.
- **Attack.** Query-independent prefixes rerouted requests with 88% success in the worst white-box case,
  and less when transferred black-box, sending 1.5 times more queries to the strong model and so raising the victim's bill. A
  perplexity filter did not stop it (Shafran et al., unrefereed arXiv preprint, January 2025). Decision models used as judges can
  be turned too: a note injected into the judged text reversed 0–5% of correct verdicts for five models and 17–49% for
  nine (Subramanian, unrefereed, October 2026).
- **A weak first stage.** If the cheap stage has to defer most of the traffic, the gate saves
  little: see the LegalBench result in [[Confidence-Gated Escalation]].

## What argues against it

Two benchmarks, both unrefereed arXiv preprints, cut against routers. RouterBench (405k outcomes, 2024) found no predictive
router (KNN, MLP) significantly better than its Zero router, built from the individual models' convex hull. Simulated cascades did beat it when
the judge's error rate was at most 0.1 and fell off above 0.2, a result it calls a simulated upper limit. LLMRouterBench
(400K instances, 21 datasets, 33 models, 2026) found that several recent approaches, including the commercial OpenRouter,
do not outperform the best single model, and that binary routers such as Hybrid LLM and FrugalGPT struggle to save
while keeping its accuracy. Before training a router, compare it with the best single model on your own traffic.

## Open questions

- No industry post read gave measured production savings.
- How far the benchmark results carry over to answer-then-score cascades beyond FrugalGPT, which LLMRouterBench names.

## See Also
- [[Confidence-Gated Escalation]] — extends (how the gate's threshold is set and checked)
- [[Jev Decision Model]] — instance-of (a typed decision model as first stage)
- [[Three-Band Confidence Routing]] — prerequisite-for (the score-and-threshold decision layer)
- [[Drift Seen and Unseen in an Automated Router]] — related (what a frozen router's monitors can see)
- [[Verification Loops]] — alternative-to (cheap execution with the expensive model at the verification gate)
- [[Agentic Workflow Patterns]] — related (routing as a workflow shape)
- [[Context Engineering and Cost Interview Study Guide]] — related (model routing among the cost levers)
- [[LLM Inference Economics]] — prerequisite-for (where the price gap between models comes from)
