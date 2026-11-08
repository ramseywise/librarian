---
title: SAFE Long-Form Factuality Scoring
tags: [eval, pattern]
summary: "SAFE splits a long answer into atomic facts, searches Google for each and labels it supported, not supported or irrelevant; F1@K then combines the counts. It agreed with crowd annotators on 72.0% of 16,011 biography facts and cost $0.19 per response against $4 for humans (self-reported), with the LongFact prompt set used to rank 13 models."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-wei-2024-long-form-factuality-large-language.md
---

# SAFE Long-Form Factuality Scoring

Wei et al. (arXiv 2403.18802, NeurIPS 2024) propose three linked pieces: **LongFact**, a prompt set; **SAFE**, an LLM judge that uses Google Search; and **F1@K**, a response-level score.

## SAFE pipeline

1. Split the response into **atomic facts**, each a sentence carrying one piece of information.
2. Rewrite each fact so it stands alone.
3. Check whether the fact is relevant to the prompt, using "Foo / Not Foo" labels.
4. Rate relevant facts supported or not supported by issuing exactly five Google Search queries (via Serper), three results each, to a gpt-3.5-turbo-0125 model.

The response is then described by counts of supported (S), not-supported (N) and irrelevant facts. **F1@K** uses precision S/(S+N) and recall min(S/K, 1), with irrelevant facts dropped. K is a subjective choice.

## LongFact

LongFact has 2,280 GPT-4-generated prompts over 38 topics, split evenly into Concepts and Objects. The benchmark run takes 250 of the Objects prompts, appends a "be specific" instruction, and samples at temperature 0 with up to 1,024 output tokens.

## Results (self-reported)

- **Agreement with humans.** On 496 FActScore biography prompt-response pairs, SAFE matched crowdsourced labels on 72.0% of 16,011 facts. Only the checking steps were tested, since humans had already split the facts.
- **Adjudicated disagreements.** On 100 random disagreements, the authors' re-annotation with full web search judged SAFE right 76% of the time, the crowd right 19%, neither 5%.
- **Cost.** $96.31 for 496 responses ($0.19 each) against the $4 per response that the earlier FActScore work reported.
- **SAFE's own errors.** Of 24 error cases, the authors count 10 reasoning, 9 search and 5 revision errors; the pie labels extract ambiguously.
- **Response level.** Pearson r was 0.912 for supported counts, 0.662 for not-supported and 0.313 for irrelevant. For fact counts after SAFE's own splitting, r = 0.798.
- **Professional domains.** Agreement was 79.7% (106 of 133) for law and 94.9% (130 of 137) for medicine, on 6 questions with researcher labels; errors came mostly from splitting and rewriting.
- **Ranking.** F1@64 correlated with Chatbot Arena Elo at r = 0.754 (p = 0.031) over 9 models, where precision by itself gave only 0.502 (p = 0.205). On 13 models GPT-4-Turbo led (F1@64 95.0, F1@178 66.4); Claude-3-Haiku had the best precision (92.8) with low recall. Precision spanned only 82.0 to 92.8. Asking for shorter answers raised precision for GPT-4-Turbo.

## Limits

Beating crowd workers is not shown to beat all humans, and no expert comparison exists. Labels mean "supported by search results", not true. The 76/19 result partly reflects access: crowd annotators had one Wikipedia page, SAFE and the adjudicators the open web, and the adjudicators were the authors, unblinded, n = 100. The 72% figure is biographies only. There are no error bars. Repeating one supported fact inflates F1@K, and the choice of K is subjective. The judge model, model list, prices and Elo scores date from early 2024. SAFE checks against the open web, not against a supplied context, so it says nothing about RAG faithfulness.

## See Also
- [[Tool-Augmented Factuality Checking]] — related (FacTool is the closest earlier tool-based checker)
- [[Chain-of-Verification]] — related (FActScore is its biography metric)
- [[Grounding Claim Methodology]] — alternative-to (faithfulness to retrieved context rather than to the web)
- [[LLM-as-Judge Evaluation]] — related
