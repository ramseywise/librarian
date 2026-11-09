---
title: Recursive Self-Improvement
tags: [llm, agents, eval, concept]
summary: "Level 4 at the frontier — the write boundary is the load-bearing design decision, a 3% hit rate is fine when attempts are cheap, and automating generation shifts the bottleneck onto verification."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--04-loop--loop-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--04-loop-engineering--notes--08-self-improving-loops.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--04-loop-engineering--notes--03-the-scorekeeper.md
  - data/raw/papers/2026-11-06-zhang-2026-autogenesis.md
  - data/raw/papers/2026-11-06-zhang-2026-harnessing-agentic-evolution.md
  - data/raw/papers/2026-11-06-zhang-2026-self-harness.md
  - data/raw/papers/2026-11-06-zheng-2026-llms-improving-llms.md
  - data/raw/papers/2026-11-06-tian-2026-cedar.md
  - data/raw/papers/2026-11-06-zweiger-2025-self-adapting-language-models.md
  - data/raw/papers/2026-11-06-ye-2026-fragility-self-improving-agents.md
---

# Recursive Self-Improvement

The hill-climbing loop of [[Loop Engineering]] taken to its endpoint: systems that
autonomously design and develop their successors. [[Evolve Loop]] is the same shape at
practitioner scale.

## The Escalation

- **2021–2023** humans write code
- **2023–2025** chatbots emit snippets for humans to integrate
- **2025–2026** coding agents write and edit whole files
- **next** systems that build and train models

Measurements worth quoting when arguing about loop horizons:

- **Task length an AI can complete independently is doubling every ~4 months** (was ~7). Claude
  Opus 3 (Mar 2024) handled ~4-minute tasks; Claude Opus 4.6 handled 12-hour tasks by 2026.
- **>80% of merged production code at Anthropic authored by Claude** (May 2026), up from single
  digits before Feb 2025; engineers shipped **8× more code per quarter** vs 2024.
- CORE-Bench (research reproduction): ~20% success in 2024 → **benchmark saturated within 15
  months**.
- Experiment-optimization speedups: ~3× (May 2025) → **~52×** (Apr 2026).
- On open-ended research problems, models chose a better next step than humans **64%** of the
  time (Apr 2026), up from 51% (Nov 2025).

## The Amdahl Bottleneck

Risks named: acceleration past human oversight; misalignment compounding as systems build
successors (*"more frequent but less understood"*); and an **Amdahl's-law bottleneck** —
automating development shifts the constraint onto **human review and verification**.

That last one is the connection to every other scale in this pillar:

> **At every scale, from a nightly test-fixer to a self-improving lab, the binding constraint
> becomes verification capacity, not generation capacity.**

Which is why levels 2 and 4 of the capability taxonomy matter more than they look, and why the
hard failure modes are the human ones — comprehension debt, cognitive surrender — rather than
the mechanical ones.

Proposed safeguard: verification mechanisms enabling a coordinated multi-lab slowdown or pause
with clear triggers — acknowledged as **harder than arms control**, because training runs are
easy to conceal, and **no credible system exists today**.

> *"The comparative advantage of humans as of right now is still in seeing the bigger picture
> and thinking beyond the confines of the immediate task."*

## The Worked Example: `autoresearch`

The open-source `autoresearch` (released **2026-03-06**, MIT, **~630 lines of Python**) is the
smallest concrete artifact exhibiting the level-4 shape — worth reading precisely because it is
small enough to hold in your head.

The setup: **one Python file, one GPU, one metric.** The agent reads the code, proposes a
change, runs a ~5-minute training run, checks whether validation improved, keeps or discards,
repeats.

### The Write Boundary

**The load-bearing design decision**, and it maps exactly onto the maker/checker split:

| Artifact | Who writes it | Why |
|---|---|---|
| `train.py` — model, optimizer, training logic | **Agent** | The search space |
| `prepare.py` — evaluation utilities | **Nobody** (agent cannot touch) | The verifier must not be editable by the thing it grades |
| `program.md` — instructions | **Human** | The contract |

> **An agent that can edit its own evaluator does not have a verifier; it has a negotiation.**

Making `prepare.py` off-limits converts *"loop that reports success"* into *"loop whose success
means something"* — the same rule as *the model never grades its own work*, **enforced
structurally rather than by instruction**. Compare [[Verification Loops]], where the
generator/evaluator split is enforced by separate agents; here it is enforced by filesystem
permissions, which is stronger.

### The Ratchet Step and the English-Language Loop

