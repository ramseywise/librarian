---
title: LLaMA 1 and Llama 2 Open Foundation Models
tags: [llm, pretraining-and-data, concept]
summary: "Touvron et al. (2023) train LLaMA on public data for longer than compute-optimal so small models are cheap to serve, and Llama 2 adds 2T tokens, grouped-query attention and a documented SFT, two-reward-model RLHF, Ghost Attention and safety context distillation pipeline (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-touvron-2023-llama.md
  - data/raw/papers/2026-11-07-touvron-2023-llama-2.md
---

# LLaMA 1 and Llama 2 Open Foundation Models

## LLaMA 1: train smaller models longer

The LLaMA bet: to reach a given quality, serving a smaller model that saw more tokens costs less at inference than serving a larger model sized for compute-optimal training. The family is decoder-only transformers at 7B, 13B, 33B and 65B using pre-RMSNorm, SwiGLU and rotary embeddings, trained with AdamW and a cosine schedule on 1.0T to 1.4T tokens of public sources only (CommonCrawl, C4, GitHub, Wikipedia, Books, ArXiv, StackExchange). The 65B model ran 1.4T tokens for 21 days on 2048 A100 80GB; smaller models trained 1.0T tokens. All models were released to the research community. The authors note that even the 7B model was still improving beyond 1T tokens, which runs against the Chinchilla recommendation of 10B parameters for 200B tokens.

Their headline claim: across 20 zero-shot and few-shot benchmarks, LLaMA-13B outperforms GPT-3 175B on most while being ten times smaller (self-reported; the extraction gives no per-benchmark values). On MMLU 5-shot, LLaMA-65B sits behind Chinchilla-70B and PaLM-540B, a gap the authors blame on the small share of books and papers in the pretraining mix. One instruction-finetuned variant, LLaMA-I, was tried on MMLU only, following the Flan protocol. Measured toxicity grows with model size, most visibly for prompts framed respectfully (RealToxicityPrompts, 100k prompts, greedy decoding).

## Llama 2: pretraining

Llama 2 keeps the Llama 1 design and pretrains 7B, 13B, 34B and 70B models on 2T tokens of public data (cutoff September 2022; training January to July 2023) with 4k context, up from 2k, and grouped-query attention on the 34B and 70B models. The 34B model was trained and reported but withheld, since there was not enough time to red-team it. Language mix is 89.70% English (fastText threshold 0.5).

- Ablations (self-reported): GQA with 8 KV heads matches multi-head attention on average and beats multi-query attention in a 30B-size, 150B-token ablation. Doubling context from 2k to 4k lifts SCROLLS (QuALITY 26.1 to 29.6) with no SQuAD loss (150B tokens each).
- Pretraining used 3.3M A100-80GB GPU hours across all sizes (7B 184,320; 13B 368,640; 34B 1,038,336; 70B 1,720,320; TDP-based, excluding interconnect, non-GPU server power and cooling) and an estimated 539 tCO2eq, offset by Meta.
- Base model MMLU 5-shot: 45.3 (7B), 54.8 (13B), 62.6 (34B), 68.9 (70B), against 63.4 for LLaMA 65B (internal evaluation library). 70B code average (HumanEval 0-shot, MBPP 3-shot) 37.5; GSM8K 8-shot 56.8. Set beside closed models (figures taken from OpenAI and Chowdhery et al.), the 70B nearly matches GPT-3.5 on MMLU, scoring 68.9 to its 70.0, and on GSM8K, 56.8 to 57.1, yet trails badly on HumanEval, 29.9 to 48.1.
- Contamination (skipgram match of 10+ tokens): only HellaSwag and MMLU-Humanities were boosted; 70B HellaSwag clean subset 80.0 against 89.5 not-clean.

## Llama 2-Chat: alignment recipe

