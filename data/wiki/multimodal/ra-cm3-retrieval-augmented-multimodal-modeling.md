---
title: RA-CM3 Retrieval-Augmented Multimodal Modeling
tags: [multimodal, concept]
summary: "RA-CM3 prepends up to two documents retrieved by a frozen CLIP retriever to a 2.7B CM3 generator, so it can retrieve and generate both text and images; on MS-COCO it reports better FID and CIDEr than vanilla CM3 at under 30% of DALL-E training compute (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-yasunaga-2022-retrieval-augmented-multimodal-language-modeling.md
---

# RA-CM3 Retrieval-Augmented Multimodal Modeling

Yasunaga et al. (ICML 2023) ask whether a multimodal generator that reads text and image documents from external memory can beat a non-retrieval model at lower training compute. Knowledge lives in the memory rather than in parameters. The authors describe it as the first retrieval-augmented multimodal model that retrieves and generates both modalities.

## Mechanism

- **Retriever:** a bi-encoder, the frozen CLIP ViT-L/14, represents a document by averaging its text and image embeddings and L2-normalising the result. A flat FAISS index over the 150M LAION training pairs serves lookups, and at most 2 documents come back.
- **Selection strategy:** chosen for relevance, modality and diversity. Avoid Redundancy discards candidates that resemble the query, or documents already picked, too closely (a relevance above 0.9, for example). Query Dropout removes some of the query tokens, say 20%.
- **Generator:** a CM3 Transformer of 2.7B parameters, trained from scratch. Retrieved documents are placed in front of the input, and the loss covers the main document and the retrieved ones together, with weight alpha 0.1 on the retrieved part.

## Results (self-reported, MS-COCO, no finetuning, 2.7B)

- FID is lower than for vanilla CM3 (29.5) and DALL-E 12B (about 28), and the abstract claims gains of 12 FID and 17 CIDEr over the CM3 baseline. CIDEr beats vanilla CM3 (71.9), 4-shot Flamingo 3B and Parti 20B. For that better FID, training compute is below 30% of DALL-E's.
- Ablations (image perplexity, val): retrieving at both train and inference beats random at train time (243, or 246 random at both); mixed-modal documents beat image-only or text-only (234); simple top-K (244) is worse than Avoid Redundancy (235), and Query Dropout is best (227); alpha 0.1 beats 0 (239) and 1 (240); K=2 is best at inference (K=1, 4 give 228, K=8 232).
- Retrieval gains hold from 125M to 2.7B at equal compute, and a 1.3B retrieval model is claimed to beat a 2.7B vanilla one in perplexity. On a binary ImageNet k-shot task, the reported figures at k=1 are 0.78 against 0.53, and baseline CM3 at k=8 is 0.56 (self-reported).

## Limits

- There are no finetuned results, and a large FID gap remains against Imagen at 7.27, Re-Imagen at 6.88 and Parti at 7.23. The retriever stays frozen CLIP.
- Memory is the same LAION data as training, so a new or updated memory is untested. K is capped at 2 by the 4096-token context.
- Faithfulness and editing appear only as qualitative examples. There is one run, with no seeds or significance tests, and no code link. The authors caution against generating images of people and mention biases in the data.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[CLIP Contrastive Language-Image Pretraining]] — prerequisite-for
- [[Microsoft COCO]] — related
