---
title: Diversity Collapse in Multi-Agent Ideation
tags: [graph, concept]
summary: A study of LLM agent groups writing research proposals finds that authority-structured personas produce less diverse ideas than flat junior groups, that quality barely offsets this, and that mixing models helps hierarchical groups but not flat ones (all self-reported, one task, one main backbone).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-chen-2026-diversity-collapse-multi-agent-llm.md
---

# Diversity Collapse in Multi-Agent Ideation

Chen et al. (arXiv 2604.18005, April 2026 preprint, no venue printed) ask whether groups of LLM
agents keep the variety of ideas that people expect from diverse views. The task is open-ended
research proposal generation, not tasks with a checkable answer. Diversity is scored with the Vendi
score over embeddings, plus dispersion, structural disorder and lexical uniqueness. Five expert
annotators validated the diversity metric (agreement with human judgement was 87% on pairwise
comparisons, self-reported); quality is judged by an LLM from the same family as the generator.

## Findings (self-reported)

- **Authority lowers diversity.** DeepSeek-V3 at temperature 0.7, 50 sessions on each of 20 ICLR
  topics, giving 1,000 proposals in every setting, five persona structures, three agents. Vendi was 8.080 for the
  flat Horizontal structure and 4.647 for the Interdisciplinary one; Leader-Led scored 6.932, Vertical
  6.082 and Naive 5.567. The extraction warns that the per-bar order in the source figure was garbled,
  so the Leader-Led, Vertical and Naive values need checking against the figure.
- **Quality does not compensate.** The highest-quality structure was the least diverse: overall quality
  8.50 against 7.88 on a 10-point scale, with Vendi 4.65 against 8.08.
- **More agents, less per agent.** Vendi divided by agent count fell from 1.03 to 0.47 as the group
  grew from 3 to 7, while absolute Vendi still rose; a per-topic analysis in the appendix is said to
  rule out topic exhaustion.
- **Model mixing.** Three agents on DeepSeek-V3, GPT-4o and Claude-Sonnet-4 with a standard
  topology, 5 topics by 25 runs per cell: Interdisciplinary rose 34.0% (from 2.197 up to 2.943, p=0.0003),
  Leader-Led rose 14.6% (p=0.071, not significant) and Horizontal fell 4.1% (p=0.627). A separate
  20-topic mixed-model Horizontal run scored Vendi 3.402 against 2.755 single-model.
- **Topology interventions.** Nominal-group-style blind writing before discussion, and random
  subgroups, helped depending on persona: for the Naive persona the blind-writing topology scored
  0.456 Vendi lower than the Recursive one with a large effect size across all 20 topics, while
  for Horizontal the gap was -0.040 (p=0.298). The persona-by-topology interaction had p<0.0001.
- **Alignment.** The authors say alignment compresses diversity while the marginal quality
  distribution stays stable; the evidence is a figure, with no numbers given. They also say
  reasoning-heavy models may resist structural fixes, from cells they call illustrative.

## Limits

- One task (scientific proposal generation); the authors say the dynamics may not transfer to
  tasks with ground-truth constraints such as maths. The cross-task figure compares only baseline
  entropy and did not repeat the topology manipulations.
- Primary backbone DeepSeek-V3; replications used GPT-5.1, o1-mini and one three-model mix.
  Temperature took only three values (0.3, 0.7, 1.0), with fixed rounds. Humans validated diversity,
  not quality.
- The "structural coupling" account is an interpretation. The authors qualify the authority claim:
  with flat peers, Senior personas gave higher diversity than Junior ones, so they attribute
  the collapse to expertise combined with hierarchy, not expertise alone. Inside one session,
  dispersion grows and drift shrinks, so collapse is a property across runs.
- Internal inconsistencies noted by the extraction: the Vendi scale is 4.6-8.1 in the main text and
  about 1.7-3.4 in the appendices, unexplained; the main text credits the blind-writing topology as
  beating the standard baseline and maximising initial diversity, but an appendix table with GPT-5.1
  has Recursive at 2.823, blind-writing at 2.526 and Standard at 1.659, so do not cite it as the
  best topology unqualified. The main text says dense interaction speeds premature convergence,
  yet Recursive scores highest in the appendix. The heterogeneous cells use 5 topics, the
  single-model baseline 20.
- No correctness tasks, tool-using agents or cost; it does not address the
  task-success failure rates measured elsewhere.

## See Also
- [[Multi-Agent Failure Modes at Scale]] — prerequisite-for
- [[Multi-Agent Topology Patterns]] — prerequisite-for
- [[Delegation Ceiling and Posterior Distortion]] — related (another measured limit on multi-agent gains)
