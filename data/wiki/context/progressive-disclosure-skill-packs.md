---
title: Progressive Disclosure and Skill Packs at Library Scale
tags: [context, concept]
summary: He et al. (2026) turn long books into skill packs an agent harness reads on demand; a flat pack (one SKILL.md with a chunk index) usually beat raw text, a hierarchical pack and hybrid RAG, but gains depend on task, language and harness (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-he-2026-progressive-disclosure-all-you-need.md
---

# Progressive Disclosure and Skill Packs at Library Scale

The paper (LOONGDOC; arXiv 2607.17598) turns the long-document tasks of a public long-context suite into an agent environment on BenchFlow and ACP. It uses three harnesses (Codex, Pi, Claude-Code) and three small or mid-sized models (claude-haiku-4.5, gpt-5.4-mini and qwen3.6-27b).

## Approaches compared

- **Raw:** the full text on disk.
- **Flat:** one SKILL.md holding a chunk index, with the chunks under references/.
- **Hierarchical:** a skill per chunk plus a meta-router.
- **Hybrid-rag:** BM25 and BGE-M3 with RRF and a reranker (Pi only).

## Results (self-reported, mean of three seeds)

- Single book, Pi harness, gpt-5.4-mini, En.MC: flat scored 0.9126 against 0.6398 for hierarchical, 0.8851 for raw and 0.7628 for hybrid-rag. Pi with qwen on Zh.QA: flat 0.7479 against hierarchical 0.3890. Codex results tie within error. Claude-Code with haiku on En.MC: flat 0.8667 against raw 0.7448 (plus or minus 0.1166).
- Library scale, Codex with gpt-5.4-mini, En.QA, 20 books: raw 0.257, flat 0.462, hierarchical 0.267. Raw Zh.QA falls to 0.043.
- Cost: raw 68.3M tokens (about $52 as an uncached upper bound) against 32.5M ($25) for flat.
- Pi with qwen3.6-27b: hybrid-rag scored 0.5439 on En.QA and 0.5856 on Zh.QA, below raw (0.6813, 0.7563).

## Limits

- The En.MC books are probably memorised, K takes only the values 1, 5, 10 and 20, and only narrative books appear. Gains are specific to a task and a language, and many gaps lie within one standard error.
- Appendix C.1 contradicts the main-text pattern: on the Pi harness at library scale, hierarchical is the best pack at K=20 (0.330) and flat falls under raw on Zh.QA.

## See Also
- [[Context Retrieval Strategies]] — prerequisite-for
- [[Coding Agents as Long-Context Processors]] — related
- [[Context Window Budgeting]] — related
