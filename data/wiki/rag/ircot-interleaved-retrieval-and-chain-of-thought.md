---
title: IRCoT Interleaved Retrieval and Chain-of-Thought
tags: [rag, pattern]
summary: "IRCoT alternates generating one chain-of-thought sentence with a BM25 retrieval keyed on that sentence, so few-shot LLMs gather evidence for multi-step questions without any training."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-trivedi-2023-interleaving-retrieval-chain-thought-reasoning.md
---

# IRCoT Interleaved Retrieval and Chain-of-Thought

The premise: the right retrieval depends on what has been worked out so far, so a single retrieval keyed to the question cannot serve multi-step questions. IRCoT begins by running BM25 on the question to fetch K paragraphs. It then alternates a **reason step** (the LLM writes the next chain-of-thought sentence from the question, collected paragraphs and earlier sentences) and a **retrieve step** (the last chain-of-thought sentence is the BM25 query, adding K more paragraphs). The loop stops when "answer is" appears or after 8 steps. All collected paragraphs (at most 15) go to a separate reader: Direct prompting for Flan-T5, chain-of-thought for GPT3. Nothing is trained. The baseline, OneR, is one-step retrieval from the question.

## Results

Setup: Elasticsearch BM25; per dataset (HotpotQA, 2Wiki, MuSiQue, IIRC), 500 test questions drawn from dev, with K and M chosen on 100 further dev questions; averages over 3 sets of demonstrations; at most 15 paragraphs retrieved ("fixed-budget optimal recall"). All self-reported.

- Gold-paragraph recall is higher with IRCoT than with OneR for both GPT3 (code-davinci-002) and Flan-T5-XXL.
- With GPT3 and a chain-of-thought reader, answer F1 beats OneR by 7.1, 13.2 and 7.1 on HotpotQA, 2Wiki and MuSiQue; there is no gain on IIRC despite about 21 recall points.
- With Flan-T5-XXL and a Direct reader, IRCoT beats OneR in answer F1.
- Compared with OneR, generated chains contain 50% fewer factual errors on HotpotQA and 40% fewer on 2Wiki (GPT3; manual annotation of 40 random questions per dataset).
- IRCoT with 3B Flan-T5-XL beats OneR with the 58X larger GPT3.
- With GPT3, IRCoT scores 49.3 EM / 60.7 F1 on HotpotQA; on 2Wiki it scores 57.7 / 68.0, and 34.2 / 43.8 on the 2-hop part of MuSiQue. Two later systems edge it out (DSP by 2.0 on HotpotQA, a newer DecomP by 2.8 on 2Wiki) while it stays ahead on MuSiQue; the comparison is leaderboard-style, not head-to-head.
- For Flan-T5-XXL on HotpotQA, adding a separate reader helps (F1 59.1 against 52.6 without it), while for GPT3 the results are mixed (60.7 against 61.0). Flan-T5-XXL prefers the Direct reader (59.1 versus 52.0 with chain-of-thought); GPT3 prefers the chain-of-thought reader.

## Limits

- Requires an LM that can do few-shot chain-of-thought (rare below 20B parameters) and an input long enough for paragraphs plus demonstrations.
- Each chain-of-thought sentence costs one LLM call; the cost was not measured.
- With code-davinci-002 deprecated, GPT3 numbers are hard to reproduce; the authors expect the trends to hold.
- Other systems are not compared head-to-head, and the retrieved sets are unranked, so no standard IR metrics are given.
- BM25 is the only base retriever, corpora derive from Wikipedia, and there are 500 test questions per dataset. For the smallest model (0.2B), QA does not beat OneR.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[Agentic RAG — Advanced Patterns]] — related
- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Demonstrate-Search-Predict (DSP)]] — alternative-to
- [[Self-Ask Prompting]] — alternative-to
- [[Decomposed Prompting (DecomP)]] — alternative-to
