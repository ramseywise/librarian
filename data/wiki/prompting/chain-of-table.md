---
title: Chain-of-Table
tags: [prompting, pattern]
summary: Table question answering where the LLM repeatedly picks one of five table operations, the operation is executed programmatically, and the transformed table is fed back, so the reasoning lives in the evolving table.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wang-2024-chain-table.md
---

# Chain-of-Table

Chain-of-Table treats a table as the carrier of reasoning. In a loop, the LLM chooses the next operation from five options (add column, select row, select column, group by, sort by), then generates its arguments. Code executes the operation on the table, and the new table goes back into the prompt. The loop ends on an end tag, and the final table plus the question go to the LLM for the answer. Arguments are parsed with regular expressions and tables are serialised in a pipe format. The planning prompt requests the entire remaining chain, yet only its first operation is retained, because later steps were not planned against the updated table (the extraction's reading of App. E.1).

## Reported results (self-reported)

- Three backbones were used: PaLM 2-S, a GPT-3.5 turbo 16k snapshot from June 2023 and Llama-2 chat; few-shot demos from training sets (29 annotated samples overall); WikiTQ by denotation accuracy, TabFact by binary accuracy.
  - PaLM 2: TabFact 86.61 against 84.63 for the best baseline (Dater); WikiTQ 67.31 against 61.48.
  - GPT-3.5: TabFact 80.20, WikiTQ 59.94 (gains of 1.03 and 3.20). Llama 2: 67.24 and 42.61 (gains of 2.12 and 1.17).
- Vanilla CoT gave little or negative gain: on PaLM 2 WikiTQ 60.43 against 60.59 for end-to-end QA, and on GPT-3.5 TabFact 65.37 against 71.54 for few-shot QA.
- Table length (WikiTQ, model not stated in the extraction): gains over the best baseline grew from +5.63 on short tables to +10.25 on tables above 4k tokens.
- Sample counts: at most 25 per question against 50 for Binder and 100 for Dater; this counts samples, not latency or cost.
- Leave-one-out ablation on PaLM 2: dropping group-by cost 5.43 points on WikiTQ; dropping row or column selection cost 4.0 to 4.4 points on TabFact.
- Free-form FeTaQA: BLEU 32.61 against 29.47 for Dater, with the authors noting ROUGE under-rewards correct answers.
- Serialisation matters for the end-to-end baseline: pipe 60.6 on WikiTQ against 56.1 to 58.1 for HTML, TSV and Markdown.

## Limits

- Only five operations; three table benchmarks; three mid-size 2023 models. The extraction notes that current models handle tables natively, so numbers are not comparable to recent systems.
- PaLM 2 shows the largest gains; the other two backbones improve only slightly.
- Dater with Codex (65.9 WikiTQ, 85.6 TabFact, in a footnote) was excluded because Codex is gone, so the state-of-the-art claim depends on that exclusion. The extraction's own reading of the footnote was inconsistent, and it concludes only that the Codex-Dater comparison was not run.
- The authors re-ran the baselines with new backbones. Its efficiency analysis counts samples only, although the loop makes several calls.
- Which model the table-length analysis used is not stated; no error analysis is given.

## See Also

- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Program-Aided Language Models (PAL)]] — alternative-to (program-aided baselines in the paper)
- [[Decomposed Prompting (DecomP)]] — related
- [[Structured Output]] — related
