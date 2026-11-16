---
imported_hash: 1fbb0e342c2223ca
title: Technical Questions — ML/LLM Breadth Round
summary: 'Rapid-fire conceptual fluency: can you explain core mechanisms in 60 seconds with one level of depth in reserve?'
order: 73
kind: reading
section: Technical questions
source: learn-ai-engineering/practice/interviewing/rounds/technical-questions/README.md
---

# Technical Questions — ML/LLM Breadth Round

## What's tested

Rapid-fire conceptual fluency: can you explain core mechanisms in 60 seconds with one level of depth in reserve? The follow-up question is where the signal is — memorized definitions collapse on the second "why?".

This is not a coding round. It's a verbal fluency check across a breadth of ML/LLM concepts, with the interviewer probing depth on whichever topics stall you.

## Format

30–45 min, often folded into another round's first half. 2026 loops front-load transformer/LLM-era questions: attention, tokenization, RLHF/DPO, RAG-vs-fine-tuning, hallucination mechanisms, context windows, chain-of-thought, temperature/sampling — with classical ML as the sanity-check layer.

Real screen question lists run: "What is RAG? Graph+RAG? Chain of Thought? Reflection? How do you manage memory and context? How do you ensure models don't hallucinate?"

## Per-role weighting

| AIE | MLE | DS | FDE |
|-----|-----|-----|-----|
| ●   | ●   | ◐   | ●   |

AIE/FDE versions skew LLM-era topics; MLE adds classical depth; DS versions fold into the stats/SQL screen, so drill the [experimentation](../../../data-analytics/03-experimentation-and-causality/readme.md) and the [classical ML](../../../data-science/01-classical-ml/readme.md), which has spoken answers to the 18 ML Fundamentals questions.

## Folder contents

| File | Purpose |
|------|---------|
| `questions.md` | 25–30 questions organized by domain, each with 60-second answer + one level deeper + study ref |
| `mcq-bank.md` | 238 multiple-choice questions across 14 topics (11 guide topics plus probability, statistics and A/B testing, and classical ML models), with answer keys and a 40-item distinction drill |
| `stats-ml-bank.md` | 127 short-answer questions and worked problems for a maths, statistics and ML screen (81 core, 46 on Bayesian inference, Markov chains, unsupervised learning, neural networks, retrieval, time series and metrics), each linked to its note and lab |
| `stats-ml-primer.md` | Nine short lessons that teach the screen topics with worked numbers; read before the bank and the cheat sheet |
| `stats-ml-cheat-sheet.md` | One page of distributions, probability rules, testing and A/B formulas, and a model pros-and-cons table |
| `real-tech-question-bank.md` | 23 reported interview questions in 9 themes (provider-agnostic config, evals, observability, …) with researched, sourced answers |
| `study-guide.md` | Method, trade-off pairs, flashcard approach, per-role priorities, practice plan, anti-patterns |
| `sources.md` | Internal cross-reference (study guides, notes) + external resources |

**No `examples/` folder** — `questions.md` with 60-second + deeper answers IS the worked content for this round. The domain study guides carry the full treatment.

## Prep checklist

- Work the ●-topics for your role in the README matrix — each study guide's question bank is this round's drill set.
- For every concept, rehearse the 60-second version + the one-level-deeper version (`study-guide.md` covers the method).
- Practice the honest-gap move: "my understanding there is superficial" then redirect.
- Trade-off pairs on flashcards: RAG vs fine-tune, precision vs recall, batch vs streaming, LoRA vs full FT, on-prem vs API. Full list in `study-guide.md`.
- Claim audit: everything on your resume is fair game.

## Note on content placement

The substantive content for this round lives primarily in the domain study guides. This folder organizes the *method* (how to answer rapidly under pressure) and the *question index* (the drill set, with depth markers). Go to the study guides for the full treatment of any topic.
