---
title: SheetCompressor Spreadsheet Encoding
tags: [context, pattern]
summary: "SheetCompressor serializes a spreadsheet for an LLM by keeping rows and columns near structural anchors, inverting the index to value-to-address and aggregating by number format, reaching 24.79x average token compression; Chain of Spreadsheet then detects the table before answering (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-dong-2024-spreadsheetllm.md
---

# SheetCompressor Spreadsheet Encoding

SpreadsheetLLM asks how large multi-table spreadsheets can be serialized for an LLM within token limits while keeping the layout needed for table detection and question answering. The authors expect most rows and columns of large sheets to be homogeneous and to carry no layout information, so that removing them and compacting what remains raises accuracy and lowers token counts.

## Mechanism

The vanilla encoding writes each cell as address, value and format in a Markdown-like text. SheetCompressor applies three modules:

1. **Structural-anchor extraction.** Heuristics propose heterogeneous rows and columns at likely table boundaries (structural anchors). Only rows and columns within k=4 of an anchor are kept, and coordinates are re-mapped.
2. **Inverted-index translation.** A lossless dictionary maps each cell value to its address or address range, merging identical values and dropping empty cells.
3. **Format aggregation.** Numeric cells are replaced by number-format strings or type tags, and adjacent cells of the same type merge into ranges.

Chain of Spreadsheet (CoS) then runs table detection on the compressed sheet, and answers from the detected table re-encoded with no extraction step, which restores the detail that the lossy anchor step dropped.

## Results (self-reported)

Table detection uses a test set of 188 spreadsheets with 311 tables, scored by EoB-0 micro F1 (exact match of all four table boundaries).

- Full compression averaged 24.79x token reduction on the test set, and cut GPT-4 / GPT-3.5-turbo in-context cost by 96% (output tokens ignored).
- Anchor extraction filtered out 75% of the content while retaining 97% of the rows and columns at table boundaries with k=4. In fine-tuned GPT-4, k=4 gave F1 0.759 against 0.712 for k=2 and 0.744 for k=8.
- Inverted-index translation raised the compression ratio to 14.91, up from 4.41 once extraction was applied, and format aggregation took it to 24.79.
- For fine-tuned GPT-4 on Huge sheets (over 32k tokens, 22 sheets), F1 was 0.000 without compression and 0.690 with it. In-context GPT-4-0125-preview rose from 0.154 to 0.410 with compression.
- Ablations on fine-tuned GPT-4: removing extraction dropped F1 from 0.759 to 0.655; removing translation gave 0.743; removing aggregation raised F1 to 0.789, so aggregation trades accuracy for tokens.
- On the authors' own QA set (307 questions over 64 spreadsheets, answers as a cell address or formula), CoS with compression and a fine-tuned detector reached 0.743 accuracy against 0.466 for plain GPT-4. TAPEX and Binder scored 0.378 and 0.622 with truncated inputs.
- Among plain encodings, GPT-4 in-context detection F1 was 0.175 for Markdown, 0.142 for XML and 0.031 for HTML. Open-source models without fine-tuning scored near zero (Llama3 0.027).

## Limits

- Cell formatting such as colour, borders and bold goes unused, as it is too token-expensive and models make poor use of it. Natural-language cells get no semantic compression.
- The extraction notes the QA set is small and its questions each need only one operation. The text mentions no repeated runs, seeds or significance tests, and states no code or data release.
- The extraction notes that fine-tuned and in-context rows use different GPT-4 versions, the baselines were truncated when over their limits, and baselines did not share budgets with the authors' method.
- The extraction notes that the abstract's headline 78.9% F1 belongs to the variant lacking aggregation, not to the full pipeline with about 25x compression, which scored 0.759.

## See Also
- [[Context Window Budgeting]] — related (serialization choices spend the same token budget)
- [[RAG Knowledge Preparation]] — related (preparing tabular sources for model use)
- [[Structured Context and Schemas]] — related
