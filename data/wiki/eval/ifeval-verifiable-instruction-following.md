---
title: IFEval Verifiable Instruction Following
tags: [eval, graders-and-metrics, benchmark]
summary: "IFEval scores instruction following without a human or LLM judge: 541 prompts carry 25 kinds of verifiable instruction, each checked by a deterministic program, reported as strict and loose accuracy at prompt and instruction level."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-zhou-2023-instruction-following-evaluation-large-language.md
---

# IFEval Verifiable Instruction Following

Zhou et al. look for a way to score instruction following that is objective and repeatable and needs neither human raters nor an LLM judge. Their bet is that **verifiable instructions**, meaning instructions whose compliance a simple program can check, make the evaluation clearer, unbiased and automatic.

## Construction

- The authors define 25 verifiable instruction types.
- Prompts are synthesised by attaching between one and three randomly chosen instructions to base prompts; few-shot prompting filters and rewords them, and a final hand edit follows. The result is 541 prompts.
- Each prompt therefore holds one or more verifiable instructions, and a response is checked by deterministic programs rather than a judge.

## Metrics

Two accuracies are reported at two levels. **Strict** accuracy checks the response as given. **Loose** accuracy also tries 8 transformations of the response before checking. Prompt-level accuracy asks whether every instruction in a prompt was followed; instruction-level accuracy scores each instruction separately. The paper reports all four for GPT-4 (responses scraped Nov 2023) and PaLM 2 S (scraped Aug 2023); the extraction does not carry the values, so none are given here.

## Where it fits

The paper's hypothesis is that program-checkable instructions give a clearer, unbiased and automatic evaluation, and the approach covers only what a program can verify. It cites the MT-Bench judge study as an example of human and model evaluation; see [[MT-Bench and Chatbot Arena Judge Agreement]].

## Limits

- Just two models were scored, and their sizes are not comparable.
- Hardly any instruction is fully verifiable, so edge cases persist: strict scoring can miss compliant answers and loose scoring can accept non-compliant ones.
- The set is limited in variety and number of instructions, and covers text only.
- No decoding settings, sampling or variance are reported.
- Per-category results appear only in figures.

## See Also
- [[MT-Bench and Chatbot Arena Judge Agreement]] — alternative-to
- [[LLM-as-Judge Evaluation]] — alternative-to
- [[FollowIR Instruction-Following Retrieval Benchmark]] — related
