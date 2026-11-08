---
title: Output Length Confounds Reference Metrics
tags: [eval, concept]
summary: "On open-ended long-context tasks, L-Eval found n-gram scores track answer length rather than human judgement: Claude-100k's NQ F1 rose from 9.84 to 57.76 once the prompt stated the expected length, and the length instruction lifted ROUGE-L's Kendall tau with human rankings from 0.5 to 0.8 (self-reported), so check answer lengths before comparing systems."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-an-2023-l-eval.md
  - data/raw/papers/2026-11-06-janiak-2025-illusion-progress.md
---

# Output Length Confounds Reference Metrics

A reference-based metric compares a model's answer with a gold answer. L-Eval (An et al., arXiv
2307.11088, 2023), a long-context benchmark of 20 sub-tasks over 508 documents of 3k–200k
tokens, found that on its open-ended tasks these scores follow the length of the answer, and
built its evaluation design around that.

## The evidence

- **One model, two prompts.** On the NQ subset (Table 2), Claude-100k scored F1 9.84 with its
  answers on average 135 words longer than the reference. With a length instruction added to
  the prompt the excess fell to about 1 word and F1 rose to 57.76 (self-reported).
- **Agreement with humans.** Without the length instruction, the paper reports that the
  automatic metrics other than the GPT-4 judge do not track human scores.

## The fix: a length instruction

L-Eval adds the expected length to the prompt ("answer in about N words"). Against human
rankings of 7 systems on 85 questions, the authors report that ROUGE-L's Kendall tau rose from
0.5 to 0.8 with the instruction, and that the GPT-4 judge's reached 1 (self-reported). Two
cautions apply:

- Stating the reference's word count tells the model how detailed an answer is wanted, which
  is part of the answer's shape. Report scores with and without it.
- Seven systems is a small sample for a rank correlation.

## Other findings worth keeping

- **Closed-ended tasks** (multiple choice, exact answers) avoid the problem; L-Eval keeps 7 of
  them beside 13 open-ended ones and scores them by exact-match accuracy.
- **Retrieval vs full context:** a 4k-window model with retrieval scored about 49.7 against
  60.7 for full context on the closed tasks, so retrieval is not a free substitute for a long
  window ([[Long-Context Prompting]]).
- The same commercial model was used to filter the data and was then evaluated, a
  self-selection risk to note when reading its scores.

## The same problem in hallucination-detector scores

Janiak et al. (arXiv 2508.08285, 2025) report that hallucination-detection papers score their detectors with ROUGE-L at a 0.3 threshold, and re-score six detectors with an LLM judge (GPT-4o-Mini) instead. Detectors are measured by AUROC.

- **Judge against ROUGE, versus humans.** On 200 NQ-Open pairs with Mistral-7B-Instruct-v0.3 answers, deliberately sampled where the two methods disagree, three annotators (Cohen's kappa 0.799) agreed with the judge more often than with ROUGE: precision 0.736 against 0.401, agreement 0.723 against 0.142, with recall 0.957 for both (self-reported). Because of the sampling these are not population rates.
- **AUROC drops under the judge.** With zero-shot detectors on NQ-Open, TriviaQA and SQuAD, Mistral's Perplexity fell from 0.852 to 0.584 on NQ-Open (-45.9%, the single worst cell), and its mean over the three datasets fell 27.8% for Perplexity, 24.4% for Eigenscore, 23.2% for eRank and 9.7% for Semantic Entropy. Llama-3.1-8B-Instruct was mixed, with mean LN-Entropy rising from 0.547 to 0.617 (self-reported). ROUGE-based and judge-based AUROCs correlated at only Pearson r = 0.55 (Mistral, one point per method per dataset).
- **Length rivals the detectors.** With judge labels and few-shot prompting, mean AUROC over three datasets for Llama was 0.751 for a standard-deviation-of-length baseline against 0.747 for Eigenscore and 0.784 for Perplexity; for Mistral, mean length scored 0.713 against 0.694 for Eigenscore and 0.635 for Perplexity. Detector scores correlate with answer length (Eigenscore 0.826 for Llama, 0.894 for Mistral). Repeating sentences with no new facts raised Mistral's NQ-Open AUROC from 0.852 to 0.964 at four repeats, and the authors report ROUGE-L falling below 0.3 for answers over 100 tokens whatever their accuracy (self-reported).

Limits of that study: it used a single run, one judge model, closed-book QA with short answers, and just two open models of 7 to 8B. The human check covers one model and one dataset and no judge bias (verbosity, self-preference) was tested; the judge's precision of 0.736 still lets false alarms through. The authors note that a long answer need not be a hallucination, so a detector correlated with length may still capture some real signal. Internal inconsistency: the Section 4 prose calls ROUGE high-precision, which contradicts its own Table 1 and abstract (precision 0.401); the table is used above. The Table 3 zero-shot gaps also differ slightly from Table 2 (for Llama eRank, -16.7% where Table 2 gives -20.2%), which the extraction puts down to different averaging.

## Practical rule

Before comparing two systems on a free-text metric, check their mean answer lengths. If they
differ a lot, either constrain the length in the prompt or normalise, and say which you did
([[Eval Metric Interpretation Pitfalls]]).

## Limits

The agreement figures are a rank correlation over 7 systems, not over individual answers, with
small question sets (85 and 96) and no inter-annotator agreement reported; the paper states
only two tau values in its text. The length instruction changes the answers as well as their
scores: Claude's average human rating rose from 3.08 to 4.04 with it. The judge sees only the
reference answer, never the document, and one of the evaluated models also filtered the data.
The authors themselves say almost every metric they tried, the GPT-4 judge included, shows bias.

## See Also
- [[Eval Metric Interpretation Pitfalls]] — prerequisite-for
- [[LLM Judge Biases]] — related
- [[Long-Context Prompting]] — related
- [[Benchmark Prompt Format Sensitivity]] — related (another prompt detail that moves scores)
- [[SelfCheckGPT]] — related (a hallucination detector of the kind re-scored in the Janiak study)
- [[SQuAD]] — related (one of the datasets used in the detector comparison)
- [[MEDEC]] — related (correction scored with reference metrics)
- [[Long-Form QA Evaluation Hurdles]] — related (ROUGE-L tested with trivial baselines and truncation)
- [[Text Metrics Beyond N-gram Overlap]] — related (metrics that replace word overlap)
