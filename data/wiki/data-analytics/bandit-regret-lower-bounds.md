---
title: Bandit Regret Lower Bounds
tags: [data-analytics, bayesian-analysis, concept]
summary: "Regret lower bounds for k-armed and linear bandits: the Bretagnolle-Huber inequality and divergence decomposition give sqrt((k-1)n)/27 minimax, an instance-dependent log n rate for consistent policies, high-probability limits, d*sqrt(n) for linear bandits and a case where optimism is arbitrarily suboptimal."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-bandit-algorithms-ch13-lower-bounds-basic-ideas.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch14-foundations-information-theory.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch15-minimax-lower-bounds.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch16-instance-dependent-lower-bounds.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch17-high-probability-lower-bounds.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch24-minimax-lower-bounds-stochastic-linear-bandits.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch25-asymptotic-lower-bounds-stochastic-linear-bandits.md
---

# Bandit Regret Lower Bounds

[[Thompson Sampling and Bandit Regret]] states that good strategies' regret grows at least logarithmically with the horizon. These chapters of *Bandit Algorithms* (Lattimore and Szepesvari) make that precise. Their tools are information-theoretic.

## The basic idea (chapter 13)

The minimax argument reduces a bandit to two-hypothesis testing: choose two instances so that whatever suits one instance hurts on the other (competition) while no policy can reliably distinguish them from data (similarity). On unit-variance Gaussian k-armed bandits with means in [0,1], this gives worst-case regret that grows at least as fast as sqrt(kn), scaled by a universal constant the chapter leaves unspecified (Theorem 13.1; only sketched there, proved in chapter 15). The heuristic builds the first instance with means (Delta, 0, ..., 0) and the second by raising the mean of the arm with the smallest expected pull count to 2*Delta. By pigeonhole that arm has E[T_i(n)] at most n/(k-1), which fixes Delta = sqrt((k-1)/n). The chapter's own caveat: the step assuming E[T1(n)] is about the same under both instances is not proven, since T_i(n) is random; the information-theoretic tools below close it. It also suggests that a policy within a constant of minimax, but far better on easy instances, is preferable to the exact minimax one. The MOSS policy on [[Upper Confidence Bound Bandit Algorithms]] reaches a worst-case bound of order sqrt(kn) (Theorem 9.1 there, stated as 39 sqrt(kn) plus the sum of gaps), matching this up to a constant.

## Tools (chapters 14-15)

- Relative entropy D(P,Q) is the extra code length, on average, paid for using Q's best code on data drawn from P. It lacks symmetry and the triangle inequality, so it is not a distance. For Gaussians with common variance sigma^2 it is (mu1 - mu2)^2 / (2 sigma^2).
- Bretagnolle-Huber: for any event A, P(A) + Q(A^c) is at least (1/2) exp(-D(P,Q)). It is vacuous if P is not absolutely continuous with respect to Q, and holds with D(Q,P) too, so the book advises using the smaller. Pinsker gives 1 - sqrt(D/2) instead, better when D is small and worse when it is large. A single Gaussian observation between means 0 and Delta with Delta^2/sigma^2 at most 1 has an error probability of at least 3/20 under one of the hypotheses.
- Divergence decomposition (Lemma 15.1): for a fixed policy on two bandits, the divergence between the two bandits equals a sum over arms, each term the expected pull count under the first bandit times that arm's own divergence. This turns a regret statement into a statement about expected pulls. The chain-rule form is only an exercise in chapter 14.

## Minimax bound (chapter 15)

For any policy on k-armed unit-variance Gaussian bandits with horizon n at least k-1, regret reaches (1/27)*sqrt((k-1)n) for some mean vector in [0,1]^k (Theorem 15.2). The proof takes means (Delta, 0, ..., 0) with Delta = sqrt((k-1)/(4n)), then a second bandit that raises the least-pulled suboptimal arm to 2 Delta; that arm has E[T_i(n)] at most n/(k-1), bounding the relative entropy by 2 n Delta^2/(k-1). An alternative route (Exercise 15.2) gives a weaker form, (1/8) sqrt(kn). For n below k some bandit has regret above n/2. The chapter notes this does not contradict O(log n) upper bounds, which depend on inverse gaps that may be large.

## Instance-dependent bound (chapter 16)

A policy is consistent over a class if for every bandit and p > 0, R_n / n^p tends to 0. For an unstructured class, any consistent policy has liminf R_n / log n at least a sum over suboptimal arms of gap Delta_i divided by d_inf, the smallest relative entropy from the arm's law P_i to any law in its class whose mean beats mu* (Theorem 16.2). The proof shows liminf E[T_i(n)]/log n is at least 1/d_i, using Bretagnolle-Huber and the divergence decomposition. UCB is asymptotically optimal for unit-variance Gaussian and KL-UCB for Bernoulli bandits, by the chapter's account. Per the chapter, explore-then-commit and elimination methods can never reach asymptotic optimality; even well tuned, they lose a factor of two on standard Gaussian problems (reported from Garivier et al.). Because consistency would permit playing arm 1 for an astronomically long opening stretch (10^100 rounds), the chapter adds a finite-time Gaussian bound (Theorem 16.4) whose leading term for p = 1/2 is about half the asymptotic one.

## High-probability bounds (chapter 17)

