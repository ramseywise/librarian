---
title: Code LLM Training Recipes
tags: [llm, pretraining-and-data, concept]
summary: "How five code LLMs were built: Codex fine-tuned a GPT on GitHub Python, CodeGen trained in three data stages, StarCoder trained on a filtered Stack subset, Code Llama and Qwen2.5-Coder continued from general models, and IntelliCode Compose trained a small GPT-2 variant for IDE latency (all self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-chen-2021-evaluating-large-language-models-trained.md
  - data/raw/papers/2026-11-07-nijkamp-2022-codegen.md
  - data/raw/papers/2026-11-07-li-2023-starcoder.md
  - data/raw/papers/2026-11-07-roziere-2023-code-llama.md
  - data/raw/papers/2026-11-07-hui-2024-qwen2-5-coder-technical-report.md
  - data/raw/papers/2026-11-08-svyatkovskiy-2020-intellicode-compose.md
  - data/raw/papers/2026-11-07-fried-2022-incoder.md
  - data/raw/papers/2026-11-06-zhang-2023-unifying-perspectives-nlp-software-engineering.md
---

# Code LLM Training Recipes

The decoder-only code models differ mainly in where the weights start, what the code corpus is, and which stages follow. Scores for these models are on [[HumanEval and pass@k]] and [[MBPP and MathQA-Python]]; infilling is covered on [[Fill-in-the-Middle and Infilling Code Models]].

## Recipes

| Model | Starting point | Data | Stages and notes |
|---|---|---|---|
| Codex (Chen et al., 2021), up to 12B | GPT-3 family (reuses its tokenizer and learning rates) | 159 GB filtered GitHub Python, 100B tokens | Codex-S: a second fine-tune on a curated set of standalone functions; Codex-D: trained on the reverse task of writing docstrings |
| CodeGen (Nijkamp et al., ICLR 2023), 350M to 16.1B | Not stated; trained sequentially on three corpora | NL: The Pile; MULTI: BigQuery; MONO: BigPython | Three models trained one after another on those corpora; next-token loss on TPU-v4 with the JAXFORMER library |
| InCoder (Fried et al.), 6.7B | Not stated | code in 28 languages (159 GB) with StackOverflow (57 GB); deduplication removed about 75% by size | Causal masking objective, one epoch |
| StarCoderBase / StarCoder (Li et al., TMLR 2023), 15.5B | Not stated | 86 languages from The Stack v1.2, with GitHub issues, Git commits and Jupyter notebooks added; near-deduplicated and PII-redacted; 1T tokens trained | 8K context, multi-query attention, FIM; StarCoder = base fine-tuned about 2 epochs (35B tokens) on Python |
| Code Llama (Rozière et al.), 7B to 70B | Llama 2 | 500B code-heavy tokens (1T for 70B) | Optional FIM, then long-context fine-tuning on 16,384-token sequences with the RoPE base period increased a hundredfold, to one million; optional 100B Python tokens or about 5B instruction tokens |
| Qwen2.5-Coder (Hui et al.), 0.5B to 32B | Qwen2.5 checkpoints | continued pretraining on 5.2T tokens of files (8K context), then roughly 300B repo-level tokens (32K context); the mixture covers code, text-code grounding, synthetic, math and plain text | SFT in two stages (tens of millions of low-quality samples first, then millions of high-quality ones chosen with rejection sampling), followed by offline DPO whose feedback comes from execution and an LLM judge |
| GPT-C in IntelliCode Compose (Svyatkovskiy et al., FSE 2020) | Trained from scratch (stated) | 1.2B lines of Python, C#, JavaScript, TypeScript | GPT-2 variant with tied embeddings; built for under-100 ms completion |

