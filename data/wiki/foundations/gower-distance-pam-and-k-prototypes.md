---
title: "Gower Distance, PAM and k-prototypes"
tags: [foundations, comparison]
summary: "Gower handles missing values but equal weights give categories about three times the say of numbers; PAM needs an n-by-n matrix, and k-prototypes' gamma has no value that suits every world."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--05b-clustering-categorical-and-mixed-data.md
---

# Gower Distance, PAM and k-prototypes

## Gower

For each pair, a number scores absolute difference over the column's range, a category scores 0 for a match and 1 otherwise, and the distance is the average. A column missing for either customer drops out of that pair's average, a property coordinate methods lack. There are no coordinates, so k-means is out: use PAM (k-medoids, centres are real customers), or agglomerative clustering with average link; HDBSCAN accepts precomputed distances but no benchmark of the pairing was found.

**Equal weights are not equal say.** A mismatch is 0 or 1 while a range-scaled number difference sits near 0.2. Standard deviation of each column's term over pairs: numbers 0.131 to 0.164, categories 0.341 to 0.500, so categories move the distance about three times as much. A column where half of pairs match has the largest spread, 0.5. Results (ARI): Gower with PAM 0.289 in the both-columns world over 5 seeds and 0.024 where only numbers hold groups; numeric columns alone 0.608; numbers weighted by 5 lifts both-world to 0.713 (at seed 0, numeric world 0.018 to 0.466, categorical world 0.184 to 0.141). Ranking each number first gave 0.387. Nothing tells you the weight in advance; choose from what segments are for and report sensitivity.

**Cost is the matrix**: memory is 8 n squared bytes, 0.512 GB at 8,000 customers and about 80 GB at 100,000. Timings on one laptop: Gower matrix 0.954 s and PAM 0.637 s at 8,000 customers, against 0.060 s for FAMD plus k-means. Cluster a sample and assign the rest to the nearest medoid. A stable Gower result (0.802 subsample agreement) can still be wrong (0.263 recovery on the same table); outliers can silently stop numbers counting (spread fell from about 0.15 to 0.04 while the score stayed 0.264). Gower's matrix can be drawn with multidimensional scaling, as a picture only.

## k-modes and k-prototypes

k-modes replaces the mean by the most common level and squared distance by a mismatch count. k-prototypes sums numeric squared distance plus gamma times categorical mismatches, one gamma for both types; the guidance for setting it is called premature even by its author, and the package default is half the average numeric standard deviation. ARI by gamma (seed 0):

| gamma | both | categorical | numeric |
|---|---|---|---|
| 0.5 | 0.750 | 0.004 | 0.700 |
| 1 | 0.752 | 0.024 | 0.662 |
| 2 | 0.675 | 0.165 | 0.511 |
| 4 | 0.535 | 0.271 | 0.215 |
| 8 | 0.357 | 0.220 | 0.037 |

Each world wants a different gamma and you do not know which world you are in; gamma 2 is the most even but still mostly misses categorical-only structure. Treat it as a sensitivity check. One critique argues fixed weights, dummy coding and Gower cannot reliably balance the two types, while proposing a competing method.

## See Also
- [[Clustering Categorical and Mixed Data]] — prerequisite-for
- [[Clustering Algorithms: k-means, Agglomerative and DBSCAN]] — related
- [[Validating Clusters Without Labels]] — related
