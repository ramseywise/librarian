---
title: Skill Lift Evaluation
tags: [eval, pattern]
summary: "Measure an agent skill by running the same tasks with and without it and reporting the difference (skill lift); ACES (NVIDIA authors) averaged +0.2134 composite lift over 947 paired cases while static scan scores had no measurable correlation with live lift, and SkillsBench reported curated skills lifting mean pass rate from 33.9% to 50.5% over 18 model-harness configurations (all self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-kevin-2026-evaluating-skills-not-just-agents.md
  - data/raw/papers/2026-11-07-li-2026-skillsbench.md
  - data/raw/papers/2026-11-06-liu-2026-how-well-do-agentic-skills.md
  - data/raw/papers/2026-11-06-jiang-2026-demystifying-agent-skills.md
---

# Skill Lift Evaluation

A skill is a package built around a `SKILL.md` file that an agent harness makes available to a model. Two 2026 preprints measure what a skill adds by running the agent twice, once with the skill and once without. Kevin et al. (arXiv 2608.20614, NVIDIA authors) call the method ACES; Li et al. built the SkillsBench benchmark. The pairing is the point: both papers score the difference, not the with-skill score alone.

## ACES: skill lift under a fixed setup

ACES defines **skill lift** as the with-skill score minus the baseline score, holding agent, model, task, workspace and grader fixed. Its composite is the equal-weight mean of six metrics, graded by deterministic checks plus LLM and RAGAS judges. The authors present the equal weights as a convenient default for inspection and do not argue the six metrics are equally causal.

Method points the authors stress:

- **Keep decoys in the baseline.** Other skills stay visible in both arms, since, by the authors' account, a naive baseline inflates the lift by crediting both effects to the skill.
- **Isolation and group modes.** Lift is computed with the target skill alone and again among other visible skills. The difference, group minus isolation, is what the paper names the routing premium.
- **Cost.** The paper's cost formula is 2·N·K·C·A container runs at most (skills, agents, cases and attempts multiplied together, times two for the two conditions).

### Results (self-reported)

- **Headline.** Mean composite lift of +0.2134 (95% CI 0.1967 to 0.2301; 0.7460 with skill against 0.5326 baseline) over 947 paired cases, covering 58 of 64 production skills on four harnesses (Claude Code, Codex, OpenCode, Terminus-2) and 177 scored skill-agent cells. The live-grading judge models are not named.
- **Outcome-only lift is smaller.** Accuracy +0.1431 and goal accuracy +0.2167 give an outcome lift of 0.1799. Process metrics gained more: skill execution +0.3263, behaviour check +0.2983, efficiency +0.2758 and security +0.020. The extraction points out that the first two process metrics test things a skill-less baseline may be unable to do, so some of that gain is built in by design.
- **Not always positive.** Across the 947 cases composite lift was negative in 87, zero in 171 and positive in 689 (median 0.1717), and the efficiency metric gained in just 41.7% of cases.
- **Scan scores do not predict lift.** On 62 skills with both static and live data, Spearman correlation with live lift was −0.0181 for a structural score (CI −0.2667 to 0.2327) and −0.0266 for an LLM-judge rubric score (CI −0.2745 to 0.2247). On 145 skills, the two scan methods correlated with each other at Spearman 0.14.
- **Stronger models, smaller lift.** On the Codex harness with GPT-5.2, 5.4 and 5.5, baselines were 0.63, 0.67 and 0.71, with-skill scores 0.73, 0.77 and 0.76, and lifts +0.09, +0.11 and +0.05. The authors call this a methodological demonstration, not a model-quality claim.
- **Harness matters.** Mean lift was 0.3611 on OpenCode, 0.2904 on Claude Code, 0.1264 on Codex and 0.0896 on Terminus-2, each against its own baseline, with uneven coverage; it is not a model ranking.
- **Many visible skills.** In a stress test with 25 variants and 5 target skills on two harnesses, lift stayed at 0.133 to 0.149 for 1 to 20 visible skills. At 50 visible skills the with-skill pass rate was 0.55 (0.725 at one skill) and wall time 1,290 s.
- **Missing results.** If every case scored at baseline but unscored with the skill is imputed as a failure, composite lift drops from 0.2153 to 0.1840 yet stays above zero (raw-row audit reconstructing 898 of 947 pairs).

