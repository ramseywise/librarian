---
title: Laplace Mechanism and Sensitivity-Calibrated Noise
tags: [foundations, concept]
summary: "Dwork, McSherry, Nissim and coauthors prove that Laplace noise with scale equal to a query's L1 sensitivity over epsilon keeps answers epsilon-indistinguishable, even for adaptive query sequences, and that non-interactive mechanisms need exponentially large databases."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-dwork-2006-calibrating-noise-sensitivity-private-data.md
---

# Laplace Mechanism and Sensitivity-Calibrated Noise

Dwork, McSherry, Nissim and coauthors (a Springer chapter, doi 10.1007/11681878_14; the PDF prints neither venue nor year, so 2006 is inferred) ask how much noise a statistical-database answer needs to stay private, for arbitrary query functions rather than only sums. They hypothesise that it is enough to scale noise to the query's sensitivity, meaning the biggest shift a single row can produce, instead of to the database size or the output dimension. Everything below is a theorem; the paper contains no experiments.

## Definitions

- **epsilon-indistinguishable:** take any two databases that differ in one entry, any adversary and any transcript; the log of the ratio between the two transcript probabilities never exceeds epsilon in absolute value.
- **L1 sensitivity of f:** the smallest S(f) bounding the L1 distance between f(x) and f(x') whenever x and x' differ in one entry.
- **Laplace distribution with scale lambda:** a symmetric density that decays exponentially in |y|/lambda, with mean 0.

## The mechanism

Add independent Laplace noise, with scale S(f)/epsilon, to each coordinate of f(x) (Proposition 1). The result is epsilon-indistinguishable for every f whose L1 sensitivity is finite. For adaptive query sequences (Theorem 1), set lambda to the largest sensitivity over the queries the adversary might pose, divided by epsilon; adding Lap(lambda) noise to each answer then stays epsilon-indistinguishable against any adversary. The server may decline queries whose sensitivity exceeds a cap. The budget is therefore charged once over the whole transcript, at the worst sensitivity, not per query.

## Sensitivity examples

- A histogram with d disjoint bins has L1 sensitivity 2 whatever d is.
- A sum of 0/1 entries has sensitivity 1, so noise of scale 1/epsilon.
- For the average of a vector function v of each row (with gamma bounding its L1 norm) the change is at most 2*gamma/n; for the covariance matrix the bound is 8*gamma^2/n.
- Hamming distance to a fixed set has sensitivity 1; so do the weight of a min cut and of a minimum spanning tree when edge weights lie in [0,1].
- The paper contrasts this with the prior SuLQ framework, which puts noise of order sqrt(d)/eps on each coordinate and so, the paper says, inflates total L1 error by a factor of order sqrt(d) for histograms and d for covariance matrices.

## Further results

- Lemma 1: consider a randomized algorithm that reads any given x_i with probability no more than alpha, yet outputs a value close to f(x) (L1 distance up to sigma) with probability (1+alpha)/2 or better; then S(f) is at most 2*sigma. The reverse implication fails, as Reed-Solomon codeword distance shows.
- Theorem 2: in a metric output space, sampling an output with density proportional to an exponential of epsilon times distance, scaled by twice the sensitivity, is epsilon-indistinguishable provided the density normalises. This is an early form of what became the exponential mechanism.
- Theorem 3: any non-interactive epsilon-indistinguishable mechanism over {0,1}^d needs a database with exponentially many rows (2^Omega(d)) to answer parity-style sum queries. Sizes of order 2^(d/4)/sqrt(eps) fall short, and under randomized response (Proposition 2) so do sizes of order 2^(d/3)/eps^(2/3). Interactive mechanisms escape this barrier.
- Group privacy: a mechanism that is eps/k-indistinguishable for single entries is eps-indistinguishable for groups of k. In these forms indistinguishability matches semantic security and implies simulatability.
- Answering a count to within even a constant factor forces epsilon to be at least on the order of 1/n.

## Limits

- The work is purely theoretical, with no experiments, datasets or utility numbers.
- A trusted server is assumed, and neighbouring databases differ in exactly one entry.
- Epsilon is left as a policy decision with no advice on its value; counts need epsilon around 1/n or larger.
- The paper gives the Laplace distribution a standard deviation of lambda; the extraction notes the true figure is sqrt(2)*lambda, and the privacy argument depends only on the scale.
- Theorem 1 bounds sensitivity over every possible transcript, so S has to be known and capped before any answer is given.
- Only pure epsilon is covered; the later epsilon-delta relaxation does not appear here.
- The separation result holds for mechanisms meeting Definition 1 and breaks down under weaker definitions (footnote 4).
- Theorem 2 requires that the density integrate to a finite value.

## See Also
- [[Diffusion Model Training-Data Extraction]] — related (DP-SGD training failed to converge there)
- [[NIST Adversarial ML Taxonomy]] — related (the report recommends differential privacy against membership inference)
- [[Min-K% Prob Pretraining-Data Detection]] — related
