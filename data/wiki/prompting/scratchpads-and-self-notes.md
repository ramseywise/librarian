---
title: Scratchpads and Self-Notes
tags: [prompting, pattern]
summary: "Let a model write intermediate computation as text before the answer (scratchpads, 2021) or inline while reading the context (Self-Notes, 2023); Nye et al. report results on 137B and 8B models, while Self-Notes is mostly small GPT-2 work on synthetic tasks (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-nye-2021-show-your-work.md
  - data/raw/papers/2026-11-08-lanchantin-2023-learning-reason-memorize-self-notes.md
---

# Scratchpads and Self-Notes

Both methods ask the model to emit intermediate tokens instead of answering in one pass. They differ in where the extra text goes.

## Scratchpad

Nye et al. (2021) encode the steps of an algorithm as text between scratch tags in the target, and train or few-shot prompt the model to emit them before the answer. A **scratchpad** is an arbitrary sequence of intermediate tokens produced before the final answer; the architecture does not change. The authors test long addition, polynomial evaluation and Python execution, where the trace is a line-by-line record of local variables as JSON.

Results are the paper's own (self-reported):

- Fine-tuned addition (decoder-only models of 2M to 1B parameters, 1 to 8 digit addition, 100k examples): scratchpad models solve addition once the model passes a critical size; models lacking a scratchpad fail even when largest. The critical size appears only in a figure.
- On 9 to 10 digit addition, beyond the training range, the baselines fail entirely and scratchpad accuracy grows with model size.
- Polynomial evaluation was run few-shot (137B model, 4-shot) and fine-tuned (8B model); the extraction records the scratchpad versus direct comparison but not its numbers.
- Python tracing: the extraction records gains for both few-shot and fine-tuned tracing on synthetic programs (137B), under a relaxed scoring rule for the few-shot case. On MBPP with 374 training tasks, scratchpad execution accuracy is below direct execution; adding about 17k sampled programs raises scratchpad accuracy and lowers direct. The best model traces perfectly about a quarter of tasks, and the tracing fine-tune lowers MBPP synthesis from 62% to 54%.

## Self-Notes

Lanchantin et al. (NeurIPS 2023) let the model step away from the context whenever its next token falls in a start-token set and write a note, which is inserted in place before reading goes on. The notes act as working memory placed next to the facts they use. Four paradigms are covered: supervised, semi-supervised, unsupervised and few-shot prompted, on seven datasets including the new Toy-Story task.

- GPT-2 fine-tuned, supervised notes: Self-Notes beat Scratchpad on the Algorithmic task beyond the training length (101 to 200 statements). Scratchpad falls below the plain model there because it copies the context past GPT-2's 1024-token limit.
- On Chess Piecetype beyond 80 moves, Self-Notes and Scratchpad are roughly equal and both far above the plain model.
- With 1% note supervision (100 samples) the model already beats the plain model on Toy-Story; the gain saturates near 25%.
- On GSM8K with 5-shot prompts to the 175B GPT-3 (text-davinci-003): Self-Notes 13.4 against chain of thought 11.4. Dummy tokens in place of notes help only slightly on Chess Piecetype.

## Limits

- Scratchpad: the trace must fit a 512-token generation window, so the MBPP evaluation covers 212 of 500 tasks; the scratchpad is supervised, and learning it without supervision is left for future work; no seeds, variance or optimizer details.
- Self-Notes: the supervised and few-shot variants need notes written by hand, the same annotation burden as scratchpads; most tasks are synthetic with small GPT-2 fine-tuning; the GSM8K gain over chain of thought is small and uses an older davinci-003 model; the gains over Scratchpad on Boolean Variable and Chess Piecetype are within noise; Chess Move accuracy stays below 51%; no code release is stated.

## See Also
- [[Chain-of-Thought Prompting]] — prerequisite-for (the prompting form of the same idea)
- [[Program-Aided Language Models (PAL)]] — alternative-to (offloads the computation to an interpreter)
- [[Math Word Problem Benchmarks]] — related