1. **SFT** on only 27,540 vendor-written annotations; the authors report that quality mattered more than quantity, so they dropped millions of third-party examples. The extraction links this to [[LIMA: Small Curated Instruction Data]].
2. **Reward models.** Two models, helpfulness and safety, trained on 1,418,091 Meta binary comparisons collected over 14 weekly batches (2,919,326 with open-source sets), each starting from a chat checkpoint and trained for a single epoch, with batch size 512 pairs and a peak learning rate of 5e-6 on 70B and 1e-5 on the other sizes. The ranking loss carries a rating-based margin m(r): `-log(sigma(r(x, y_c) - r(x, y_r) - m(r)))`. With the margin, accuracy on "significantly better" pairs moves from 79.1 to 80.7, while the all-pairs average barely changes (62.5 to 62.9). Adding an auxiliary safety loss takes recall of unsafe responses from 73.0 up to 90.4 (threshold 0.5). On the Meta Helpful test set the helpfulness reward model reaches 63.2%, with GPT-4 at 58.6; it is right on 80.7% of "significantly better" pairs but only 54.7% of "negligibly better" ones.
3. **Iterative RLHF** over five versions, using rejection sampling (70B only, distilled to smaller models) and PPO. The optimum rejection-sampling temperature moves to 1.2-1.3 after RLHF. The PPO reward subtracts beta times D_KL(pi_theta || pi_0) from the reward-model score. A 70B PPO iteration takes about 330 seconds, and FSDP caused about a 20x generation slowdown until weights were consolidated per node. See [[RLHF Pipeline]] and [[Rejection Sampling Fine-Tuning]].
4. **Ghost Attention (GAtt)**, inspired by context distillation, alters the fine-tuning data to help attention hold a system message across turns. After RLHF-V3, adherence to a persona instruction holds at 100% through turn 20; without GAtt it starts at 100% on turn 2, drops to 10% by turn 4 and reaches 0% at turn 6.
5. **Safety context distillation:** prefix a prompt with a safety preprompt, generate safer responses, then fine-tune on them without the preprompt.

Results: in human helpfulness comparisons with ChatGPT, Llama 2-Chat 70B wins 36% of the time and ties in 31.5% (roughly 4,000 prompts, three raters per prompt, gpt-3.5-turbo-0301; the win rate is 44% when ChatGPT's system prompt is removed). For the 70B, fine-tuning lifts TruthfulQA from 50.18 to 64.14 and cuts ToxiGen toxicity from 24.60 down to 0.01 (temperature 0.1, top-p 0.9). Refusals of harmless prompts run near 0.05% on the helpfulness set but 15-27% on a 210-prompt borderline set. In red-teaming on the 7B model, the gamma measure went from 1.8 to 0.45 in prompts per person-hour. A calculator tool gave ASDiv 67.1, SVAMP 69.2 and MAWPS 82.4 zero-shot, with no tool-use training; the authors compare these against Toolformer's reported numbers.

## Limits

- LLaMA 1: no contamination analysis; comparison numbers are taken from other papers that used different evaluation sets (TriviaQA filtered dev against unfiltered test), and some are read off figures. A third-party API produces the toxicity scores. Neither the architecture changes nor the data mix is ablated; sequence length, vocabulary size and precision are not stated. Instruction finetuning is one MMLU experiment with data and hyperparameters not given. Size comparisons confound parameters and tokens.
- Llama 2: the paper does not give depth, hidden size, head count, numeric precision, step count, seeds or the data composition, so pretraining cannot be rerun. Human evaluation has roughly 4k prompts, none involving coding or reasoning, judges only the last turn of multi-turn chats, and shows Gwet AC2 between 0.37 and 0.55 on helpfulness. The safety standards probably favour Llama 2-Chat, and Falcon seems safe partly because its answers are short. The model focuses on English, hallucinates, cannot learn after pretraining and refuses some borderline prompts it should answer. Coding lags far behind GPT-4 and PaLM-2-L. The carbon figure leaves out fine-tuning, annotation compute and hardware manufacture. Reward accuracy is weak on near-tied pairs, GAtt is presented as a basic variant, and the move from 70B rejection sampling to the smaller models is not studied.

## See Also

- [[Open Pretrained Model Reports Comparison]] — related (other open pretraining reports)
- [[GPT-3 and Few-Shot In-Context Learning]] — prerequisite-for
- [[Transformer Architecture]] — prerequisite-for
- [[RLHF Pipeline]] — prerequisite-for
- [[Constitutional AI and RLAIF]] — related
- [[Scaling Laws: Kaplan, Chinchilla and Error Landscapes]] — related (LLaMA trains past the Chinchilla-optimal token count)