The StarCoder paper builds on SantaCoder (same architecture, tokenizer design, dedup pipeline) and The Stack. Efficient inference uses multi-query attention ([[Multi-Query and Grouped-Query Attention]]) and the 8K window uses FlashAttention ([[FlashAttention and FlashAttention-2]]). Qwen2.5-Coder's offline DPO follows [[Direct Preference Optimization]], and its instruction data uses rejection sampling ([[Evol-Instruct (WizardLM and WizardCoder)]] and [[OSS-Instruct (Magicoder)]] cover other code instruction-data recipes).

## Findings that bear on a recipe (self-reported)

- **Code fine-tuning loss**: held-out test loss falls as a power law of non-embedding parameter count across Codex sizes 12M to 12B. Averaged over sizes, Codex-S gains 6.5 pass@1 points and 15.1 pass@100 points over Codex. Codex-300M solves 13.2% of HumanEval with one sample.
- **Staged data**: CodeGen-Mono 16.1B reaches 29.28 HumanEval pass@1 against 14.24 (NL) and 18.32 (MULTI). At 2.7B, CodeGen-Mono is ahead of the 2.5B Codex on pass@1.
- **Multi-turn prompting**: CodeGen's 115-problem Multi-Turn Programming Benchmark (MTPB) shows multi-turn prompts beat concatenated single-turn ones at 16.1B and 350M, with lower prompt perplexity, and almost no gain on easy problems at 6.1B and 16.1B. Pass problems have lower prompt perplexity at every size (16.1B: 3.12 against 3.40).
- **Start from a general model**: Code Llama reports (7B, same data mix) that initialising from Llama 2 does better than training from scratch, and that Code Llama 7B roughly matches Llama 2 70B on HumanEval pass@1 after 500B code tokens. The full recipe sits next to [[Continued Pretraining for Domain Adaptation]].
- **Data mix**: in the Qwen2.5-Coder-7B ablation the code:text:math ratio 70:20:10 averages 55.0, against 31.3 for code only and 48.9 for 85:10:5; code only leaves GSM8K at 23.8 versus 64.5. Filtering the text-code grounding data through four hierarchical fastText-style stages moves the 1.5B model's HumanEval/MBPP average from 41.6 up to 46.8.
- **Prompt format**: at temperature 0.1 a file-name prefix prompt lifts StarCoder's HumanEval pass@1 (33.6% to 40.8%) but barely moves StarCoderBase.
- **Language share**: in StarCoderBase, pass@1 improves between 800B and 1000B tokens only for languages with more than about 1 GB of data, and R drops.
- **Instruction data**: Code Llama's self-instruct data (question, test and solution triplets kept only if the tests pass) improves HumanEval for the 7B instruct model; separately, the 34B Instruct model's TruthfulQA score (true and informative) goes from 34.64 to 47.37.
- **Cost**: StarCoderBase took 320,256 GPU hours on 512 A100 80GB (16.68 tCO2eq); InCoder-6.7B used 248 V100 GPUs for one epoch.
- **Responsible release (StarCoder)**: OpenRAIL-M licence, an attribution tool that pairs a Bloom-filter membership check with a BM25 index, and a PII detector (NER with pseudo-labels reaches key F1 70.41% against 6.74% for regex; a better email regex lifted that detector's F1 from 81.8% to 96.83%).
- **Latency (IntelliCode)**: on Python, monolingual GPT-C scores 86.7% edit similarity (perplexity 1.82) while the best n-gram model, a 5-gram, scores 59.7%. Cutting 26 layers to 12 makes inference 2.7x faster at a 6% edit-similarity cost (8 layers: 4.5x faster, 8% cost), and batched beam search with key/value caching cuts latency from 7500 ms to 2700 ms. A multilingual model with control codes helps JS/TS (87.6 against 84.1) but lowers C# (74.6 against 76.8). Online, surfacing rate was 9.2% and click-through rate 10% over more than 150 thousand internal requests. The distillation step is the layer-reduction approach of DistilBERT; for the general method see [[Knowledge Distillation with Soft Targets]].

## Corpus sizes and survey numbers

Zhang et al.'s survey of code language models gives these code corpus sizes (its Table 2, sizes in GB, counting just the code portion for The Pile and ROOTS): CodeSearchNet 20, The Pile code 95 (of an 800 GB raw dataset), ROOTS code 163 (13 languages, of 1.6 TB), CodeParrot 1K, The Stack 3,136, The Stack v2 32K. Code is already part of general pretraining mixes: the survey gives LaMDA as 12.5% code and PaLM as 5%.

It treats the Codex, PaLM-Coder and Code Llama steps as continual pretraining on code, which it says is still self-supervised rather than fine-tuning: Codex adds 100B code tokens to GPT-3, PaLM-Coder adds 7.8B code tokens to PaLM, and Code Llama adds more than 500B code tokens to Llama 2. On fill-in-the-middle, it notes that infilling models outscore the next-token-only CodeGen in its Table 4 but calls the real benefit of infilling training controversial (confounded by model size and data).

For code instruction tuning it gives sizes: InstructCodeT5+ uses 20K samples generated with InstructGPT, WizardCoder grows 20K Code Alpaca samples to 78K through Evol-Instruct and tunes StarCoder on them, Pangu-Coder 2 derives 68K from 20K, and CommitPackFT, built from commit histories, is 2 GB with 742K samples.

## Limits

- Hyperparameters are largely missing: Codex omits batch size, learning rate, context length and model dimensions; Qwen2.5-Coder omits the learning rate, optimizer, batch size, step count, hardware and compute; Code Llama gives no vocabulary, layer counts or precision; CodeGen's hyperparameters were not tuned and its compute is not stated; IntelliCode omits tokens, steps and cost. Single runs, no seeds or error bars throughout.
- Qwen2.5-Coder's mix ablation has no token budget; the code-only average printed (31.3) differs from the mean of that row (37.3), and the table shows 85/15/5 where the text says 85:10:5. On the code columns of Table 3, code-only also beats the 70:20:10 mix, which contradicts the text's statement that 7:2:1 won everywhere.
- Code Llama's Table 2 and Table 10 disagree on Llama 2 MBPP pass@100 (34B 77.6 against 83.1; 70B 83.1 against 85.5); LCC data points are in its code training data, so CodeXGLUE overlap is possible; its data is not released.
- StarCoder: near-deduplication was not applied to Git commits or issues; Swift and D were omitted from training languages; the natural-language share is stated as roughly 20% while the listed components sum to 23%; StarCoder beating StarCoderBase on some non-Python languages is unexplained; benchmarks are English only.
- IntelliCode: internal inconsistencies (batch size 128 against 160; multilingual 26 against 24 layers; the 355M GPT-2 baseline was not code-trained); its offline metrics measure string similarity rather than whether code works; the model is GPT-2 scale and predates Codex; the model and code are not released.
- Zhang et al.'s prose gives CodeParrot as 50GB and The Stack as 3TB while its Table 2 says 1K GB for CodeParrot; its numbers are self-reported by each cited paper.
- Codex needs a very large amount of code to train (hundreds of millions of lines), and the Codex numbers are for research models, not production Copilot. CodeGen is pretraining only, with no instruction tuning, and its multi-turn setting is prompt concatenation, not trained dialogue.
- InCoder's Table 11 notes that its cross-paper comparisons are not rigorous; Zhang et al. say the same of the numbers they collect from each model's paper.

## See Also

- [[Fill-in-the-Middle and Infilling Code Models]] — related (objective used by several of these models)
- [[Code Encoder and Encoder-Decoder Pretraining]] — alternative-to (encoder and encoder-decoder code models)
- [[HumanEval and pass@k]] — related
- [[MBPP and MathQA-Python]] — related
- [[Continued Pretraining for Domain Adaptation]] — related (Code Llama is the starting point for Llemma there)
- [[AlphaCode Sample, Filter and Cluster]] — related
- [[PolyCoder Open Multilingual Code Model]] — instance-of
