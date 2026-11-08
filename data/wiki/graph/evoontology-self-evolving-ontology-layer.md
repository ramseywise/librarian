---
title: EvoOntology Self-Evolving Ontology Layer
tags: [graph, pattern]
summary: "EvoOntology keeps a small typed ontology over a data agent's tables, serves it through browse and resolve MCP tools, and revises it from trajectories behind a paired-validation gate; the authors report +17.8 Trajectory-Wise on DDR-Bench over six backbones, with the static prompt version often hurting (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-chong-2026-evoontology.md
---

# EvoOntology Self-Evolving Ontology Layer

Chong, Zhang, Fan and Du (Renmin University; arXiv 2609.15779, a preprint with no stated venue) give a data agent a semantic layer over its tables and files. The ontology holds Terms, Mappings, Constraints and Evidence nodes joined by semantic-relation and structural-reference edges. A builder agent drafts it, and only items that pass a probe against the data are committed. The agent reaches it through two MCP tools, `browse` (explore) and `resolve` (ground a term to concrete columns or values); only a compact manifest sits in the prompt. After tasks, a loop diagnoses failures, attributes them to a schema, content or tool level, proposes a typed patch, and accepts it only if a paired validation score improves by a threshold; otherwise it rolls back.

## Results (self-reported)

Setup: DDR-Bench (10-K filings), six backbone models in a ReAct loop, two-fold evaluation using 70/30 splits; ablations use a four-backbone subset.
- Queryable tools beat injecting the same content as static text: EvoOntology averaged +17.8 Trajectory-Wise over the baseline (range +4.8 to +26.7), while baseline plus a static semantic layer fell 15.0 on Claude-Sonnet-5. On BIRD the average gain was +7.4 execution accuracy and +8.6 VES; the static layer cut execution accuracy by up to 5.6 on GPT-5.5.
- Ablations: removing the gate cost 11.2 Trajectory-Wise (89.5 to 78.3), attribution 6.3, diagnosis 4.8, typed patches replaced by free-form rewrite 1.7. Masking Mappings cost 13.4 and Evidence 8.7.
- Tool-level edits gave the most single-level gain (+13.2 against +8.7 content and +3.6 schema; 57% of cumulative gain in the case run).
- The initial ontology added +12.3 over baseline and evolution a further +7.7; on InsightBench gains were +0.8 and +0.2.
- Cost: turns per task fell from 14.6 to 8.4 and total tokens from 52.6K to 42.0K, though input per turn rose from 3.2K to 4.6K. Reflexion-style episodic memory scored 13.7 lower (75.8 against 89.5).
- Evolved stores were backbone-specific: accepted-term overlap (Jaccard) at most 0.62, and applying another backbone's store cost at least 6.6 points.

## Limits

- No limitations section. Evaluation is frozen after adaptation on a known workload, so new domains and drift are untested. No seeds, variance or significance tests; no comparison against knowledge-graph retrieval methods; text-to-SQL baselines use older backbones without a controlled match.
- The extraction notes a mismatch between four backbones named in the abstract and conclusion and six used in the body, that two EvoOntology rows in Table 3 are identical to baseline-plus-static rows (a likely copy error), and that the text claims gains on every backbone while InsightBench gains are small.
- Model names date quickly.

## See Also
- [[MCP Protocol]] — prerequisite-for
- [[Tool Design as Harness Surface]] — related
- [[Harness Continual Learning]] — related
