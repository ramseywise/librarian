---
title: "Clustering Categorical and Mixed Data"
tags: [foundations, concept]
summary: "One-hot plus k-means goes deaf to categories because dummy variance is small; FAMD and MCA recode before PCA, reducing first can hide groups, and the best method depends on which columns hold the groups."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--05b-clustering-categorical-and-mixed-data.md
---

# Clustering Categorical and Mixed Data

Clustering needs a sense of distance; "retail vs construction" has none, so each method invents one, and that invented distance decides whose columns get heard. Three families: turn the table into numbers (MCA, FAMD), define a distance directly ([[Gower Distance, PAM and k-prototypes]]), or assume each group is a recipe ([[Latent Class Analysis for Mixed Data]]). All figures below come from generated tables (1,200 customers, 5 numeric and 6 categorical columns, four groups of 40/30/20/10%) in worlds where groups live in both column types, only categories, only numbers, nowhere (each column shuffled), or both plus a within-group size factor.

## Why one-hot goes deaf

k-means weighs a column by roughly its variance. A z-scored number has variance 1; a dummy for a category with share p has p(1-p), at most 0.25. Six categorical columns (26 levels) hold 3.4 of variance against 5.0 for five numbers. When only categories hold the groups, k-means on one-hot plus numbers scores ARI 0.003 (0.319 on the dummies alone) yet returns four tidy groups and a decent silhouette. When both column types separate, it scores 0.879.

## FAMD and MCA

**FAMD** is PCA after one recoding: z-score numbers and divide each centred dummy by the square root of its share p, stretching rare levels. Each numeric or categorical column can contribute at most 1 of inertia to an axis (totals are not balanced: a category with m levels holds m-1). Eigenvalue 3.271, 2.127, 1.467 for the first axes matched the library's within 0.001. Axes sweep (ARI): 2 axes 0.786, 4 0.888, 8 0.880, 12 0.880, 20 0.752; run the sweep on your table. Library traps: without declaring categorical columns, an integer column is treated as categorical (60 levels), and row coordinates recompute category shares from the batch, so one customer scored in a batch of 5 lands elsewhere than in the full table; score with shares saved at fit time.

**MCA** is the categories-only version (correspondence analysis on the dummy table). Raw percentages mislead: dummy coding inflates total inertia. **Benzécri correction** drops axes with eigenvalue at or below 1/J (J columns) and rescales the rest as [J/(J-1) x (lambda - 1/J)] squared. Example, J=6: eigenvalue 0.324 gives 0.0356; 0.160 is below 1/6 and dropped. Raw first axis 9.7% of structure, corrected 73.4%. Do not pick axis counts from the raw scree.

**Rare levels pull hard**: dividing by the square root of p makes a level count 1/p in squared distance. Giving 8 of 1,200 customers a new channel and plan made those two levels supply 48.1% of axis 1's inertia each, and the new axis correlated only 0.134 with the old one, while k-means ARI barely moved (0.520 to 0.501). Pool rare levels or make them passive. Blocks of columns can be balanced by multiple factor analysis (divide each block by its first singular value); FAMD is the case of one column per block.

## Reducing first can hide the groups

Tandem analysis (reduce, then cluster) can lose the groups because PCA ranks by variance. Three loud correlated columns beside two quiet columns holding three groups, k-means ARI: all 5 columns 0.230, the 2 quiet columns 0.964, PCA axis 1 alone 0.002, axis 2 0.142, 4 axes 0.234. The elbow keeps one axis (56% of variance) with no groups in it. Column choice beat reduction. For categorical data the published evidence is mixed: one simulation had tandem level with joint methods (ARI 0.85 vs 0.82 to 0.86), a later report had it worse once unrelated variables were added. Keep more axes than the elbow says; rerun with a joint method (reduced or factorial k-means) if noise columns are likely.

## Encodings with no label

Target, CatBoost-style and supervised-embedding encodings need a label, so they are unavailable for clustering (a stand-in label makes distances reflect the stand-in). On 1,500 customers with 3 columns of 200 levels where co-occurrence is the signal (ARI, 3 seeds): one-hot then SVD to 8 axes 0.491; one-hot (600 columns) 0.053; frequency 0.039 (equal-sized levels merge); hashing 0.012 (collisions); binary 0.004 (bit codes are arbitrary); Gower with PAM 0.008. Only the MCA-like route keeps co-occurrence; this is one constructed world.

## Benchmark (ARI, 5 seeds)

| Method | both | categorical | numeric | correlated |
|---|---|---|---|---|
| One-hot, k-means | 0.879 | 0.003 | 0.726 | 0.336 |
| FAMD 8, k-means | 0.890 | 0.542 | 0.572 | 0.448 |
| Gower, PAM | 0.289 | 0.190 | 0.024 | 0.220 |
| k-prototypes | 0.796 | 0.004 | 0.721 | 0.315 |
| Latent class | 0.957 | 0.659 | 0.791 | 0.351 |

Latent class wins three columns because the generator is its model; where its independence assumption breaks (correlated), FAMD leads. Two published simulations agree Gower with PAM is weak (mean ARI 0.136 against about 0.34 for FAMD in one) but disagree on the rest, and both draw numbers from normals. On one real table (333 penguins, k=3 scored against species) every mixed method scored below k-means on the numbers alone (0.799): adding a column that splits every species (sex) cost FAMD 0.799 to 0.543, and Gower with PAM 0.631 to 0.181. A mixed method clusters faithfully what you give it.

## Which to reach for

| Situation | Start with |
|---|---|
| Mixed columns, any size | FAMD with generous axes, then k-means; compare one-hot and numeric-only versions |
| Only categories | MCA with corrected percentages |
| "No groups" must be possible, or per-customer probabilities | Latent class with BIC |
| Many missing values or bespoke similarity | Gower with chosen weights |
| Hundreds of levels | Pool rare levels or MCA-like SVD; never binary or hashing on trust |
| Some columns likely noise | Drop them first, or a joint method |

Pitfalls: five outlying values took FAMD plus k-means from 0.880 to 0.413 (clipping at 1% and 99% restored 0.879), so clip before any scale-based method. Rerun on numeric-only and category-only versions to learn which columns the answer depends on.

## See Also
- [[Validating Clusters Without Labels]] — extends
- [[Gower Distance, PAM and k-prototypes]] — extends
- [[Latent Class Analysis for Mixed Data]] — extends
- [[Clustering Algorithms: k-means, Agglomerative and DBSCAN]] — prerequisite-for
- [[Categorical Encoding Choices]] — related
- [[PCA, NMF and Low-Rank Factorisation]] — prerequisite-for
