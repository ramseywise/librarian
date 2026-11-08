---
title: Skill Lift Evaluation
tags: [eval, pattern]
summary: "Measure an agent skill by running the same tasks with and without it and reporting the difference (skill lift); ACES (NVIDIA authors) averaged +0.2134 composite lift over 947 paired cases while static scan scores had no measurable correlation with live lift, and SkillsBench reported curated skills lifting mean pass rate from 33.9% to 50.5% over 18 model-harness configurations (all self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-kevin-2026-evaluating-skills-not-just-agents.md
  - data/raw/papers/2026-11-07-li-2026-skillsbench.md
---

# Skill Lift Evaluation

A skill is a package built around a `SKILL.md` file that an agent harness makes available to a model. Two 2026 preprints measure what a skill adds by running the agent twice, once with the skill and once without. Kevin et al. (arXiv 2608.20614, NVIDIA authors) call the method ACES; Li et al. built the SkillsBench benchmark. The pairing is the point: both papers score the difference, not the with-skill score alone.

## ACES: skill lift under a fixed setup

ACES defines **skill lift** as the with-skill score minus the baseline score, holding agent, model, task, workspace and grader fixed. Its composite is the equal-weight mean of six metrics, graded by deterministic checks plus LLM and RAGAS judges. The authors call the equal weights a diagnostic default, not a claim that the metrics matter equally.

Method points the authors stress:

- **Keep decoys in the baseline.** Other skills stay visible in both arms, since a naive baseline attributes both the skill's content and the routing effect of having it to the skill ("inflates lift", in the authors' words).
- **Isolation and group modes.** Lift is computed with the target skill alone and again among other visible skills. The difference, group minus isolation, is what the paper names the routing premium.
- **Cost.** A full run needs up to 2·N·K·C·A container runs for N skills, K agents, C cases and A attempts.

### Results (self-reported)

- **Headline.** Mean composite lift of +0.2134 (95% CI 0.1967 to 0.2301; 0.7460 with skill against 0.5326 baseline) over 947 paired cases, covering 58 of 64 production skills on four harnesses (Claude Code, Codex, OpenCode, Terminus-2) and 177 scored skill-agent cells. The live-grading judge models are not named.
- **Outcome-only lift is smaller.** Accuracy +0.1431 and goal accuracy +0.2167 give an outcome lift of 0.1799. Process metrics gained more: skill execution +0.3263, behaviour check +0.2983, skill efficiency +0.2758, security +0.020. The extraction notes that the first two process metrics check things the baseline may be unable to satisfy without the skill, so part of that gain is built in by design.
- **Not always positive.** Composite lift was positive in 689 cases, zero in 171 and negative in 87 (median 0.1717). Skill efficiency was positive in only 41.7% of cases.
- **Scan scores do not predict lift.** On 62 skills with both static and live data, Spearman correlation with live lift was −0.0181 for a structural score (CI −0.2667 to 0.2327) and −0.0266 for an LLM-judge rubric score (CI −0.2745 to 0.2247). On 145 skills, the two scan methods correlated with each other at Spearman 0.14.
- **Stronger models, smaller lift.** On the Codex harness with GPT-5.2, 5.4 and 5.5, baselines were 0.63, 0.67 and 0.71, with-skill scores 0.73, 0.77 and 0.76, and lifts +0.09, +0.11 and +0.05. The authors call this a methodological demonstration, not a model-quality claim.
- **Harness matters.** Mean lift was 0.3611 on OpenCode, 0.2904 on Claude Code, 0.1264 on Codex and 0.0896 on Terminus-2, each against its own baseline, with uneven coverage; it is not a model ranking.
- **Many visible skills.** In a stress test with 25 variants and 5 target skills on two harnesses, lift stayed at 0.133 to 0.149 for 1 to 20 visible skills. At 50 visible skills the with-skill pass rate was 0.55 (0.725 at one skill) and wall time 1,290 s.
- **Missing results.** If every case scored at baseline but unscored with the skill is imputed as a failure, composite lift falls from 0.2153 to 0.1840 and stays positive (raw-row audit reconstructing 898 of 947 pairs).

