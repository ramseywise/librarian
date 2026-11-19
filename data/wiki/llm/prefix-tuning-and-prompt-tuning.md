---
title: Prefix-Tuning and Prompt Tuning
tags: [llm, fine-tuning, comparison]
summary: "Two ways to train continuous vectors in front of a frozen language model: prefix-tuning (activations at every layer, for generation) and prompt tuning (embeddings at the input only, whose gap to full tuning closes as the model grows)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-li-2021-prefix-tuning.md
  - data/raw/papers/2026-11-07-lester-2021-power-scale-parameter-efficient-prompt.md
---

# Prefix-Tuning and Prompt Tuning

Both methods freeze the pretrained model and learn a small block of continuous vectors that is prepended to the input. Lester et al. describe prompt tuning as a simplification of the concurrent prefix-tuning.

## Prefix-tuning (Li and Liang, ACL 2021)

A trainable matrix of free activations, prefix length by hidden size, stands in for the first positions at every layer, and all language-model weights stay frozen. For BART the prefix goes on both encoder and decoder. Training uses the ordinary log-likelihood. Optimising the prefix directly was unstable and sensitive to initialisation, so during training the prefix is produced by an MLP applied to a smaller matrix, and once training ends only the resulting prefix is kept.

Reported results (self-reported; GPT-2 Medium for table-to-text, BART Large for summarisation):

- With 0.1% of the parameters it performs on par with full fine-tuning on E2E and beats adapter tuning at the same 0.1% budget by 4.1 BLEU on average across E2E, WebNLG and DART. Adapters at 3.6% sit about 30 times higher in parameter count.
- On XSUM it trails full fine-tuning at 2% of parameters and falls further behind at 0.1%.
- With 50 to 500 training examples (E2E, five sampled datasets with two seeds each) it beats fine-tuning on average, and the gap narrows with more data. It also beat fine-tuning on XSUM news-to-sports extrapolation and on WebNLG unseen categories, though ADAPTER at 3% scored higher there (47.9).
- Best prefix length was about 200 for summarisation and 10 for table-to-text, with a slight drop beyond. Tuning only the embedding layer (EMB-10) was much worse than a full prefix on E2E, and infix placement was slightly worse.
- It took about 30% less training time than fine-tuning and 18% of GPU memory against 50% at batch size 1. Initialising from real words beat random initialisation in the low-data setting and made no difference with full data.

## Prompt tuning (Lester et al., EMNLP 2021)

A p-by-embedding-size prompt matrix is prepended to the embedded input fed to a frozen T5 1.1 and learned by backpropagation; only that matrix is updated. Findings (self-reported; T5 1.1, SuperGLUE dev, mean of three runs):

- Competitiveness grows with scale. At T5-XXL (11B) prompt tuning matches multi-task model tuning, with a 5-token prompt costing 20,480 parameters per task. Prompt-tuned T5-Small reaches GPT-3 XL's level, and prompt-tuned T5-Large surpasses GPT-3 175B (few-shot figures taken from the GPT-3 paper).
- The frozen base matters. With the span-corruption objective prompt tuning worked well at only two of five sizes. The authors "LM-adapt" T5 with 100K extra steps, about 10% of original pretraining steps, giving a better frozen base.
- Beyond 20 tokens extra prompt length gives marginal gains and XXL works even with one token.
- Domain shift: trained on SQuAD, prompt tuning beat model tuning by 12.5 F1 on TextbookQA (66.8 against 54.3) but lost on DROP (67.1 against 68.9) and DuoRC. QQP to MRPC transfer gained 3.2 accuracy and 3.1 F1.
- A five-prompt ensemble on XXL scored 91.3 against 91.0 for the best single prompt and 90.5 on average.

## Limits

- Prefix-tuning was evaluated only on GPT-2 (largest 774M) and BART Large; larger models are proposed as future work, not tested. The paper calls the reason for its better extrapolation an open question. Low-data and extrapolation numbers are small-sample averages without significance tests, and seed counts for full-data runs are not given.
- Prompt-tuning curves come from figures, not tables; only T5 1.1 encoder-decoders and English classification or extractive QA were used, with no generation benchmark; the domain-shift section does not state the model size.
- Prompt-tuning hyperparameters were tuned manually on the same SuperGLUE dev score that is reported. The authors admit the learned prompts can mostly not be interpreted.

## See Also
- [[Parameter-Efficient Fine-Tuning Methods]] — prerequisite-for (the family overview)
- [[LLaMA-Adapter Zero-Initialized Attention]] — extends (layer-wise prompts with a gate)
- [[Black-Box Tuning for Language-Model-as-a-Service]] — extends (tunes a prompt without gradients)
- [[BitFit Bias-Term Fine-Tuning]] — alternative-to (trains bias terms instead of added vectors)
