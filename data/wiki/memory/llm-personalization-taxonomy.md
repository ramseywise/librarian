---
title: LLM Personalization Taxonomy
tags: [memory, concept]
summary: "A 2025 survey organises personalised LLMs by granularity (user, persona, global), technique (RAG, prompting, representation learning, RLHF) and evaluation; it is qualitative, relies mainly on LaMP and LongLaMP, and says nothing on agent memory stores or forgetting."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-zhang-2024-personalization-large-language-models.md
---

# LLM Personalization Taxonomy

The survey (TMLR, arXiv v3 July 2025) asks how two separate lines of work, personalised text generation and downstream personalisation such as recommendation, can sit under one taxonomy. The authors hypothesise that the two directions are essentially one and will converge. It defines personalisation as tailoring output to the preferences, needs and characteristics of a user or group, and splits usage into direct (the personalised text is evaluated) and indirect (generated text or embeddings improve a downstream task).

## Axes of the taxonomy

- **Inputs about a user.** User documents (their own writing), attributes (static traits such as age or occupation) and interactions (clicks, purchases). An adaptation function folds the user data into the prompt, and a retrieval module is one example.
- **Granularity.** User-level (one person, needs enough data), persona-level (a group described in natural language) and global preference (norms shared by the public, used through RLHF). The survey proposes layering them: user level suits frequent users, persona level occasional ones and global preference new ones, starting at persona level and moving to user level as data accrues.
- **Technique.** Retrieval-augmented generation, prompting (contextual, persona-based, profile-augmented, prompt refinement), representation learning (fine-tuning, PEFT, user embeddings) and RLHF.
- **Evaluation.** Intrinsic (score generated text against user-written text) against extrinsic (task metrics on the downstream application).

## Practices it recommends

- Pick the technique by constraint: retrieval for large or changing profiles, prompting where brief history fits without retraining, representation learning when per-user data and compute are plentiful, RLHF-style methods when pairwise preference data exists.
- Retrieve or summarise rather than pasting a whole history, since profiles exceed context limits and irrelevant text distracts the model. Combine sparse (BM25) and dense retrieval.
- Keep user data current; stale attributes are a named failure. Interaction history alone may not reflect current preferences.
- Where user-written text exists, score against it, and pair any LLM judge with human evaluation. Anonymise demographic data and protect personal information.

## Reported results

These are findings from the works the survey cites, not experiments it ran.

- Richardson et al. report that BM25 retrieval plus LLM-written user summaries improved LaMP results while retrieving 75% less user data.
- Kang et al. find that zero-shot LLMs trail traditional recommenders for rating prediction but match or beat them after fine-tuning on minimal interaction data, with 100B+ models doing better.
- The survey judges that dense retrievers generally beat sparse ones but need task training; it gives no numbers.
- Prompt-based personalisation degrades as the context window saturates, while fine-tuning and user embeddings reach further yet overfit if data per user is thin.
- Weissburg et al. find all tested LLMs show bias as personalised educators, the attributes hit hardest being income and disability status.

## Limits

- Survey only: no experiments or shared-number comparison, and the effectiveness discussion is qualitative, resting on LaMP and LongLaMP.
- The authors concede there is no comprehensive quantitative metric for degree of personalisation, and know of no LLM-as-a-judge framework for it; judges risk persona injection, self-favouring and positional bias.
- Cold start has had little study, and many datasets exclude users with under five interactions. Black-box retrieval through search APIs is excluded.
- Memory is mentioned only within application examples, and the survey does not discuss agent memory stores, write policies or forgetting. Cited work mostly ends in mid-2024, which dates it on agent-memory systems.

## See Also
- [[Memory Forms Taxonomy]] — related (a taxonomy of agent memory; this one covers personalised output instead)
- [[Memory-Augmented Conversational RAG]] — related
- [[PERSONA-CHAT]] — related (persona-conditioned dialogue)
- [[Context Window Budgeting]] — related (retrieve or summarise profiles to fit the window)