## SkillsBench: a benchmark of curated skills

SkillsBench has 87 containerised tasks across 8 domains, each with a human-written instruction, an expert-written skills bundle, an oracle solution and a deterministic pytest verifier. The authors ran each of 18 model-harness configurations under no-skills and curated-skills conditions, 3 trials per cell (9,396 trials), at temperature 0, and score the paired difference in task-macro pass rate.

Results (self-reported):

- Curated skills raised the mean pass rate from 33.9% to 50.5% (+16.6 points) across the 18 configurations. The smallest gain was OpenHands with Gemini 3.1 Flash Lite (16.0 to 20.1); the largest was OpenHands with GLM 5.1 (32.7 to 58.4).
- The same model differs by harness: Opus 4.7 scored 61.2 with curated skills in Claude Code and 53.1 in OpenHands.
- Self-generated skills (a creator session writes them, a clean solver uses them) fell below no-skills on all three configurations tested, for example Codex with GPT-5.5 at 35.5 against 46.8 without skills and 66.5 with curated skills. In 10 of 12 audited trajectories, the generated skills were never mentioned. The authors' audit covered ten pairs chosen for extreme gaps, not a random sample.
- Of the 87 tasks, 13 showed a negative skills delta pooled over the 18 configurations.
- Domain gain ranged from Natural Science (42.0 to 70.8, 14 tasks) down to Mathematics and OR (45.7 to 55.4, 8 tasks).

## Limits

ACES: live inter-judge agreement, human calibration and judge-uncertainty propagation are unmeasured, and the 1.5-point judge spread covers document rubrics only. Lift is a marginal contribution under the declared workspace and baseline, not an intrinsic value of the skill. Repeated runs are partial (88 of 201 cells have two trials, 113 have one). The corpus skews toward system-access, deployment, platform and data-infrastructure skills, some goal-accuracy scores are a lower bound because a container could not reach a VPN, the raw trajectories are not released, and the headline CI treats cases as independent (cluster bootstraps give [0.1898, 0.2350] over skills). The extraction adds that the authors are at one company and the corpus is mostly internal, evals were written by the authors, and the production runs name no models.

Internal inconsistencies noted by the extraction for ACES: the lift definition lists four metrics and then two more; Table 6 reports 578 condition runs against 947 paired cases, unexplained; the Codex lift in the model sweep (+0.09) differs from the Codex rows in the harness figures (0.13 and 0.11); and the paper's related work says SkillsBench has a fixed 84-task set where the SkillsBench paper has 87, so the 87 here is the SkillsBench figure.

SkillsBench: tasks are terminal-based and containerised only. Injecting a skill adds context, and no length-matched control (irrelevant text, retrieval-only documents) was run. The benchmark skills come from the top quality quartile of the ecosystem (mean 10.1 of 12 on the authors' rubric), so results describe an optimistic case. The skill-count and skill-length splits are observational over different task subsets with different baselines, and the Comprehensive length bucket has 5 tasks. Cybersecurity (7 tasks) and Media (5 tasks) slices are descriptive only. Sixteen of 18 configurations use OpenHands, Claude models may be advantaged by training awareness of the skill format, confidence intervals treat trials as independent, and the self-generated deficit mixes content quality with discovery and creator-solver interference.

## See Also
- [[Skill Eval Pipeline (Blind Comparison + Grading)]] — related (a practitioner pipeline for the same with/without comparison)
- [[Skill Discovery Failure Modes]] — related (trigger and discovery failures, the routing side of the stress test)
- [[Paired Eval Comparison]] — related
- [[Holistic Agent Leaderboard (HAL)]] — related (harness and scaffold effects on one model)
- [[Skill Authoring Discipline]] — related
