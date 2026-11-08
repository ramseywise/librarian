---
title: Logic-of-Thought
tags: [prompting, pattern]
summary: "A zero-shot augmentation that extracts propositions from the context, expands them with logic laws in Python, translates the result to English and appends it to the original context; improved the baseline in 37 of 40 comparisons in the paper (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-liu-2024-logic-thought.md
---

# Logic-of-Thought

Logic-of-Thought (LoT; Liu et al.) adds derived facts to a prompt instead of replacing it. Three phases: Logic Extraction (an LLM pulls out propositions and implications), Logic Extension (a Python program applies Double Negation, Contraposition and Transitive laws over the connectives not, implies and and), and Logic Translation (an LLM writes the new expressions back in natural language). The translation is appended to the full original context, so nothing in the question is dropped; the paper contrasts this with LINC and SatLM, which hand the problem to a symbolic solver.

## Reported results

- Setup: two models (GPT-3.5-turbo-0125, GPT-4-0613), zero-shot, five datasets (ReClor with 46 items, LogiQA, RuleTaker, ProofWriter, FOLIO) and four baseline prompts. LoT beat its baseline in 37 of the 40 pairings (self-reported).
- With GPT-3.5, direct prompting rose from 46.20 to 56.02 on ReClor and from 68.89 to 76.00 on FOLIO (self-reported). GPT-4 gains were small, for example Direct on FOLIO 82.96 to 83.55.
- Regressions appeared: GPT-4 on LogiQA with CoT fell 0.57 points, and GPT-3.5 on FOLIO with CoT fell 2.23 (self-reported); the authors blame extraction errors.
- On FOLIO, LINC (8-shot, rerun with public code) scored 45.19 with GPT-3.5 against LoT's 76.00 zero-shot (self-reported); few-shot against zero-shot is a different setup.

## Limits

- The text says LoT by itself beats CoT in eight of ten pairs. The extraction notes that Table 1 does not obviously show this, since with GPT-3.5 LoT trails CoT on four datasets.
- ReClor uses only 46 items, so the headline +4.35 is two questions.
- The extraction notes a model label in Table 4 that looks inconsistent.
- Only three connectives and three laws; the Figure 3 SatLM values were unreadable in the extraction.

## See Also
- [[Chain of Thought]] — prerequisite-for
- [[Program-Aided Language Models (PAL)]] — related (code does the exact step, here logic expansion)
- [[Self-Consistency]] — related (combined with LoT in the paper)
- [[Chain of Code]] — related
