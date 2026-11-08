---
title: Delegation Ceiling and Posterior Distortion
tags: [graph, concept]
summary: A decision-theory note argues that a multi-agent network adding no new outside signal can at best match one Bayes decision maker seeing the same signals, and that the cost of passing messages is the distortion of the posterior; MMLU relay experiments show accuracy falling with each prose stage (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-ao-2026-reliability-limits-llm-based-multi.md
  - data/raw/papers/2026-11-06-nechepurenko-2026-coordination-as-architectural-layer-llm.md
---

# Delegation Ceiling and Posterior Distortion

Ao, Gao and Simchi-Levi (arXiv 2603.26993, a March 2026 preprint the authors call a technical note)
give a theory of when splitting a decision across LLM agents can help. The theory is framed over what
information passes between agents, and says nothing about how tokens are generated.

## The ceiling (Proposition 6)

Take any finite acyclic graph of agents whose only inputs are exogenous signals (a shared signal
plus any verifier signal) and whose nodes may use extra randomness independent of the truth given
those signals. For every bounded loss, the expected loss of the network is at least the best loss a
centralized Bayes decision maker achieves from the same signals. Message rules and node rules may be
arbitrary. The proof treats the network output as a randomized garbling of the signals, using a data
processing step (Lemma 2, stated again in Blackwell form in Lemma 4).

## Common-evidence reduction (Theorem 7)

When no node holds a private signal, a multi-agent graph is equivalent to a stochastic encoder from
the shared signal to a finite message. The communication budget is the log of the size of the
terminal state that reaches the output stage; transcript length does not enter. The authors' Remark 2 says the
design object is the experiment induced by the communication interface, not the role label, so an
interface that Blackwell-dominates free text is at least as good as free text. Remark 1 ties the
problem to Bayesian persuasion, rational inattention and the information bottleneck, and notes that
if nodes hold private signals the problem becomes a team decision problem and the reduction fails.

## Communication loss as posterior distortion (Theorem 8)

For a proper scoring rule, the excess loss from passing a message M instead of the full history H
equals the expected divergence between the posterior given H and the posterior given M. Under log
loss this is the conditional mutual information of the truth and H given M; under the Brier score it
is the expected squared distance between the two posteriors. On a serial chain under log loss the
loss adds up stage by stage. Remark 4 says transcript length, role count and round count are the
wrong proxies, and an added stage that keeps the posterior intact need not make a system worse.

## Does a stage add information? (Corollary 9, Theorem 10)

Adding a verifier signal strictly lowers the best achievable loss for some bounded loss exactly when
the pair of message and signal is not dominated by the message alone. The authors give the reading
that self-critique re-reading only the message cannot move the envelope, while executable tests or
external validators can. For selective human or expert review (Theorem 10), the optimal value takes
the smaller of automated risk and review loss at each history, so review should trigger on
posterior risk and not on stage count, disagreement alone or blanket rules. Remark 3 warns that
architecture comparisons which also change tools, retrieval or workspace size confound the
architecture with a change in information.

## Experiments (self-reported)

- **Relay with no new signal.** 200 four-way MMLU questions, prose relay in which later stages do not see the
  original question. For gpt-4.1-mini the single agent scored 90.7% and the relay scored 41.2% (2 agents),
  43.5% (3) and 22.5% (5); for o4-mini the single agent scored 89.9% and a 3-agent relay 37.0%. The 5-agent figure is
  below the 25% chance level.
- **Structured interface.** 50 MMLU questions, gpt-4.1-mini, 750 runs per condition: a 3-stage relay
  passing a probability vector reaches 75.2%, while a 3-stage prose relay reaches 58.1%.
- **Tools.** gpt-4.1-mini on a synthetic knowledge base of 200 fictional entities: 24.3% without the
  tool, 82.7% with it. On MMLU, a single agent with Wikipedia scored 87.2%, while Wikipedia plus
  Semantic Scholar specialists and two Wikipedia specialists both scored 89.8%.
- **Distortion and accuracy.** On gpt-4.1-mini only, the per-question correlation between posterior
  divergence and accuracy drop is 0.72 (3-agent relay) and 0.44 (5-agent relay).

## Limits

- The theory covers the common-evidence regime, meaning settings with no fresh outside signal;
  the authors concede the reduction no longer applies with private signals. It does not cover extra
  inference compute on the same evidence, and Proposition 6 leaves open gains from parallel
  samples or aggregation.
- The experiments use MMLU, which the authors say is not a planning benchmark, with two OpenAI
  models. The relay hides the original question on purpose, so the collapse is a worst-case
  bottleneck and not a typical design. Posteriors are token-probability proxies, interpreted
  qualitatively by the authors, and no multi-agent condition beat the single agent.
- Internal inconsistencies noted by the extraction: the 58.1% prose figure (50-question subset)
  conflicts with 43.5% in the main table (full set); one figure labels the MMLU baseline 82.4 and 87,
  whereas the text gives 90.7; the table lists the o4-mini baseline at 0.899 beside the 0.907
  gpt-4.1-mini one. Check these before quoting a single figure.
- A v1 preprint that cites Kim 2025, Xu 2026 and Wan 2025 as empirical neighbours and engages no
  later literature.

## A topology comparison under controlled information (Nechepurenko, self-reported)

Nechepurenko's preprint compares five coordination topologies with the information available to agents held fixed: sequential, ensemble, orchestrator, debate and consensus. The task was forecasting 100 Polymarket markets with claude-opus-4-6, scored by Brier score (lower is better). Results were 0.153 sequential, 0.159 ensemble, 0.162 orchestrator, 0.170 debate and 0.181 consensus, against 0.152 for the market price itself. None of the differences is significant after Bonferroni correction. The extraction frames this as consistent with topology mattering less than information when information is controlled; the result is one model on one task family.

## See Also
- [[Multi-Agent Failure Modes at Scale]] — prerequisite-for (a measured information-loss account of why relays degrade)
- [[Multi-Agent Topology Patterns]] — prerequisite-for
- [[Multi-Agent Context]] — related (what each agent sees)
- [[Verification Loops]] — related (the verifier-signal test)
- [[Protocol-Driven Multi-Agent Collaboration]] — related (measured protocol effects)
