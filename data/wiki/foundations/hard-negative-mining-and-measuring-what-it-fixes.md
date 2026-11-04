---
title: "Hard-Negative Mining and Measuring What It Fixes"
tags: [foundations, pattern]
summary: "Mining hard negatives did not raise recall on a tuned matching encoder but cut look-alikes in the top 10 from 0.494 to 0.363 on every seed; judge mining on what the negatives were meant to fix, keep in-batch negatives, and read a sample of what you mined for false negatives."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--05-time-series-and-recommenders--notes--05-learning-a-similarity-function.md
---

# Hard-Negative Mining and Measuring What It Fixes

In-batch negatives are whatever else landed in the batch, mostly easy. **Mining** adds the ones the current encoder likes: for each anchor, rank all training records with the encoder, drop what the labels call a match, take a band of ranks. Here four per anchor are added to the in-batch set, rebuilt once halfway through training, 1,000 pairs, recall standard deviation about 0.01 over three seeds ([[Tuning an Embedding Model from Match Labels]]).

| Arm | Recall | Look-alikes in top 10 | Mined matches before removal |
|---|---:|---:|---:|
| In-batch only | 0.908 | 0.494 | n/a |
| + hardest (rank 1-10) | 0.906 | 0.363 | 0.047 |
| + hardest, false negatives removed | 0.893 | 0.304 | 0.048 |
| + rank 11-100 | 0.908 | 0.502 | 0.002 |
| Hardest only, no in-batch | 0.852 | 0.250 | 0.047 |

## Readings

- **Recall did not rise, look-alikes fell**, on every seed (0.498 to 0.377, 0.499 to 0.349, 0.485 to 0.363). The hard negatives in a catalogue are the look-alikes, so training against them pushes those away. With recall@10 alone mining looks useless; it works on a metric you may not be tracking. If a colleague says mining "did nothing" because recall was flat, ask them to measure what the negatives were meant to fix; if that does not move either, mining is not earning its pipeline.
- **Rank 11 to 100 did nothing**: already easy for this model. A search team on a much larger corpus found ranks 101 to 500 best and that "using the hardest examples is not the best strategy". Rank bands depend on the corpus; test one.
- **Hard only costs recall without collapse**: 0.056 lower, lowest look-alike share. A face-embedding paper warns of collapse to a zero embedding; not seen here, perhaps because of the pretrained start and small learning rate (untested). The search team's hard-only models did not beat random negatives; their fix was rationing: online, at most two hard per positive; offline, recall kept rising with the easy-to-hard ratio until it saturated at 100 to 1. Treating never-clicked impressions (hard by construction) as negatives gave an absolute 55% recall regression on people search.
- **Removing false negatives did not help recall** (0.893 against 0.906). About 4.7% of the hardest band were unlabelled true matches against 0.2% of rank 11 to 100, which is why mining finds them more than random sampling does: it searches where true matches sit. At higher rates they hurt: a label-free tuning method lost 2.5 nDCG@10 points with hard negatives and blamed false negatives. Before building a pipeline, read a sample of what it mines and count true matches.
- **Other studies saw retrieval gains**: adding one BM25 negative per example raised top-5 accuracy on a question-answering dev set from 52.1 to 65.0 at batch 32 (a second added nothing), and refreshing hard negatives from the model's top 200 every 10,000 batches reached MRR@10 0.330 against 0.279 and 0.280 for in-batch with the same warm-up. Why those gained and this did not is untested; earlier ranks on passages, and a recall that had already flattened, are untested explanations.

## Pitfalls

- Mining without reading what you mined (nothing errors when mined negatives are true matches).
- Training on hardest negatives only.
- Copying a rank band.
- Letting known matches be negatives: the loss quietly pushes true matches apart; the cost was not measured.
- Judging mining by recall only.

## See Also
- [[Tuning an Embedding Model from Match Labels]] — prerequisite-for
- [[Two-Tower Retrieval with logQ Correction]] — related (in-batch negatives and their sampling bias)
- [[Similar vs Interchangeable in Matching]] — related (look-alikes)
