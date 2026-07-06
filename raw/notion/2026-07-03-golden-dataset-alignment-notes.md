# Golden Dataset Alignment Notes

**Source:** https://app.notion.com/p/4cc6427075864831a75eaeffd76a6828
**Last edited:** 2026-07-03
**Project:** Virtual Assistant
**Status:** Draft

## Current Status

| Component | Status |
|---|---|
| User questions | ✅ ~100 real user questions selected from 700-question intercom eval dataset |
| URL labels (retrieval targets) | ✅ Human-generated and validated by CS agents |
| Full conversation context | ✅ Captured in separate column |
| Evaluation pipeline | ✅ Hooked up in Langfuse; runnable from terminal against staging, production, or development |
| "Low hanging fruit" eval metrics | ✅ Connected to Langfuse eval pipeline (from VA agents and Galactus) |
| Dataset representativeness | Frequency analysis was applied only across Ramsey's 700 questions |
| Answer quality evaluation | 🔜 Next step after retrieval evaluation is stable |

---

## Meeting 1 — Jun 29, 2026

*Langfuse: The Meeting: Part 2*

### Asks by Team Member

**Jeremy:**
- Dataset good enough to run the evaluation pipeline **now**, without waiting for a perfect dataset
- Runnable against staging, production, and development pipelines
- Simple, interpretable metrics for product side transparency
- Iterative process — no version of the dataset should "lock us in"

**Dan Steenbjerg Rasmussen:**
- Clear description of **how the dataset was created** — enough to understand data lineage
- Confidence that URL labels are trustworthy before tuning agent against them
- Human validation of golden answers before using as benchmark
- Small, high-trust dataset over large, uncertain one
- One-click experiment run (similar to MLflow)

**Yan Zhang:**
- Clarity on team boundaries — agentic AI layer or evaluation team owns dataset and evaluators
- Review Ramsey's pipeline before any decisions to replace or modify
- Input from agent development side on which properties/metrics to include
- Communication and alignment between agent layer and evaluation layer

---

## Meeting 2 — Jul 3, 2026

*VA - Daily Standup*

### Updates

**Jeremy:**
- Selected ~100 questions from Ramsey's 700-question dataset, ordered by likelihood of addressing common customer concerns
- Evaluation pipeline now live in Langfuse with basic metrics, runnable from terminal
- CS agent validated the answers — confirmed most correct, did not flag as off-topic
- *Resolved:* Frequency analysis was run across Ramsey's 700 questions only (not all Intercom)

**Anders:**
- Concern: 100 questions may skew toward edge cases rather than most frequently asked questions
- *Open:* Is the current dataset representative enough as a reliable baseline, or needs revisiting before Thursday?

**Sebastian:**
- Wants pipeline run at least once against the golden dataset before Thursday to establish baseline

**Daniel Tadros:**
- *Open:* Should answer quality be evaluated, not just article retrieval? Correct article link ≠ complete/accurate generated answer. Team agreed this is the next step once retrieval evaluation is stable.

### Open Actions

- Jeremy and Anders to sync to align before looping in CS
- Team to run evaluation pipeline once before Thursday to establish a baseline

---

## Key Decisions

- **~100 question dataset** is sufficient to unblock the pipeline; representativeness is a known limitation to address in next iteration
- **Retrieval eval first**, then answer quality eval
- **Langfuse** is the eval pipeline surface — runnable from terminal
- **CS agent validation** of URL labels provides the human-in-the-loop quality gate