Each experiment is one ratchet step ([[Loop Scorekeeper]]): commit the change, train for a
**fixed 5 minutes of wall clock**, compare validation; if better, keep the commit and append a
row to `results.tsv`; if not, `git reset HEAD~1` and log the failure. **The fixed budget makes
results comparable** — no change wins by running longer — and `results.tsv` is the loop's memory
of every attempt, kept or not.

**The loop is written in English.** `program.md` is a methodology, not code: what to change,
what to leave alone, how to judge, what to do on failure, and one iron rule — *never ask for
help, keep going*. Give the agent a method, not a task, and the method becomes the loop.

### Results and the Hit-Rate Reframe

700 experiments over two days → **20 genuine stackable improvements**, cutting GPT-2 training
from **2.02 → 1.80 hours (11%)**. A practitioner reported 19% on the same setup after 37
experiments.

Note the hit rate: **20 of 700 is under 3%.** The loop's value is not that it is clever — it is
that **a ~3% hit rate is perfectly acceptable when attempts are cheap and unattended.** That
reframes the economics:

> *"If you have an objective metric, you are the bottleneck."*

Humans exhaust after roughly a dozen experiments; the loop does not.

**The prerequisite is hard and it bounds where this transfers: an automatic gate that can fail
the work.** Model training, refactoring, content rewrites, and pipeline tuning qualify.
**Anything whose success is only expressible as "looks right" does not** — the same gate as
rung 2 of the [[Loop Autonomy Ladder]].

## When "Done" Is Not Progress

The verifiable loop works where tests, environment state or deterministic rules give fast
feedback. Open-ended research is different: feedback is late, there may be no single right
answer, and the goals that matter (research taste, long-term value) don't reduce to a score. In
one study of four end-to-end autonomous-research attempts, **only one completed**; failures fell
into **implementation drift** (falling back to a familiar method that no longer tests the
hypothesis), **epistemic over-optimism** (noise explained, patched and announced as a finding)
and **missing tacit judgement** (not knowing which baseline matters or when to drop a
hypothesis). The fixes are structural: separate claims from evidence with provenance for every
number; log negative results with equal standing; keep diverse lower-scoring branches alive;
move humans *up* — problem definition, evaluation criteria, reading anomalies, deciding when to
stop. **A self-improving loop's ceiling is set by whether it can evaluate what you actually care
about, not the easiest proxy for it.** Release mechanics for self-edits:
[[Self-Modification as a Release Process]].

## Bilevel Autoresearch