For Gaussian bandits with gaps at most one, if a policy's expected regret never exceeds B*sqrt((k-1)n), then a bandit exists on which pseudo-regret passes one quarter of the smaller of n and (1/B)*sqrt((k-1)*n*ln(1/(4*delta))), and it does so with chance delta or more (Theorem 17.1). A tail that scales as log(1/delta) to a power p below 1, times B*sqrt((k-1)n), is impossible for any policy. For adversarial bandits some reward sequence in [0,1] pushes regret past a constant times sqrt(n*k*log(1/(2*delta))) with chance of at least delta (Theorem 17.4, proof sketched), so the Exp3-IX high-probability bounds are tight up to constants. The chapter advises an anytime algorithm when guarantees are needed at every confidence level, paying a further factor of the square root of log(1/delta) over log k. It conjectures, without proof, a policy with tail B sqrt(kn) log(1/delta).

## Linear bandits (chapters 24-25)

- Hypercube action set [-1,1]^d with parameters in {-n^(-1/2), n^(-1/2)}^d and unit-variance Gaussian noise: every policy has regret at least (exp(-2)/8) d sqrt(n) on some parameter, about 0.017 d sqrt(n). The unit ball gives a bound of d sqrt(n)/(16 sqrt 3) for d at most 2n. So the d sqrt(n) of [[LinUCB and Linear Bandit Confidence Ellipsoids]] is near optimal in general.
- Sparsity p in dimension d does not remove the polynomial dependence on d: regret is at least sqrt(p d n)/8, proved on p copies of a k-armed bandit where only the summed reward is seen. With p = 1 this is the finite-armed order sqrt(dn).
- Misspecification: a policy that gets sqrt(n)-order regret on exactly linear problems must pay order k*sqrt(n) on some k-armed instance, so no bound can adapt to the smaller of d*sqrt(n)+eps*n and sqrt(kn). The rates that are achievable, with eps the misspecification, are about d*sqrt(n) + eps*n*sqrt(d) when k is large and, for small k, about sqrt(d*k*n) + eps*n*sqrt(k) (Foster and Rakhlin 2020).
- Asymptotic bound for a finite action set with Gaussian noise and a unique optimal action: every consistent policy has regret growing at least as c(A, theta)*log n. Here c is the optimum of an allocation problem: choose nonnegative weights alpha(a) to minimise the gap-weighted total of alpha, subject to each suboptimal arm's squared length in the inverse of H_alpha = sum_a alpha(a) a a^T not exceeding half its squared gap. A matching policy exists (Theorem 25.3, not proved).
- Optimism can lose here. The example has d=2, arms e1, e2 and (1-eps, gamma*eps), theta=(1,0), with eps small and gamma no smaller than 1. The optimal rate is 2*gamma^2*log n when 2*gamma^2 is at most 2/eps, reached by pulling the clearly bad second arm about 2*gamma^2 times per unit of log n and never the third. An optimistic algorithm whose confidence set stays within radius c*sqrt(log n) measured in the V_t norm, together with gamma of order c^2 or larger, pulls that second arm only about 4c^2*log n times, which forces order log(n)/eps^2 pulls of the nearly optimal third arm; regret then reaches order log(n)/eps and is arbitrarily worse as eps shrinks (the Omega(1/eps) claim is sketched). The chapter says Thompson sampling does not overcome this and advises budgeting exploration for apparently bad but informative arms when actions share information. See [[G-Optimal Design and Phased Elimination]] for a non-optimistic design.

## Limits

- Chapter 13 is a heuristic: the indistinguishability step is unproven, it mentions no Bretagnolle-Huber, KL or log n bound, and the constant c is never given.
- Chapter 14 is foundations with no experiments; Pinsker is stated without proof, and the entropy-coding intuition covers countable alphabets only. It says nothing on KL penalties in RLHF, forward versus reverse KL or estimating KL by sampling.
- Chapter 15's bound holds only for n at least k-1 (smaller horizons are an exercise), uses Gaussian noise for convenient KL, and the constant 1/27 is not claimed to be tight.
- Chapter 16 covers asymptotics and unstructured classes only; given structure, pulls of one arm can inform another. Table values cover parametric families, non-parametric classes being largely open, and with unknown subgaussian constant d_inf is 0 so consistent policies have an infinite lower bound. Theorem 16.4 needs a polynomial regret bound over a neighbourhood.
- Chapter 17: the stochastic results cover Gaussian bandits with gaps below one and presuppose the worst-case expected-regret guarantee; Theorem 17.4's proof is sketched and its constants unspecified; instance-dependent bounds are not covered.
- Chapters 24-25: bounds are worst case over a hand-picked hard action set with unit-variance Gaussian noise, with small constants that are not tight; optimal regret over wide ranges of action sets and the optimal misspecified trade-off are open. Chapter 25 is asymptotic, for finite action sets and consistent policies; parts of Theorem 25.1, Corollary 25.2 and Theorem 25.3 are not proved; algorithms that match it are impractical at finite times and none is also near-minimax.

## See Also
- [[Thompson Sampling and Bandit Regret]] — prerequisite-for
- [[Upper Confidence Bound Bandit Algorithms]] — related (the upper bounds these lower bounds match)
- [[LinUCB and Linear Bandit Confidence Ellipsoids]] — prerequisite-for (the upper bound these match)
- [[G-Optimal Design and Phased Elimination]] — related
- [[Exp4 and Oracle-Based Contextual Bandits]] — related
