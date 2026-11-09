---
title: INSTRUCTOR Instruction-Finetuned Embeddings
tags: [rag, concept]
summary: "INSTRUCTOR embeds text together with a natural-language task instruction, finetuning a GTR dual encoder on 330 instruction-annotated datasets (MEDI); the 335M model is reported to beat a 4.8B baseline on a 70-task average (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-su-2023-one-embedder-any-task.md
---

# INSTRUCTOR Instruction-Finetuned Embeddings

Su et al. (Findings of ACL 2023) ask whether one embedding model can give task- and domain-aware embeddings from an instruction supplied with the input, with no task-specific finetuning.

## Mechanism

- Each input, and each target within a pair, gets an instruction prefix that follows a fixed template naming the domain, the text type and the task objective. Similarity is cosine between the embeddings of instruction plus text on either side.
- INSTRUCTOR starts from GTR, a T5-based dual encoder, and is finetuned on MEDI with a contrastive loss that is bidirectional and uses in-batch negatives. MEDI collects 330 datasets with human-written instructions, 300 of them from Super-NaturalInstructions. A symmetric task shares form and objective across both sides, so both sides receive the same instruction. For compute reasons the authors used four negatives per positive.
- Evaluation covers 70 tasks, 66 unseen in finetuning: MTEB, Billboard text evaluation and prompt retrieval.

## Results (self-reported)

- In Table 2, INSTRUCTOR (335M, initialised from GTR-Large) is tested on 70 evaluation datasets. Its 70-dataset average tops the 4.8B Sent-T5-XXL, and it gains 5.7% relative over GTR-Large on MTEB, text evaluation improving most.
- Retrieval gains only slightly at 335M (about +0.4%), and MS MARCO, HotpotQA, NQ and Touche2020 get worse after instruction finetuning at that size.
- Unseen-domain gains are reported for geography, biology and civil comments (prompt retrieval, Table 3; figures stripped in the extraction).
- Robustness was probed with five paraphrased instructions per dataset. Taking away the 300 Super-NaturalInstructions datasets widens the gap between best and worst phrasing (read off a figure). Mixing symmetric and asymmetric training data hurts when instructions are absent and helps when they are present.

## Limits

- Multitask instruction finetuning of the 4.8B GTR-XXL was out of reach for lack of compute. A single instruction template was used, and paraphrases were tested within it. Coverage is English only, which is why the English-to-German Billboard set was left out.
- Single runs, no seeds or significance tests; batch size and GPU count not stated.

## See Also
- [[GTR Large Dual Encoders]] — prerequisite-for
- [[GritLM (Generative Representational Instruction Tuning)]] — alternative-to
- [[Dense Passage Retrieval (DPR)]] — prerequisite-for
