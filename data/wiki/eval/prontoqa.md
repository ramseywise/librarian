---
title: PrOntoQA
tags: [eval, reference]
summary: A synthetic first-order-logic question set over fictional ontologies, with unique parseable proofs, used to check chain-of-thought step by step rather than by final label.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-saparov-2022-language-models-greedy-reasoners.md
---

# PrOntoQA

PrOntoQA (written PRONTOQA in the source) is a synthetic question-answering dataset built to test chain-of-thought reasoning formally. Each example starts from a randomly drawn linear ontology and a modus-ponens proof, which is then written out in plain natural language. Each example has a unique, parseable gold proof, and difficulty is programmable (number of hops, true, false or fictional ontology, top-down or bottom-up ordering). Fictional ontologies are meant to separate reasoning from retrieved world knowledge.

## How it is used

The paper prompts models with eight CoT demonstrations and decodes greedily. It parses each sentence the model writes and classifies it against the gold proof. Its taxonomy has three classes:

- strictly-valid atomic step (canonical): provable from earlier steps with one gold-proof rule and on the gold path;
- misleading step: its premises are in the gold proof but its conclusion is not;
- broadly-valid step: valid only under a richer rule set than the gold proofs use (in this case, subtype transitivity).

Proof accuracy counts a proof as correct when some route from the premises to the conclusion uses only the allowed step classes.

## Findings reported by the paper (GPT-3 family, 2022)

- Most predicted steps from text-davinci-002 on 5-hop fictional ontologies are strictly valid, and invalid steps are a small share (the text gives no numbers; results are bar charts).
- Failures are planning failures: in wrong proofs, the earliest step that departs from the canonical path is usually a misleading atomic step, and models seldom recover from it.
- Only text-davinci-002 beats chance, and among the smaller models accuracy climbs across the 350M, 1.3B and 6.7B sizes. A true ontology gives much higher accuracy that holds from 3 to 5 hops. With fictional ontologies and top-down order at five hops, accuracy falls to chance, and top-down ordering gets harder than bottom-up as hops increase.
- Self-consistency (40 samples, temperature 0.7) and in-context depth-first-search traces did not improve valid proof accuracy (setup: 100 examples, text-davinci-002, five hops, fictional ontology, top-down).
- Over 48 experiments, final-label accuracy tracked strict proof accuracy poorly and tracked valid proof accuracy best.

Later work used it as a first-order-logic evaluation set; for instance, SymbCoT reports 99.60 on 500 PrOntoQA items with GPT-4 (self-reported).

## Limits

- Covers only modus ponens, proofs up to five hops, simple sentences and linear ontologies; longer proofs, other inference rules and complex sentences are untested.
- The models are 2022 OpenAI API models; no later models were evaluated. The authors could not explain why text-davinci-002 far outperforms the 001 versions, and name the token limit as one possible factor.
- Most main results appear only as bar charts with few numbers in the text; the self-consistency and search tests ran 100 examples in a single configuration.
- The authors judge CoT insufficient for harder mathematical reasoning and point to neurosymbolic search, which they do not test.

## See Also

- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Symbolic Chain-of-Thought (SymbCoT)]] — extends
- [[Self-Consistency]] — related
- [[ROSCOE Reasoning Chain Metrics]] — alternative-to (step-level reasoning evaluation)