## SkillsBench: a benchmark of curated skills

SkillsBench has 87 containerised tasks across 8 domains, each with a human-written instruction, an expert-written skills bundle, an oracle solution and a deterministic pytest verifier. The authors ran each of 18 model-harness configurations under no-skills and curated-skills conditions, 3 trials per cell (9,396 trials), at temperature 0, and score the with-minus-without gap in task-macro pass rate.

Results (self-reported):

- Curated skills raised the mean pass rate from 33.9% to 50.5% (+16.6 points) across the 18 configurations. The smallest gain was OpenHands with Gemini 3.1 Flash Lite, from 16.0 to 20.1; the largest was OpenHands with GLM 5.1, from 32.7 up to 58.4.
- The same model differs by harness: Opus 4.7 scored 61.2 with curated skills in Claude Code and 53.1 in OpenHands.
- Self-generated skills (a creator session writes them, a clean solver uses them) fell below no-skills on all three configurations tested, for example Codex with GPT-5.5 at 35.5 against 46.8 without skills and 66.5 with curated skills. In 10 of 12 audited trajectories, the generated skills were never mentioned. The authors' audit covered ten pairs chosen for extreme gaps, not a random sample.
- Of the 87 tasks, 13 showed a negative skills delta pooled over the 18 configurations.
- Domain gain ranged from Natural Science (42.0 to 70.8, 14 tasks) down to Mathematics and OR (45.7 to 55.4, 8 tasks).

## Skills in the wild: retrieval, loading and refinement (Liu et al. 2026)

Liu et al. (UCSB and MIT; an April 2026 preprint under review) re-run SkillsBench (84 of its 87 tasks, 3 runs each, Claude Opus 4.6 in Claude Code) while making skill access more realistic, drawing on a pool of 34,198 skills collected from two public registries. Pass rates (self-reported) fall as the setup loosens: 55.4 when the skills are force-loaded, then 51.2 curated, 43.5 with distractors added, 40.1 with top-5 retrieval alongside curated skills, and 38.4 with retrieval alone; no skill at all gave 35.4. Claude loaded all curated skills in 49% of trajectories (31% with distractors). Without curated skills, Kimi K2.5 (19.8 against 21.8 with none) and Qwen3.5-397B (19.7 against 20.5) fell below their no-skill baselines, each in its own harness.

- Agentic search found curated skills better than direct search: recall at 3 of 56.8 against 38.1 for semantic search (Opus 4.6, Claude Code).
- One round of task-specific refinement lifted Claude from 40.1 to 48.2 and Qwen from 26.7 to 30.8, but lowered Kimi from 33.5 to 26.7 in the curated setting; query-agnostic refinement gave smaller gains (Claude 40.1 to 42.0). On Terminal-Bench 2.0 (89 tasks) Claude went 57.7 to 65.5 with retrieval plus refinement; Qwen retrieval alone (44.2) sat below its 44.7 baseline.
- Refinement raised Claude's any-skill load rate from 44% to 72%. With no relevant skill in the retrieved set, refinement did not help Claude (38.4 to 37.9).

## Skills as procedural anchors (Jiang et al. 2026)

