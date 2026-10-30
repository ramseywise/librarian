---
title: Paired Eval Comparison
tags: [eval, llm, pattern]
summary: "Compare two versions on identical tasks via per-task differences (McNemar for binary outcomes) — only discordant tasks carry information, so pairing shrinks the error bar for free; gate on the CI of the difference, read the flipped transcripts, and treat each fix as a tiered, cost-weighted hypothesis."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--09-reading-results.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--10-evals-in-ci.md
---

# Paired Eval Comparison

When comparing version A and B, run both on the **same tasks** and analyze **per-task
differences**, not two independent pass rates.

```
task   A    B    B − A
t1     1    1     0
t2     0    1    +1
t3     1    0    −1
mean difference = Δ;  SE(Δ) = sd(differences) / √n
```

Most tasks pass or fail on both versions, so the differences are mostly zero and SE(Δ) is
much smaller than either rate's SE. Miller (*Adding Error Bars to Evals*, 2024) shows
pairing cuts comparison variance substantially for free.

**McNemar's test** is the binary form: only tasks where A and B disagree carry information.
B winning 14 and losing 6 of 20 discordant tasks is evidence; 11–9 is not.

## Gate on the interval, not the point

"Block if the upper bound of Δ is below −3" won't block on noise; "block if Δ < 0" blocks on
noise half the time. Store the released version's results as the new baseline, with dataset
and grader versions ([[Run-Then-Assert Eval CI]]). Model or provider swaps are run the same
way: everything, paired against current prod.

## Read the flipped transcripts

Numbers say how much; transcripts say why. Before accepting any score change:

1. Pull 10–20 tasks that **flipped** (pass→fail and fail→pass).
2. Read them: real, or grader quirk, infra error, flaky task?
3. If regressions share one failure label ([[Eval Failure Taxonomy]]), that is the story; if
   scattered, it may be noise.

Also read the transcripts of the **biggest gains** — that is where Goodhart shows up
([[Eval Suite Maintenance]]).

## From a benchmark report to hypotheses

A report's value is the hypotheses it suggests. Li's AndroidWorld walkthrough (*AI Agents in
Depth*, ch. 6) gives the method:

1. **Check the eval first** — a 0% cluster may be broken tasks.
2. **Cross per-task results with capability tags**; failures concentrated in one tag point
   to one cause.
3. **Tier hypotheses by cost**: *surface* (prompt hints, tool descriptions — cheap,
   independent, test in parallel with multiple-comparison correction) → *mid* (new tools,
   workflow changes) → *deep* (swap model, new input modality, post-train) only if the tag
   stays low after cheaper tiers.
4. **Weigh gain against cost** — "+75 points for +8% input tokens" differs from a gain at 3×
   cost; never deploy a fix whose gain is inside the noise.
5. **Re-run the full benchmark** — fixing one cluster reveals the next.

A model swap is one deep hypothesis among others, compared on success, tool-call accuracy,
latency and cost on your own set — not a shortcut.

## Report template shape

Per version and paired Δ with CI: headline pass rate, the worst slice with n, errors and
refusals as their own rate, median steps, cost per success, flipped-tasks-read count with the
dominant label, and an explicit decision line.

## See Also
- [[Eval Error Bars and Sample Size]] — prerequisite-for (the SE this reduces)
- [[Eval Metric Interpretation Pitfalls]] — complements (slicing and denominators)
- [[Run-Then-Assert Eval CI]] — instance-of (paired regression gate in CI)
- [[Offline Prompt Experiment Runner]] — related (prompt variants on a frozen sample)
- [[Frozen Ranking Baseline from a Pure Ranker]] — related (a stored baseline to pair against)
