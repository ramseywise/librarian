---
title: ROSCOE Reasoning Chain Metrics
tags: [eval, concept]
summary: "ROSCOE scores a model's step-by-step reasoning chain without a gold chain, using 18 metrics built on step-to-context embedding alignment, NLI contradiction and fluency; it beat reference-free baselines (PRISM, CTC Consistency, BARTScore) on synthetic perturbation tests, with moderate correlations on small human-judged sets (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-golovneva-2022-roscoe.md
---

# ROSCOE Reasoning Chain Metrics

Golovneva et al. (ICLR 2023) ask how an LLM's reasoning chain can be scored automatically with no gold chain to compare against, and regardless of whether the final answer is right. They expect metrics that need no reference and rest on step alignment, embedding similarity, NLI contradiction and fluency to follow reasoning errors more closely than ROUGE, BERTScore or BARTScore do.

## Method

ROSCOE is a suite of 18 interpretable metrics, scored per step and per chain, in four groups: semantic alignment, semantic similarity, logical inference and language coherence. A hypothesis chain h is compared with its source context s (reference-free) or a reference chain r. Cosine scores come from sentence embeddings (SimCSE, fine-tuned contrastively on gold chains and their perturbed versions); for example, the alignment of a step is its best cosine match among the context sentences, rescaled to 0 to 1. An NLI model supplies contradiction probabilities, and GPT2-Large perplexity plus a grammar classifier supply fluency. The metrics are meta-evaluated with Somers' D (preferred over Kendall tau for handling ties) against synthetic perturbation labels on 6 diagnostic datasets and expert error labels on 5 human-judged ones. The authors also give a taxonomy of reasoning errors used for the annotation.

## Results

All figures are the authors' own and self-reported; they are the maximum over perturbation or error types, reference-free, with non-significant correlations omitted.

- **Diagnostics.** With fine-tuned embeddings ROSCOE beats every reference-free baseline on all six datasets. On EntailmentBank, ROSCOE-SS gets 0.955 and the strongest baseline, PRISM, gets 0.453. On ASDIV, ROSCOE-SA gets 0.879 against 0.396 for CTC Consistency; swapping in off-the-shelf embeddings gives 0.198 (all-mpnet) or 0.515 (sup-simcse). ProofWriter (depth-5 subset) is the weakest: ROSCOE-LC at 0.788 against 0.513.
- **Fine-tuning.** On average, fine-tuning SimCSE improves every correlation except repetition, with a gain of up to 0.556 on Informativeness-Chain.
- **Human-judged sets** (GPT-3 chains, expert labels). DROP (n=210): ROSCOE-SS 0.824 against 0.462 for CTC-Consistency. ESNLI (n=151): ROSCOE-SA1 with all-mpnet embeddings 0.799 against 0.647, while fine-tuned ROSCOE-SA gets 0.521. GSM8K (n=200): ROSCOE-SS2 0.638, while BARTScore correlates at -0.546. Several baselines are strongly negative on DROP, for example BARTScore at -0.835. The authors state that human-judged correlations are moderate compared with the synthetic ones.
- **Thresholds drift.** A Repetition cut-off on Informativeness-Chain chosen on EntailmentBank (near 0.95) would mark almost every EQASC chain, including unperturbed ones.
- **Coverage.** Informativeness-Chain covers 10 of 12 perturbation types, and none of the scores reliably detects the missing-step perturbation. The grammar score barely separates perturbed chains (mean 0.854) from unperturbed ones (mean 0.909), with Somers' D of 0.392; the extraction could not tell which dataset that table (Table 41) covers.
- **Annotation cost.** Expert annotation of at most 5 examples averaged 754 seconds, and crowd workers, even paid above $30 an hour, could not annotate accurately. Embedding scores moved by about 0.01 from run to run; fixing the seed at 42 removed that.

## Limits

- The authors concede that the error taxonomy is incomplete and leave improving downstream task performance with the metrics to later work.
- The grammar-score figures have no stated dataset in the extracted text.
- Human-judged sets are small (151 to 210 instances) and mostly GPT-3 outputs, with no inter-annotator agreement in the text the extraction read.
- The figure reported is the best correlation across perturbation or error types, so a metric with many variants has an edge and typical performance is overstated.
- Fixed thresholds do not transfer because scores drift between datasets, and missing-step errors go undetected. ProofWriter results are low since a correct proof may list facts in any order.
- The metrics do not check the integrity or bias of explanations. Baselines are 2020-2021 text-generation metrics, with no LLM-as-judge baseline.

## See Also
- [[Text Metrics Beyond N-gram Overlap]] — related (BERTScore and BLEURT are among its baselines)
- [[Eval Metric Interpretation Pitfalls]] — prerequisite-for
- [[LLM-as-Judge Evaluation]] — alternative-to (an LLM grades the chain instead of embedding and NLI scores)
- [[Chain of Thought]] — prerequisite-for (the step-by-step output it scores)
- [[GPTScore]] — related (another reference-free text metric)
- [[PrOntoQA]] — related (synthetic benchmark with parsed reasoning chains)
