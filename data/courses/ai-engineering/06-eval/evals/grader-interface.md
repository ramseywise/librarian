---
imported_hash: da02d8794502eb07
title: Grader Interface Contract
summary: 'The grader interface is documented in the canonical source: evals/graders/README.md'
order: 8
kind: reading
section: Evals
source: learn-ai-engineering/ai-engineering/06-eval/evals/grader_interface.md
---

# Grader Interface Contract

The grader interface is documented in the canonical source: **`evals/graders/README.md`**

That file covers:
- `BaseGrader` abstract class and `grade()` signature
- `GraderOutput` schema (`score`, `is_correct`, `reasoning`, `dimensions`, `labels`)
- Registry (`get_graders_for_tier`, `TierName`)
- How to add a new grader
- Tier definitions (`heuristic`, `calibrated`, `experimental`)
