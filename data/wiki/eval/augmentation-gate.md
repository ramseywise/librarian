---
title: The Augmentation Gate
tags: [eval, rag, concept]
summary: "The A in RAG is the gate nobody evaluates — retrieval can be perfect and generation can be sound while the failure lives entirely in how much retrieved context got handed to the model."
updated: 2026-08-04
sources:
  - own-prose
---

# The Augmentation Gate

You cannot evaluate a RAG system with one metric. A bad answer can come from bad
retrieval, bad augmentation, bad generation, or a bad corpus — and the fix for each is a
different piece of work by a different person. A single end-to-end score tells you the
system is wrong; it does not tell you who has to fix it. That is the argument for
component gates, each with its own dataset and its own pass condition
([[RAG Eval Gate Contract]]).

The gate people forget is the **A**.

> Augmentation is the front runner to what we now call context engineering. The question
> isn't whether the right passage was retrieved — it's whether we handed the model the
> right *amount* of context, or dumped a dozen passages on it and caused the hallucination
> ourselves.

## Why the A hides

Retrieval and generation both have obvious owners and obvious metrics. Retrieval has
recall@k, precision@k, hit rate, MRR — all mechanically computable against a golden set.
Generation has LLM-as-judge faithfulness and relevance. Augmentation sits between them
with **no natural metric**, because it is not a component that produces an artifact you
can score. It is a *decision about how much of the retrieved set to use*, and the decision
is usually implicit: whatever top-k the retriever returned, concatenated.

That is why the failure is invisible in the standard decomposition. Run the numbers on a
system that stuffs twelve passages into every prompt and you see high recall (the right
passage is definitely in there) and a mediocre faithfulness score. The retrieval gate
passes. The generation gate fails. The natural conclusion — *the model is hallucinating* —
is wrong, or at least incomplete: **the model was handed a context in which the right
answer was one of twelve competing candidates, and it picked wrong.** Retrieval did its
job by including the answer. Augmentation failed by not excluding the other eleven.

The diagnostic that separates the two is cheap: **re-run the failing rows with only the
gold passage in context.** If the answer is correct, retrieval and generation are both
fine and the defect is augmentation. If it is still wrong, generation owns it. This
distinction is not available from an end-to-end score at any sample size.

## What it means to say more context is not free

The intuition that retrieval should return more to be safe is what produces the failure.
More retrieved context adds distractors, and distractors are not inert — they compete for
attention, and a plausible-but-wrong passage is a *better* distractor than an irrelevant
one, because it is topically adjacent to the query that retrieved it. Retrieval is
adversarial to itself here: the passages ranked 5–12 are the ones most similar to the
gold passage without being it. See [[Why Context Is Finite]] for the mechanism.

So the augmentation decision has a real optimum, not a monotone. The levers:

| Lever | Question it answers |
|---|---|
| **top-k after rerank** | How many passages actually enter the prompt |
| **Score thresholding** | Whether a weak candidate enters at all, or the set comes back short |
| **Deduplication** | Whether three chunks of the same document count as three pieces of evidence |
| **Compression / extraction** | Whether the model sees the passage or the relevant sentences from it |
| **Ordering** | Where in the window the strongest evidence sits |
| **Empty-set handling** | What the prompt says when nothing passed the threshold |

The last one is the most-skipped and the most consequential. A retriever that returns
nothing above threshold has produced useful information — *we cannot answer this from the
corpus* — and a pipeline that silently proceeds with an empty or weak context converts
that signal into a hallucination. Refusal is a correct output. See
[[Safeguards Architecture — Five Protection Layers]], where this is Layer 3.

## Ordering the gates

The gates run in dependency order, because an upstream failure makes downstream scores
uninterpretable:

1. **Corpus quality first.** If the answer isn't in the corpus, no retrieval config finds
   it and no prompt fixes it. Scoring retrieval against rows whose source was never
   indexed measures nothing. This is why [[RAG Eval Gate Contract]] maintains
   `retrieval_eligible_gt` as a distinct row pool.
2. **Retrieval second** — recall@k, precision@k, hit rate, MRR against the golden set.
3. **Augmentation third** — given that the right passage is retrievable, does the assembled
   context help or hurt?
4. **Generation last** — LLM-as-judge for faithfulness and relevance, on rows where the
   first three passed.

Running them out of order is the common mistake, and it is expensive in a specific way:
LLM-as-judge is the costliest gate, and running it over rows that failed upstream spends
the expensive budget measuring a defect the cheap gate would have named for free.

## The link to context engineering

Augmentation is context engineering scoped to one pipeline. Every question the
augmentation gate asks — how much, in what order, compressed how, and what to do when
there is nothing good — is the same question [[Context Engineering]] asks for an agent turn,
with retrieval as the only source. Treating it as a gate is what makes it measurable
rather than a matter of taste, and the reason it is worth naming separately from
retrieval is that **the team that tunes the retriever and the team that writes the prompt
will both correctly conclude the problem is not theirs.**

## See Also
- [[RAG Eval Metrics Suite]] <!-- auto-linked -->
- [[RAG Eval Gate Contract]] — extends (the gate ladder this argues has a missing rung)
- [[RAG Evaluation]] — complements (component metrics for the other gates)
- [[Why Context Is Finite]] — depends-on (why added context degrades rather than dilutes)
- [[Context Engineering]] — instance-of (augmentation is context assembly with one source)
- [[Safeguards Architecture — Five Protection Layers]] — implements (Layer 3, the retrieval quality gate)
- [[RAG Retrieval Strategies]] — prerequisite-for (the retrieval decisions this gate audits)
