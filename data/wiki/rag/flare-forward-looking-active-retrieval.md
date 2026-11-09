---
title: FLARE Forward-Looking Active Retrieval
tags: [rag, pattern]
summary: "FLARE drafts the next sentence without retrieval and, only when a draft token is low-probability, uses that draft as the search query and regenerates the sentence; the paper reports gains on multi-hop QA and small ones on other long-form tasks (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-2023-emnlp-main-495.md
  - data/raw/papers/2026-11-07-jiang-2023-active-retrieval-augmented-generation.md
---

# FLARE Forward-Looking Active Retrieval

Jiang and colleagues (EMNLP 2023; the same paper appears in two extractions) ask whether a retrieval-augmented language model can itself choose the timing and the content of retrieval while writing a long answer, rather than fetching documents a single time from the input. They frame this as **active retrieval augmented generation**: a framework that interleaves retrieval and generation and actively chooses both the moment and the query. FLARE (Forward-Looking Active REtrieval augmented generation) is their inference-only instance. The paper's hypothesis is that a model should retrieve only when it lacks knowledge (low-probability tokens) and that the query should reflect what it is about to write, not what it already wrote.

## Mechanism

At each step the model drafts the next sentence with no retrieval. If every token in the draft has probability at or above a threshold theta, the draft is kept. If any token falls below theta, the draft becomes the basis for a query, retrieval runs, and the sentence is regenerated from the retrieved documents. Two ways to build the query from the draft:

- **Implicit (masking):** blank out the tokens whose probability is below a second threshold beta and search with the rest.
- **Explicit (question generation):** turn the uncertain spans into questions (gpt-3.5-turbo writes them) and search with those.

A second variant, FLARE-instruct, prompts the model to emit a search call by itself (the format is credited to Toolformer). The direct variant is the one reported as the main method. No weights are trained; everything runs by prompting text-davinci-003.

## Results

All numbers are self-reported by the paper. Each uses the setup in the same bullet.

- 2WikiMultihopQA (text-davinci-003; BM25 over Wikipedia; 500 sub-sampled examples; two documents per retrieval; theta 0.8 and beta 0.4; eight exemplars; implicit queries): FLARE-direct 51.0 EM against 39.4 for single-time retrieval, 47.8 for question decomposition (a re-implementation with hand-annotated exemplars) and 28.2 with no retrieval. FLARE-instruct reached 42.4 EM. Previous-window retrieval with 16 tokens scored 43.2 and previous-sentence retrieval 39.0.
- StrategyQA (229 examples, top-3, 6 exemplars, theta 0.4): FLARE 77.3 EM, no retrieval 72.9, single-time retrieval 68.6. Single-time retrieval fell below having no retrieval.
- ASQA (500 examples, top-3, 8 exemplars, explicit queries): FLARE 41.3 EM, single-time 40.0, no retrieval 33.8. ASQA-hint: 46.2 against 43.2 single-time. Query formulation made little difference on ASQA-hint (45.7 implicit, 46.2 explicit).
- WikiAsp (Bing, five documents; 500 examples; four exemplars): 53.4 UniEval against 52.4 single-time.
- Ablations on 2WikiMultihopQA: querying with the next sentence beat the previous sentence (48.8 against 39.0 EM when retrieving every sentence). For the previous-window baseline, longer queries hurt: 43.2 at 16 tokens, 40.0 at 48 tokens. Masking at beta 0.4 gave 0.510 EM against 0.488 with the full sentence.
- Retrieval fired for about 30 to 60 percent of sentences depending on the task. Triggering on 40 to 80 percent of sentences usually performed well; on StrategyQA, performance dropped above 50 percent.

## Limits

- No significant improvement on Wizard of Wikipedia (outputs of about 20 tokens) or on ELI5, where the authors point to grounding and evaluation problems.
- Interleaving costs more: each retrieval triggers another model call, and activations are recomputed with no caching.
- Only one model (text-davinci-003, which the extraction calls deprecated), no more than 500 examples per dataset, and single runs with no seeds or significance tests. Thresholds were tuned per dataset on development data.
- The baselines are the authors' re-implementations rather than exact reproductions. FLARE-instruct required logit adjustments and underperformed.
- The ASQA and WikiAsp gains are about one point; headline figures are in a chart only.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[Agentic RAG — Advanced Patterns]] — related (the practitioner view of adaptive retrieval)
- [[Self-Ask Prompting]] — alternative-to (question decomposition was FLARE's strongest baseline on 2WikiMultihopQA)
- [[2WikiMultiHopQA]] — related (an evaluation set here)
- [[ASQA]] — related (an evaluation set here)
- [[Auto-RAG Autonomous Iterative Retrieval]] — alternative-to (a fine-tuned model decides when to retrieve; FLARE is one of its baselines)
- [[Adaptive-RAG Query Complexity Routing]] — alternative-to (routes by query complexity rather than token confidence)
- [[Language Model Self-Knowledge]] — related (the calibration idea behind confidence as a trigger)
