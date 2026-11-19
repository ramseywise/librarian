---
title: Fill-in-the-Middle and Infilling Code Models
tags: [llm, pretraining-and-data, concept]
summary: "Infilling objectives let a left-to-right code model use right-hand context: InCoder's causal masking moves masked spans to the end of the document, and the fill-in-the-middle transformation used by StarCoder, Code Llama and Qwen2.5-Coder rearranges a document into prefix, suffix and middle with sentinel tokens (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-fried-2022-incoder.md
  - data/raw/papers/2026-11-07-li-2023-starcoder.md
  - data/raw/papers/2026-11-07-roziere-2023-code-llama.md
  - data/raw/papers/2026-11-07-hui-2024-qwen2-5-coder-technical-report.md
---

# Fill-in-the-Middle and Infilling Code Models

A plain left-to-right language model cannot condition on code after the cursor. Several code models solve this by rearranging the training text so that the span to be predicted comes last, then using the same decoder-only architecture and next-token loss.

## Causal masking (InCoder)

Fried et al. sample spans, replace each with a sentinel `<Mask:k>`, and move each span to the end of the document. Training is left-to-right over the permuted sequence: left context, sentinel, right context, the sentinel again, then the span and an end-of-mask token. At inference the same model either generates left to right or infills a region using both sides. The objective extends CM3 (Aghajanyan et al.); Bavarian et al. proposed the fill-in-the-middle objective concurrently.

INCODER is a 6.7B decoder-only Transformer. It saw one epoch of 28-language code (159 GB) and StackOverflow (57 GB), on 248 V100 GPUs. Deduplication removed about 75% of the corpus by size (1 TB to 250 GB, exact match on alphanumeric token sequences), and its tokenizer saves 45% of tokens against GPT-2 BPE.

Self-reported findings:

- At 1.3B (52B tokens, multi-language plus StackOverflow) the causal-masking objective slightly beats a plain left-to-right objective on HumanEval pass@1, so infilling did not hurt synthesis.
- Zero-shot infilling beats supervised TypeWriter on F1 for non-None types (2,092-example subset), and zero-shot docstring BLEU comes close to fine-tuned models (CodeXGLUE Python).
- StackOverflow data helps substantially in the 1.3B ablation.
- code-davinci-002 infills better than INCODER (87.4 against 69.0 on single-line HumanEval infilling) and its training is undisclosed.

## Fill-in-the-middle in later models

The three later models cite the fill-in-the-middle recipe of Bavarian et al. (arXiv 2207.14255).

- **StarCoder** (15.5B, 8K context, multi-query attention) trains with the transformation on an 86-language subset of The Stack. Single-line Python infilling exact match is 0.62 for StarCoder against 0.44 for SantaCoder. Docstring generation by infilling scores BLEU 21.99 (CodeXGLUE Python, zero-shot, greedy).
- **Code Llama** adds infilling to the 7B, 13B and 70B models with a multitask autoregressive-plus-infilling objective, in prefix-suffix-middle (PSM) and suffix-prefix-middle (SPM) formats. Averaged over HumanEval and MBPP pass@k, adding infilling lowers scores by 0.6 points at 7B and 1.1 at 13B (500B code tokens, before long-context fine-tuning, temperature 0.1). Its authors attribute the weak random-span infilling in SPM format to token healing not being implemented.
- **Qwen2.5-Coder** lays a document out as prefix, suffix and middle between three special tokens (fim_prefix, fim_suffix, fim_middle) and ends it with endoftext, and keeps a small FIM share in SFT. The base 32B averages 88.3 exact match on the single-line infilling task HumanEval-FIM (weighted by samples per language).

The training-data and staging context for each model is on [[Code LLM Training Recipes]]; Code Llama's long-context stage after infilling changes the RoPE base period, which its paper contrasts with the linear downscaling of [[Position Interpolation]].

## Limits

- InCoder's validation perplexity was still falling after one epoch, so the model is undertrained; the causal-masking-versus-LM ablation goes only to 1.3B.
- InCoder's Table 11 compares across papers whose architecture, data and procedure differ, so it is not rigorous. Codex and CodeGen-Mono, both left-to-right, score above INCODER on HumanEval.
- InCoder's cloze task may overlap Codex's training data (CodeSearchNet); type-hint exact match is noisy and the TypeWriter set is filtered. Learning rate, weight decay and precision are not given.
- Code Llama gives no seeds or error bars, and infilling costs short-context score.
- StarCoder's return-type and docstring benchmarks may overlap its training data.
- Qwen2.5-Coder gives no hyperparameters and single-run results.
- The StarCoder, Code Llama and Qwen papers each name the Bavarian et al. recipe; this page does not read that paper, so the transformation is described only as these papers state it.

## See Also

- [[Code LLM Training Recipes]] — related (the models' data and stages)
- [[Code Encoder and Encoder-Decoder Pretraining]] — alternative-to (denoising objectives for code)
- [[HumanEval and pass@k]] — related (source of the infilling benchmark)
- [[Position Interpolation]] — related
