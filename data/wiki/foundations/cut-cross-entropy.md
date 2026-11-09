---
title: Cut Cross-Entropy
tags: [foundations, concept]
summary: "Cut Cross-Entropy (CCE) computes the language-model loss in blockwise fused kernels without materialising the tokens-by-vocabulary logit matrix, cutting loss-layer memory from gigabytes to about a megabyte on Gemma 2 2B at near-equal speed."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-wijmans-2024-cut-your-losses-large-vocabulary.md
---

# Cut Cross-Entropy

Wijmans et al. target the cross-entropy layer of large-vocabulary models, where the N x |V| logit matrix dominates memory. The paper reports log-probabilities as 89% of Gemma 2 2B training memory (|V| = 256,128, 16-GPU FSDP) and says one 80,000-token sequence of its log-probabilities fills an 80 GB H100.

The loss is restated as the logit of the correct token, less the log-sum-exp taken across the whole vocabulary. The first term is an indexed matrix multiply fused in one kernel; the second is computed blockwise in SRAM with an atomic log-add-exp guarded by a spin lock, in custom Triton kernels. The backward pass recomputes logits in SRAM and skips blocks in which every softmax entry falls under 2^-12 (gradient filtering), and the vocabulary is reordered by average logit so the non-trivial gradients sit in contiguous blocks. Memory grows as O(N + |V|) rather than O(N x |V|), by the authors' analysis. A Kahan-summation variant without filtering on the classifier gradient (CCE-Kahan-FullC) is used for pretraining.

## Results (all self-reported)

- Setup: A100-SXM4 80GB, averages over 5 seeds, Gemma 2 2B dimensions of D = 2304 and |V| = 256,000 with 8,192 tokens. Results: loss-computation memory falls from 24 GB to 1 MB; loss plus gradient peaks at 1,164 MB against a 1,161 MB lower bound, taking 145 ms against 143 ms for torch.compile and 208 ms for the baseline. The classifier head's total training memory falls from 28 GB to 1 GB.
- At bf16, softmax elements that are non-zero make up under 0.02% in the evaluated models. Turning off gradient filtering slows CCE by 3.4x; disabling vocabulary sorting, 15% slower.
- Liger Kernels uses 95% less memory than the baseline but more than doubles time against torch.compile.
- Fine-tuning loss curves for CCE and for torch.compile cannot be told apart on four models (Qwen 2.5 7B, Phi 3.5 Mini, Gemma 2 2B, Mistral NeMo; Alpaca, 5 seeds). CCE-Kahan-FullC matches validation perplexity in pretraining (5% of Open WebText).
- Under an analytic model (16x80GB, 75 GB usable) the largest feasible batch grows between 1.5x for Llama 2 13B and 10x for GPT-2 and Gemma 2 2B.
- In Mistral NeMo pretraining CCE-Kahan-FullC allowed twice the batch size and saved 2 hours (16%) of training time; the hardware is not stated.

## Limits

- The time advantage shrinks as the vocabulary-to-width ratio falls: on Phi 3.5 Mini (D = 3,072, |V| = 32,064) loss plus gradient is about 50% slower than torch.compile.
- Gradient filtering starves rare tokens, so pretraining needs the slower Kahan variant, roughly twice or more the kernel time of torch.compile.
- Convergence runs omit optimiser, learning rate, batch size, sequence length, steps and hardware; no downstream task evaluation. The batch-size figures use an analytic model the authors say likely undercounts.
- Triton control flow is block-level only; the authors expect CUDA to be faster.

## See Also

- [[FlashAttention and FlashAttention-2]] — prerequisite-for (the blockwise SRAM and online-softmax idea it builds on)
- [[Transformer Architecture]] — related