[arXiv:2603.23420](https://arxiv.org/abs/2603.23420) (2026-03-24) closes the level-4
circle: an outer loop reads the inner loop's traces and **generates new search mechanisms as
Python code, injected at runtime.** The inner loop optimizes the task; the outer loop optimizes
*how the inner loop searches*.

Three findings worth carrying:

- **5× improvement** over the inner loop alone (−0.045 vs −0.009 val_bpb) on the `autoresearch` GPT
  pretraining benchmark.
- **Parameter-level tuning without mechanism change yielded no reliable gain.** The outer loop
  had to write new *code*, not new hyperparameters — the structural analogue of the evolve
  loop's *"rewrites files, not weights."*
- **Both loops use the same LLM.** No stronger model at the meta level — **the gain comes from
  loop structure, not model capability.** This is the sharpest available evidence for the
  pillar's governing claim.

The outer loop autonomously reached for combinatorial optimization, multi-armed bandits, and
design of experiments **without being told those domains existed** — succeeding, per the
authors, by *breaking the inner loop's deterministic search patterns*.

## 2026 Self-Improvement Systems and Their Caveats

Five 2026 preprints change what gets edited and what gates the edit. Numbers are the papers' own (self-reported).

- **Autogenesis (AGP).** Separates what evolves (RSPL: prompts, agents, tools, environments and memory held as registered, versioned resources) from the way updates are made (SEPL: reflect, select, improve, evaluate, commit). Rejecting a proposal keeps the active version. On GPQA-Diamond with GPT-4o, joint prompt and solution evolution reached 59.09% against 54.04% for simple reflection, at about 61% more output tokens, over three runs. The evaluator is a second call to the same backbone, given no reference labels, and checks consistency and format rather than correctness, and the cases never exercise rollback.
- **AEvo (Harnessing Agentic Evolution).** A meta-agent edits the mechanism that produces candidates, not the next candidate, with rounds, records and feedback held outside its loop so it cannot stop early. Terminal-Bench 53.8 (DGM and AFlow 44.3) and ARC-AGI-2 47.0 (ADAS 36.0), and 1138 cycles on a VLIW kernel task, at about three times the per-round cost of procedure baselines (Gemini-3-Flash as executor, 3 runs). Without the external harness, two of three kernel runs reward-hacked.
- **Self-Harness.** A fixed model proposes bounded edits to its own harness, and a non-regression gate accepts a change only if neither a held-in nor a held-out split drops and one rises. All nine model-benchmark combinations improved, the largest being GLM-5 on AppWorld, up from 44.4% to 85.0% (subsets of 64 to 180 cases, two attempts). The extraction notes that the held-out split is used for selection and so is contaminated as an estimate.
- **AutoTTS.** A coding agent writes a test-time-scaling controller and scores it by replaying 128 stored trajectories per problem, so no base-model calls are made during search: about $39.9 and 160 minutes over 5 rounds, with about 69.5% fewer tokens than self-consistency at matched accuracy on held-out AIME25 and HMMT25. Forcing one monotone knob (beta) held held-out accuracy at 53.1 against 49.0 without it, and giving the explorer execution traces beat scalar feedback (53.1 against 51.6).
- **CEDAR.** Monte Carlo tree search with an LLM editor and an LLM judge. The extraction flags that the judge and editor share a model class, a circularity risk, and that the appendix gives 10 MCTS iterations where the main text gives 20 by 5 expansions.
- **SEAL.** The model writes its own fine-tuning data, rewarded by the updated model's accuracy: single-passage knowledge incorporation rose from 33.5 to 47.0 (GPT-4.1-written data 46.3), and ARC reached 72.5% on a tiny evaluation set (8 tasks). Forgetting under repeated edits is not addressed.

A caution that cuts across all of them: Ye et al. (Salesforce, 2026) find that memory-based self-improvement on WebArena gives +1.5 points over a no-memory GPT-5-mini agent (Welch p=0.23, 3 runs), shuffling task order turns it into about -4.5, variance rises in 17 of 24 cases, and extra specification closes only 31% of the degradation. The default benchmark order acts as an easy-to-hard curriculum the methods may depend on. See [[Oracle-Gap Recovery by Selection]] on selector quality and [[Forgetting Reset for Discovery Teams]] on session length.

Limits specific to this section: Autogenesis's gate is self-assessed and its GPQA gain costs extra tokens; AEvo's Table 2 ARC score (47.0) and an appendix figure (0.35, 7 of 20) are not reconciled; Self-Harness and AutoTTS use subsets and 2 to 3 repeats; CEDAR's gains cannot be separated from its shared-model judge.

## See Also
- [[Loop Engineering]] — extends
- [[Evolve Loop]] — extends
- [[Verification Loops]] — extends
- [[Loop Autonomy Ladder]] — extends
- [[Eval Ladder]] — extends
- [[Loop Scorekeeper]] — extends
- [[Self-Modification as a Release Process]] — extends
- [[Four Media for Agent Lessons]] — extends
- [[Training-Agent Disaggregation]] — alternative-to (improve the weights from traces instead of rewriting the harness)
- [[RISE Recursive Introspection]] — related
- [[Strategy Lock-In in Post-Training Agents]] — related
- [[SIFT Judge-Guided Self-Improvement Tree Search]] — instance-of
- [[Rehearse Focused Outcome Memory]] — instance-of
- [[AI Research Preference Model]] — instance-of
- [[Meta^n Recursive Operator Stack]] — instance-of
- [[Red Queen Gödel Machine]] — instance-of
- [[MASS Multi-Agent Self-Supervision]] — instance-of
- [[AdaptEvolve Confidence-Routed Evolution]] — instance-of
- [[EvoPrompting Code-Level Architecture Search]] — instance-of
- [[Train-Test Ablation Audit]] — instance-of
- [[SAGA Goal-Evolving Science Agents]] — instance-of
- [[Multi-Agent Evolve Self-Play]] — instance-of
- [[AIRA Draft-Debug-Improve Search]] — instance-of
- [[Self-Evolving Agent Taxonomies]] — related
- [[Evaluator Exploits in Discovery Loops]] — related
- [[Darwin Gödel Machine]] — instance-of (archive-based self-modifying coding agent)
- [[LADDER and TTRL Verified Variant Trees]] — instance-of (verifier-bounded self-training)
- [[Self-Generated Task Practice]] — instance-of
- [[Learned Skill and Action Libraries]] — instance-of
- [[Forgetting Reset for Discovery Teams]] — related
- [[Oracle-Gap Recovery by Selection]] — related
