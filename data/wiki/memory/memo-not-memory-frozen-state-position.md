---
title: "Memo, Not Memory: Frozen State Position"
tags: [memory, concept]
summary: "A position paper argues that context-only agent memory leaves the generator's adaptive state unchanged, so it is a memo rather than learning, supports this with a conditional Omega(k^2) lower bound on stored examples, and proposes a hybrid of deletable retrieval plus audited asynchronous consolidation; it has no new experiments."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-xu-2026-contextual-agentic-memory-memo-not.md
---

# Memo, Not Memory: Frozen State Position

This position paper (a preprint: one theorem, zero new experiments) separates two ways an agent can change. One path updates the generator's persistent adaptive state, written theta, through pre-training, fine-tuning, reinforcement learning or adapters. The other changes only the context C, through prompting, retrieval, tool protocols, skill files or scratchpads. The authors place MemGPT, retrieval-augmented generation, Reflexion and Voyager on the second path and call the result a memo: useful, but not learning.

## The Frozen State invariant

For an agent that works only by context engineering, theta stays equal to its starting value across sessions. Assisted performance may rise a great deal, but competence when the stored trace or rule is withheld does not. The paper cites the MemGPT team as conceding that appending raw experience approximates learning poorly, and says their sleep-time compute still rewrites context tokens, not weights.

## The conditional bound

Theorem 1 states a conditional result. Suppose a frozen contextual system still errs on held-out items by some margin. Then retrieval needs on the order of k squared stored compositional examples for k base concepts, while a parametric learner of complexity d needs about d examples regardless of k. The ratio is Omega(k squared over d). The proof counts coverage. Pairs held in the store come out right, while unseen pairs are answered no better than a fixed ceiling. Conditions matter:

- It requires Assumption 1, that the frozen model stays below that ceiling on held-out pairs even with K demonstrations. Once the contextual system hits the target accuracy, the theorem is silent.
- Pairs are assumed sampled uniformly, and the parametric class must be realizable.
- The constructive example is modular arithmetic with VC dimension 1. The paper calls it an existence proof, and the extraction notes that the claim that frozen models do poorly on it is asserted, not measured.
- A longer window alone does not move the finite bound while a margin remains.

## Security and hybrid design

Persistent writes can carry one session's injected instruction into later sessions. The numbers the paper quotes belong to other work: MINJA at 98.2% injection success, PoisonedRAG at 90% attack success from five adversarial texts for each targeted query, and InjecAgent covering 30 agents. The probability of at least one poisoned write approaches one as writes accumulate, under independence and no detection. The authors frame retrieval stores as inspectable and deletable, and consolidation into weights as harder to audit and undo, and say this compares attack paths, not safety.

Their recommendation, drawing on complementary learning systems, keeps scoped, deletable episodic retrieval as the working substrate and adds an asynchronous consolidation channel (adapters, model editing, test-time training, self-distillation) with trace provenance, versioned checkpoints and regression guards. Raw or temporary user data stays in retrieval.

## Proposed metric

Compositional Generalization over Time exposes an agent to concepts only in isolation across T sessions, then tests novel combinations in four arms (retrieval, retrieved-rule summaries, consolidation, hybrid) with compute matched and the trace withheld. The authors say LoCoMo and LongMem measure recall, not learning.

## Limits

- The authors state no frontier-model experiment with matched compute demonstrates the effect, and the comparisons that exist vary by task.
- Large-scale reliable consolidation is not shown; forgetting, interference and unlearning remain open.
- The result is conditional on a measured accuracy ceiling and is no ranking of in-context learning against fine-tuning.
- An appendix admits an earlier margin claim was too strong.
- Label glitch noted by the extraction: the paper's text cites "Assumption 3.2" where it means Assumption 1.
- The extraction notes that the domain examples are asserted, the attack and context-saturation numbers belong to other papers, and several citations are unchecked 2026 preprints. Treat it as an opinionated position, not an empirical result.

## See Also
- [[Memory Architecture]] — prerequisite-for
- [[Memory Forms Taxonomy]] — related (its working, episodic, semantic and experiential rows)
- [[MemGPT / Letta Virtual Context Memory]] — related (the system the paper critiques)
- [[Self-Learning Agents]] — related
