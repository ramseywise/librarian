---
title: DeepCode Information-Flow Management
tags: [harness, pattern]
summary: "Four operations for generating a whole repository from a long paper without overflowing context: a blueprint, per-file memory entries with context clearing, conditional retrieval of reference code, and a verification loop."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-li-2025-deepcode.md
---

# DeepCode Information-Flow Management

DeepCode (Li et al., University of Hong Kong, a December 2025 preprint) frames the task of generating a whole repository from a lengthy paper as an information-flow problem. It uses four operations and claims to beat commercial coding agents and PhD-level humans on PaperBench Code-Dev.

## Operations

- **Blueprint:** the paper is split into chunks keyed by heading, which agents query when needed. A concept agent and an algorithm agent hand off to a planning agent. Its blueprint covers five things: the file hierarchy, a spec per component, a verification protocol, the execution environment, and a staged plan. The coding agents are meant never to consult the original document.
- **CodeMem:** for each file, context is the blueprint plus selected memory entries; the file is generated, the context is cleared, and a summarizer writes a new entry holding the file's purpose, public interface and dependency edges. The next target is kept outside the entry. The authors say this decouples context size from repository size.
- **CodeRAG:** patterns from reference repositories are retrieved conditionally.
- **Verification loop:** static analysis and sandbox execution.

## Results (self-reported)

- On the whole PaperBench Code-Dev set (20 papers, 3 runs each, o3-mini as judge), DeepCode scored 73.5 +/- 2.8 per the text; the baselines were taken from the PaperBench paper and not re-run: PaperCoder 51.1, an o1 iterative agent 43.3, a Claude-3.5-Sonnet basic agent 35.4.
- Five-paper subset with commercial agents (Claude Sonnet 4.5 thinking for all but Codex): the text gives DeepCode 0.8482 while Codex scored 0.3997, whereas Cursor got 0.5841 and Claude Code got 0.5871; the DeepCode entry in Table 1 reads 0.8541.
- Three-paper subset against a best-of-3 human score of 72.4 from ML PhDs: 75.9 +/- 4.5 in the text, 76.7 +/- 3.9 in the appendix.
- CodeMem ablation (Claude-4.5-Sonnet on 5 tasks, compared with a sliding-window baseline): scores of 0.33 to 0.43 on three tasks rose to 0.70 to 0.92, read from a bar chart without error bars.
- CodeRAG ablation with Gemini-2.5-Flash on 3 papers gave a relative gain of 41% to 71%, but negligible on Claude 4.5 Sonnet. Verification ablation: +3.7% to +6.5%.
- Cost is about 7 to 12 dollars per paper.

## Limits

- Internal inconsistencies: DeepCode is listed as 73.6 +/- 5.3 in Table 2 but the text says 73.5 +/- 2.8; the 5-paper figure is 0.8482 in the text and 0.8541 in Table 1; the 3-paper figure is 75.9 +/- 4.5 in the text and 76.7 +/- 3.9 in the appendix.
- The subsets are very small; the commercial agents carry no error bars and no run count; and the human comparison rests on 3 papers.
- The blueprint is not ablated alone, so crediting it is unproven. CodeMem is compared only with a sliding window, not with summarizing the whole history, and clearing context per file (isolation) is not separated from compression.
- Ablations use different paper subsets and models. Because DeepCode is a multi-agent system with a sandbox, the results do not isolate context handling. PaperBench Code-Dev scores code without executing results.
- Author-run, no independent replication. The authors concede a flawed blueprint leaves the coder with a stale plan.

## See Also

- [[Long-Horizon Execution]] — related
- [[Harness Anatomy]] — prerequisite-for
- [[Verification Loops]] — related
