---
title: LLM Hallucination Surveys
tags: [eval, concept]
summary: "Two 2023-24 surveys carve LLM hallucination up differently (factuality versus faithfulness in one; input-, context- and fact-conflicting in the other); neither runs experiments, and both compile benchmark sizes, detection families and mitigations from cited work."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-huang-2023-survey-hallucination-large-language-models.md
  - data/raw/papers/2026-11-08-zhang-2025-sirens-song-ai-ocean.md
---

# LLM Hallucination Surveys

Huang and colleagues (ACM Transactions on Information Systems, 2024) and Zhang and colleagues ("Siren's Song in the AI Ocean", preprint) each survey what hallucination in large language models is, how it is measured and how it is reduced. Neither runs experiments of its own; all figures in both are benchmark sizes or numbers relayed from other studies.

## Two taxonomies

Huang splits hallucination into **factuality hallucination** (a mismatch with verifiable real-world facts) and **faithfulness hallucination** (drifting from the user's input, or contradicting itself). Faithfulness has three subtypes: instruction inconsistency, context inconsistency (output unfaithful to the supplied or retrieved context) and logical inconsistency. Factuality splits into factual contradiction (entity-error, relation-error) and factual fabrication (unverifiability, overclaim). The older NLG split, intrinsic (conflicts with the source) versus extrinsic (cannot be checked against the source or outside knowledge), is kept as background.

Zhang uses three classes instead: input-conflicting, context-conflicting (conflicts with what the model said earlier) and fact-conflicting. It treats all unverifiable content as fact-conflicting and concedes that this choice is contested.

## Detection

Huang separates factuality detection from faithfulness detection. For factual errors Huang describes two routes: checking claims against trusted sources (pull out the facts, then verify by retrieval or internal checking) and estimating uncertainty from the model's own signals. Its examples are atomic-fact scoring in the style of [[FActScore]], [[Chain-of-Verification]] and sampling-consistency checks as in [[SelfCheckGPT]]. Faithfulness metrics fall in five groups: fact-based, classifier-based (NLI), QA-based, uncertainty-based and LLM-based. Zhang names three uncertainty estimators: logit-based, verbalized and consistency-based; it notes that logit-based estimation needs model logits (so fails behind closed APIs) and that verbalized confidence is over-confident.

## Benchmarks

Huang separates evaluation benchmarks (measure a model) from detection benchmarks (test a detector); Zhang separates generation from discrimination formats. Sizes as the surveys report them:

- [[TruthfulQA]]: 817 questions in 38 categories (437 filtered against GPT-3, 380 unfiltered).
- HalluQA: 450 handcrafted adversarial Chinese questions over 30 domains.
- HaluEval 2.0: five domains totalling 8,770 questions. The original HaluEval detection set has 5,000 user queries plus 30,000 task-specific samples; Zhang describes HaluEval as a 35,000-item discrimination benchmark.
- [[FreshQA]]: 600 hand-written questions.
- SelfCheckGPT-Wikibio: 1,908 sentence-level items.
- SimpleQA: 4,326 questions.

Huang observes that existing detection benchmarks centre on summarization, data-to-text and translation with weaker generators (BART, PEGASUS), so they may not reflect detection on current LLMs. Zhang's Table 6 lists single per-model scores (for example 87.9% for gpt-4o on HaluEval and 28.9 for Claude 3.5 Sonnet on SimpleQA) with no source, prompt or date.

## Mitigation and RAG

Zhang covers mitigation across pre-training, supervised fine-tuning, RLHF and decoding-time methods. It reports that greedy decoding beat sampling-based decoding on several benchmarks (cited evidence, no numbers), gives an illustrative honesty reward that pays +1 for a confident correct answer and +0.5 for a hedged correct one, nothing for an uninformative reply, and penalises hedged wrong answers (-2) and confident wrong ones (-4), and notes that honesty-oriented RL can cause over-conservatism. It also reports GPT-4 moving TruthfulQA accuracy from about 30% to about 60% using synthetic hallucination data for the reward model.

Huang attributes hallucination in retrieval-augmented systems to retrieval failure (queries, sources, retriever) and a generation bottleneck (contextual awareness and contextual alignment). It lists noisy context, context conflict and poor use of mid-context information ([[Lost in the Middle]]) under awareness, and source attribution and faithful decoding under alignment. On knowledge conflicts it contrasts reader models that trust parametric memory with later LLM work finding high receptivity to coherent external evidence; see [[Knowledge Conflicts Taxonomy]].

## Limits

- Neither survey gives its own experimental result; neither recommends one grounding metric or compares detectors quantitatively.
- Huang: FELM is given as 817 samples in the text but 3,948 in Table 4; its Table 1 example of a logical inconsistency prints x=3 while the text says the answer is x=4. Literature stops in 2024.
- Huang concedes that RAG still suffers from irrelevant retrieval and shallow retriever-generator interaction, that post-editing self-correction may be unreliable, and that probing methods for internal beliefs are not yet reliable.
- Zhang: Table 6 scores are not comparable across columns; the text attributes the external-knowledge summary to Table 4, though it sits in Table 11; automatic metrics for generation benchmarks align imperfectly with human labels; coverage is mostly English and fact-conflicting; reasoning models get one short paragraph.

## See Also
- [[TruthfulQA]] — related (a benchmark both surveys describe)
- [[FActScore]] — related (atomic-fact detection method)
- [[SelfCheckGPT]] — related (sampling-consistency detection)
- [[Chain-of-Verification]] — related (verification-question detection and correction)
- [[FreshQA]] — related (a benchmark Huang lists)
- [[Knowledge Conflicts Taxonomy]] — related (context versus memory conflicts)
- [[Summarization and Translation Hallucination Studies]] — related (the pre-LLM studies behind the intrinsic/extrinsic vocabulary)
- [[Intrinsic vs Extrinsic Hallucination]] — related