Jiang et al. (Princeton and others; an August 2026 preprint) compare skills, workflow memory and raw execution built from the same trajectories, with Codex plus GPT-5.3-Codex and Gemini CLI plus Gemini-3.1-Pro-Preview across Terminal-Bench 2.0, SkillsBench and the Pro variant of Terminal-Bench, giving 528 paired task triples with one trial per arm. Oracle success (self-reported) was 61.9% for skills, 59.1% raw and 55.9% workflow memory. Skills beat workflow memory by 6.06 points (95% bootstrap interval 0.76 to 11.36); the +2.84 over raw has an interval spanning zero (-2.27 to 7.95). An LLM judge (Claude Sonnet 4.6) labelled 65.7% of skill cases as procedural anchoring and 4.5% as knowledge injection. In retrieval on SkillsBench, the precision of skills actually used dropped from 29.6% to 3.3% when the pool grew from 5 to 100 skills, while downstream success stayed roughly flat (36.4% to 39.3%); embedding top-1 precision fell from 88.3% to 76.9%.

## Limits

ACES: the authors list agreement between live judges, human calibration and propagation of judge uncertainty as unmeasured, with the 1.5-point judge spread limited to document rubrics. They describe lift as a marginal contribution under the stated workspace and baseline, not a property of the skill itself. Only 88 of 201 cells were run twice; the other 113 ran once. The corpus skews toward system-access, deployment, platform and data-infrastructure skills, some goal-accuracy scores are a lower bound because a container could not reach a VPN, the raw trajectories are not released, and the headline interval treats cases as independent (a bootstrap clustered by skill gives 0.1898 to 0.2350). The extraction adds that the authors are at one company and the corpus is mostly internal, evals were written by the authors, and the production runs name no models.

Internal inconsistencies noted by the extraction for ACES: the lift definition lists four metrics and then two more; Table 6 reports 578 condition runs against 947 paired cases, unexplained; the Codex lift in the model sweep (+0.09) differs from the Codex rows in the harness figures (0.13 and 0.11); and the ACES related-work section calls SkillsBench an 84-task set where the SkillsBench extraction says 87, so the 87 here is the SkillsBench figure.

SkillsBench: tasks are terminal-based and containerised only. Injecting a skill adds context, and no length-matched control (irrelevant text, retrieval-only documents) was run. The benchmark's skills were drawn from the top quartile of the authors' quality rubric (mean 10.1 of 12), so the results describe an optimistic case. The skill-count and skill-length splits are observational over different task subsets with different baselines, and the Comprehensive length bucket has 5 tasks. Cybersecurity (7 tasks) and Media (5 tasks) slices are descriptive only. Sixteen of 18 configurations use OpenHands, Claude models may be advantaged by training awareness of the skill format, confidence intervals treat trials as independent, and the self-generated deficit conflates skill quality, discovery and interference between creator and solver.

Liu et al.: two benchmarks and three models, 3 runs per task with no intervals, each model in its own harness (so model and harness are confounded), a single refinement pass, no Kimi query-agnostic result, and skill coverage scored by an LLM judge (GPT-5.4). Query-agnostic refinement was applied only to the retrieved skills because of cost.

Jiang et al.: terminal and tool-using benchmarks with few agent-model pairs; the failure taxonomy was built by open coding 240 trajectories, around 3% of the records, and an LLM judge labels the 528 triples, with only the taxonomy construction human-validated (kappa 0.952). The skills are distilled from trajectories by a prompt, not hand-written. Skill beats raw without statistical significance; significance holds only against workflow memory. The authors concede the findings may not carry to other scaffolds or models. The extraction did not see appendix tables 15 and 16.

## See Also
- [[Skill Eval Pipeline (Blind Comparison + Grading)]] — instance-of (a practitioner pipeline for the same with/without comparison)
- [[Skill Discovery Failure Modes]] — related (trigger and discovery failures, the routing side of the stress test)
- [[Paired Eval Comparison]] — related
- [[Holistic Agent Leaderboard (HAL)]] — related (harness and scaffold effects on one model)
- [[Skill Authoring Discipline]] — related
- [[SkillWeaver Compositional Skill Routing]] — related (routing and retrieval of skills)
- [[ContinualSkillBench]] — related
- [[SkillGym]] — related
