---
title: Survey Weighting, Raking and Effective Sample Size
tags: [foundations, pattern]
summary: Weighting respondents to known population totals (post-stratification or raking) removes only bias carried by the auxiliary variables; it inflates variance by Kish's 1 + L, and the margin must be multiplied by deft and still ignores leftover bias.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--12-surveys-and-sampling-design.md
---

# Survey Weighting, Raking and Effective Sample Size

Weighting makes respondents add up to known totals; an analyst with a customer list has exact totals.
- **Post-stratification:** cross-classify the auxiliary variables (known for respondents and the whole population) and weight each cell to its population count. Cells run out: a population cell with no respondents is lost.
- **Raking** (iterative proportional fitting): match each variable's population shares in turn, repeating until all hold; needs only margins (29 steps to converge in one case). It assumes response probabilities multiply across variables and gives less variable weights. Use cells when few and well filled, raking when many. Related distance: [[Entropy Balancing]]; the weighting logic matches [[Matching and Weighting Estimators]].

## Cost: Kish's 1 + L
Variance inflation from unequal weights is 1 + L = n sum(w^2) / (sum w)^2, L the relative variance of weights; effective sample = n / (1 + L). Meant for haphazard weights, so a rough measure after benchmarking. Check: weights 1,1,1,1,4 give 1 + L = 1.5625, effective 3.2.

## What it repairs
True share 49.6%. Blanket email, unweighted 0.725: raking on channel alone 0.699; channel, segment, active 0.667; plus spend band 0.666 (effective n from 2,648 to about 1,500; cells lost 62 customers in 5 empty cells and landed at the same number). Dropping the activity variable gave 69.1% vs 66.7%. Designed survey (proportional stratified, reminders): unweighted 0.514, raked 0.499 (1 + L 1.034, effective n 934; cells lost 325 customers). Variables matter more than method. The designed survey's near-perfect value was a lucky draw: over 400 repeats the raked mean was 0.528, the email's 0.678, the email's intervals never covered the truth, and the designed intervals covered about 55% since they were centred 3 points off. Raking removed about 30% of the designed survey's bias and 23% of the email's. A real opt-in study found the best adjustment removed only about 30% of bias; complex methods beat simple ones by at most 0.3 points on average. What is left is selection on the answer itself, which no CRM column holds. A counterexample: a sample 93% men (750,148 interviews) forecast within 0.6 points after partial pooling over 176,256 cells that included party identification and past vote: the variables held the selection. At latent strength zero the email's fully raked figure falls from 66.6% to 49.3%.

## Honest margin
Deff is the variance ratio to simple random sampling, deft its root. Margin = 1.96 x deft x sqrt(p(1-p)/n) or the plain formula with n replaced by the effective sample. A deft of 3 turns a claimed t = 2 at alpha .05 into t = 2/3 at .50. In the designed survey (n 966, weighted 0.499, deff 1.03) the margin was 0.032. Subgroups widen fast (referral 9.2 points on 117; paid social vs organic gap 13.4 with margin about 7.4). The margin answers how much it wobbles, not how far off it is: state the residual risk with a sensitivity line. With 48% completed share, if nonrespondents are 5 points less satisfied the figure is 47.3%, 10 points 44.7%. Only a follow-up of a random subsample of nonrespondents measures the gap.

## Pitfalls
- Plain margin after weighting or clustering: intervals too narrow.
- Taking a weighted number as debiased: rows agree with each other and all miss the truth.

## See Also
- [[Survey Error Sources and Nonresponse Bias]] — prerequisite-for
- [[Stratified and Cluster Survey Design]] — prerequisite-for
- [[Entropy Balancing]] — related
- [[Matching and Weighting Estimators]] — related
