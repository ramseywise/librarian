---
title: OCR-Memory Optical Context Retrieval
tags: [memory, pattern]
summary: "OCR-Memory renders an agent's history as images, has a trained retriever pick segment indices, and returns the stored verbatim text; on Mind2Web and AppWorld it beats text baselines at a 4096-token memory budget and cuts injected text tokens 6.7x, at the price of more disk and latency (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-li-2026-ocr-memory.md
---

# OCR-Memory Optical Context Retrieval

OCR-Memory (a 2026 preprint) stores long-horizon agent history as rendered images, with set-of-mark style visual anchors. A retriever (a 3B DeepSeek-OCR model fine-tuned with LoRA on HotpotQA supporting facts) looks at the images and selects segment indices; the system then fetches the stored verbatim text for those segments, so the recovered text matches what was stored. Recent history is kept at higher resolution (the last five steps at 1024x1024) and older history at 512x512, and old frames are upscaled when retrieved. Segments are chosen with a probability threshold of 0.4, top 5 per image, at most 20 per query.

## Results (GPT-4 agent at temperature 0; single runs; default memory budget 4096 tokens)

- Mind2Web Cross-Task element accuracy 53.8 against 41.3 for dense text retrieval, 49.1 for AWM and 48.2 for ACON; AppWorld average 58.1 against 41.9 zero-shot, 46.2 retrieval, 55.0 AWM and 56.2 ACON (self-reported). Against AWM and ACON the lead is 1.9 to 4.7 points. Mind2Web task success stays very low for all methods, between 2.2 and 4.8.
- Against text retrieval the element-accuracy gain is +17.0 at 1024 tokens and +12.5 at 4096 (read off a figure's axis labels; self-reported).
- Cost moves rather than disappears: the text tokens injected per step drop from 3,980 to 596 (6.7x), but each episode needs 1.47 MB of disk instead of 18 KB and retrieval takes 1.7 s instead of 0.3 s (self-reported). The 596 excludes the visual tokens read by the retriever.
- Adaptive resolution keeps step success at 46.1 with 82 visual tokens per frame, against 46.5 for static high resolution (256) and 39.7 for static low (65) (self-reported).
- Selecting indices gives step success 46.1 and 1.7 s, against 39.2 and 5.3 s when the model generates the memory text. The 100% faithfulness figure holds by construction, as the authors say.
- Optical compression of about 10x is reported, with RULER needle-in-a-haystack Recall@1 of 98.5% at 4k tokens and 94.1% at 32k (self-reported).

## Limits

- Authors concede a fine-tuned retriever is needed, rendering costs more and uses more disk, and the vision encoder adds memory.
- No full-context or oracle baseline; tokens are matched only partly (only text retrieval is swept across budgets). The comparison confounds "optical" with "trained retriever": a text retriever trained on the same data is missing.
- No variance, no backbones beyond GPT-4 and Qwen3-32B, and "state-of-the-art" is claimed on only two benchmarks. The 6.7x figure covers reasoning-context tokens only. The extraction notes the paper is about episodic retrieval fidelity and cost, not distilled memory.

## See Also
- [[Memory Lifecycle]] — prerequisite-for
- [[Context Compaction]] — alternative-to (shrinking history by compression)
- [[Memory-Augmented Conversational RAG]] — alternative-to (text retrieval over history)
- [[Memory Intelligence Agent]] — related
- [[DeepSeek-OCR Optical Context Compression]] — related
