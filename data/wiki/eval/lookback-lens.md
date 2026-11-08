---
title: Lookback Lens
tags: [eval, concept]
summary: "A contextual-hallucination detector that feeds one number per attention head, the share of attention going to the supplied context, into a logistic regression; on LLaMA-2-7B-Chat it reached AUROC 85.3 transferring QA to summarisation (self-reported), but only about 66 in the realistic chunk-by-chunk setting, and it needs white-box access."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-chuang-2024-lookback-lens.md
---

# Lookback Lens

Lookback Lens (Chuang et al., arXiv 2407.07071, 2024) targets **contextual hallucination**: a model that has the source passage in its prompt and still writes something the passage does not support. The method looks only at attention maps, not at the text produced.

## The feature and the classifier

For each attention head at each generation step, the **lookback ratio** is the attention mass on the context tokens divided by the attention mass on the context plus the tokens generated so far. Across the 1,024 heads of LLaMA-2-7B this gives a 1,024-value vector per span. A default-settings scikit-learn logistic regression on those vectors predicts whether the span is faithful. Labels come from GPT-4o, whose verdicts were spot-checked by people: 68 of 70 XSum judgments and 47 of 50 NQ judgments were correct (self-reported).

## Detection results (self-reported)

Setup: LLaMA-2-7B-Chat greedy outputs; the data is CNN/DM (1,000 items) and NQ (2,655 items); one run; AUROC on held-out data.

- **Cross-task transfer on predefined spans.** Trained on QA and tested on summarisation, the lens scored 85.3; trained on summarisation and tested on QA, 82.0. A hidden-state probe on the 28th layer scored 83.6 and 84.7, so the lens did not win both directions. An off-the-shelf NLI model scored 76.6 and 58.6.
- **In-domain probes overfit.** The same hidden-state probe reached 100.0 train and 91.4 test AUROC on QA, then fell to 57.7 in the sliding-window transfer case.
- **Sliding windows of 8 tokens, no known spans.** The lens scored 66.1 and 66.0, against 56.1 to 59.4 for hidden states and 57.1 and 61.8 for the NLI model.
- **Where the signal sits.** The 10 best heads gave 71.2, the best 100 gave 82.8 and all heads gave 85.3. Middle layers (13 to 20) were most useful, and some heads carry negative coefficients.

## Using it to steer decoding

At each step the authors draw 8 candidate chunks, 8 tokens long, and keep whichever the classifier rates most faithful. On 1,000 XSum examples (classifier trained on CNN/DM only, GPT-4o judging) the share of faithful summaries rose from 49.0% to 58.6%, which is 9.6 percentage points, or 510 to 414 hallucinated examples. The off-the-shelf NLI model used the same way reached 59.0%, so the lens only matched it. At chunk size 16 the NLI model was ahead, 62.1 against 57.7. NQ exact match moved from 71.2 to 74.2. The NLI model was trained on about 731k examples, roughly 700 times the lens's 1k training set.

A learned linear map let the detector move from the 7B to the 13B model with some loss: predefined-span AUROC 73.5 and 78.2, against 84.0 and 84.3 when trained on the 13B itself.

## Limits

It reads the attention of every layer and head during generation, so it cannot run on API-only models, and scoring text another model wrote is untested. It cannot repair an answer when none of the sampled candidates is right, sampling adds inference time, and training needs roughly 1k to 2k labelled examples. Every score is from one run, with no variance or confidence intervals, so a gap like 58.6 versus 59.0 cannot be told apart from noise. The only models tested were LLaMA-2 7B and 13B chat, on short contexts (NQ uses three documents, output capped at 256 tokens), with no real RAG pipeline. GPT-4o produced both the labels and the XSum metric, with the reference answer visible to it, and the human check covered 70 and 50 examples whose validators saw GPT-4o's verdict. Detection is at span or chunk level, not claim level, and about 66 is far from deployable.

## See Also
- [[RAGChecker]] — related (claim-level diagnosis of RAG output from the outside, where this method reads the model's insides)
- [[Grounding Claim Methodology]] — alternative-to (checks groundedness with quoted claims instead of attention)
- [[Tool-Augmented Factuality Checking]] — related
- [[Hidden-State Hallucination Probes]] — alternative-to (another white-box detector, reading hidden states instead of attention)
- [[SelfCheckGPT]] — alternative-to (a black-box detector that needs only sampled text)
