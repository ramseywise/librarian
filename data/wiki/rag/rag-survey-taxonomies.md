---
title: RAG Survey Taxonomies
tags: [rag, reference]
summary: Two surveys' maps of the RAG design space, one by pipeline phase and retrieval-loop type (2024), one adding a structuring axis (2025); mostly vocabulary, with only borrowed numbers as evidence.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-zhao-2024-retrieval-augmented-generation-rag-beyond.md
  - data/raw/papers/2026-11-06-tonmoy-2024-comprehensive-survey-hallucination-mitigation-techniques.md
  - data/raw/papers/2026-11-06-huang-2024-survey-retrieval-augmented-text-generation.md
  - data/raw/papers/2026-11-06-jiang-2025-survey-retrieval-structuring-augmented-generation.md
  - data/raw/papers/2026-11-08-hu-2024-rag-rau.md
  - data/raw/papers/2026-11-07-asai-2023-retrieval-based-language-models-applications.md
  - data/raw/papers/2026-11-07-singh-2025-agentic-retrieval-augmented-generation.md
  - data/raw/papers/2026-11-08-zhang-2024-agentic-information-retrieval.md
---

# RAG Survey Taxonomies

These sources give names to the choices in a retrieval-augmented pipeline. None runs experiments; the figures below are copied from other papers.

## Huang and Huang (2024): phases and loop types

- **Four phases:** pre-retrieval (covering indexing, query manipulation and data modification), then retrieval, then post-retrieval (re-ranking and filtering), then generation (enhancing and customization). Multi-hop pipelines repeat the same four phases.
- **Five retrieval strategies:** basic (one pass), iterative (loop to a stop condition), recursive (sub-queries by depth), conditional (rule-based branching) and adaptive (query adjusted from feedback). Examples they give: Atlas and REPLUG (basic), IRCoT (iterative), SURGE (recursive), CRAG (conditional), FLARE and Self-RAG (adaptive).
- **Filtering is not re-ranking:** reflection tokens, empty compressor summaries and strip scoring remove content, while re-rankers only reorder.
- **Borrowed evidence (self-reported by the cited papers):** on the MIRAGE medical benchmark with GPT-3.5, average accuracy without retrieval is 60.69, and BM25 over PubMed lifts it to 69.23 (a Wikipedia corpus gives 57.74). Combining four retrievers with reciprocal rank fusion scored 59.14 on Wikipedia, below the two-retriever 60.14, which the text blames on SPECTER. Via BERGEN and eRAG, the survey reports retrieval quality mattering more than generator size, and a 7B model with retrieval beating a 70B closed-book model.

## Jiang et al. (2025): adding a structuring axis

This KDD '25 survey organises work by retrieval, structuring and generation. Its argument is that plain RAG over unstructured passages mixes non-atomic facts and struggles with multi-hop questions, so a structure step (knowledge graph, taxonomy, community summaries) should sit between retrieval and the LLM. It lists HippoRAG, GraphRAG and taxonomy-guided retrievers, and RL-trained query rewriting (DeepRetrieval, s3). It proposes a loop in which a taxonomy-aware retriever feeds a query-specific evolving graph that prompts the next sub-query; the survey never runs it.

## Hu and Lu (2024): retriever-LM interaction modes

A preprint survey covering retrieval-augmented understanding (RAU) as well as generation. It writes a retrieval-augmented LM as a function F of the input x and retrieved information z, and names three interaction modes: sequential single (top-K documents, then one generation), sequential multiple (rounds of generate and retrieve) and parallel, where retriever and LM outputs are combined by weighted interpolation as in [[kNN-LM Nearest Neighbor Language Models]]. Retrievers are grouped as sparse, dense, internet or hybrid; LMs as autoencoder, autoregressive or encoder-decoder; enhancements as retriever-side (quality control, timing), LM-side or overall. Its practical advice has two parts: match the interaction mode to the task (single for simple QA, multiple for dialogue and multi-hop), and filter or rerank web retrieval using BM25 or TF-IDF to reduce noise. The figures it quotes (for example RACE gains of 6 to 38 percent on code summarisation, ITER-RETGEN peaking at seven iterations on StrategyQA) are reported from cited work without full setups.

## Asai et al. (2023): datastore unit and integration point

An ACL tutorial proposal, with no evaluation. It sorts retrieval-based LMs by how retrieved text is integrated (appended to the input, fused in intermediate layers as in [[RETRO Chunked Cross-Attention Retrieval]], or interpolated at the output) and by the unit stored in the datastore (a text chunk, a token or an entity mention). It cites, without a figure, the claim that retrieval-based LMs can beat larger parametric ones, and concedes they can still produce plausible wrong text and leak private corpus data.

## Tonmoy et al. (2024): hallucination-mitigation catalogue

A preprint survey dated 8 January 2024, covering work up to about December 2023, that lists more than 32 mitigation techniques with no experiments of its own. It has two top-level classes, prompt engineering and model development, and places RAG inside prompt engineering, split by whether retrieval comes before, during or after generation. Among its entries, EVER works during generation, while RARR and CoNLI correct output after it; CoVe is a verification loop, and CAD, MixAlign, R-Tuning and HAR address context use. A method that appears there and has its own page here is [[RARE Retrieval-Augmented Reasoning]].

## Zhao et al. (2024): four query levels

A preprint survey with no experiments that sorts RAG queries into four levels, from L1 explicit facts to L4 hidden rationales, and matches each level to the techniques suited to it.

## Singh et al. (2025): agentic RAG by architecture

A preprint survey that traces RAG paradigms (naive, advanced, modular, graph, agentic) and classifies agentic RAG on four axes: agent count, control structure, degree of autonomy and knowledge representation. Its architecture names are single-agent router, multi-agent, hierarchical, corrective (five agents covering retrieval, relevance evaluation, query refinement, external retrieval and synthesis), adaptive (a classifier picks single-step, multi-step or no retrieval, as in [[Adaptive-RAG Query Complexity Routing]]) and agentic document workflows. Claims it makes without data:

- Agentic designs are not the default: they add coordination, latency and cost, and modular RAG serves simple fact retrieval.
- Retrieval quality stays the main bottleneck, and agentic reasoning cannot make up for poor retrieval.
- Hierarchical and corrective designs gain reliability through oversight at higher latency; single-agent favours simplicity, multi-agent scales at coordination cost.
- Autonomy calls for bounds on how far ahead an agent plans, rules for using tools and rules for stopping, and evaluation should be process-aware because current benchmarks score output quality only.

Its use-case figures (20 percent, 15 percent, 50 percent, $15,000) are fictional example outputs, the extraction notes.

## Zhang et al. (2025): agentic IR as a policy over information states

A perspective paper that redefines IR from acquiring relevant items to steering a user toward a chosen end state of information, with an LLM agent as the policy. It formalises information state, action, policy, a transition graph over states and a reward supplied by a verifier, with the objective of maximising expected reward of a trajectory against the target state. Classic IR appears as the special case where the state covers only the retrieved items on show and the only actions filter a fixed corpus. It proposes trajectory-level evaluation (utility, efficiency, ethics) in place of list-level relevance, diversity and fairness, and notes that scoring against a single reference trajectory is biased, as many different trajectories can end in the same state. An agent is bounded by its tools: with no reservation API it can find flights but cannot book. No experiments or datasets.

## Limits

- The Tonmoy and Zhao surveys report no measurements, and the former covers work only up to about December 2023.
- Surveys with no controlled comparison; claims such as "iterative rounds generally do better" reflect how the authors read a table of studies.
- Huang's numbers come from one domain (medical QA) and one model; coverage stops in early 2024 and misses long-context and agentic RAG. The Fig. 5b gains have no model mapping in the extraction.
- Hu and Lu run no experiments of their own, coverage ends in early 2024 (no agentic or reasoning-RL retrieval), the method tables carry no metrics, and the extraction notes swapped RoBERTa and BERT citations. The Asai tutorial is a 2023 proposal with every benefit cited to other work without numbers.
- The ratings Singh gives each architecture (Low, Moderate, High) are qualitative with no source, and the architectures mostly derive from blogs and tutorials rather than evaluated papers; the authors concede benchmarks miss process. Zhang's transition graph ranges over the user's real-world state, which cannot be computed, its verifier is left to rules, annotators or an LLM judge, and its case studies cite commercial products without evaluating them.
- Jiang's structuring loop is a proposal; it gives no cost, latency or hybrid-chunk comparison. The extraction notes mis-attributed references in the reference list (e.g. a Self-Refine entry and a PaLM 2 blog post), so check citations before reuse.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[Knowledge Graph Retrieval]] — related
- [[RAG Reranking]] — related
- [[Reciprocal Rank Fusion]] — related
- [[Agentic RAG — Advanced Patterns]] — related
- [[Adaptive-RAG Query Complexity Routing]] — instance-of (the adaptive architecture in Singh's list)
- [[Knowledge Graph Prompting for Multi-Document QA]] — related
- [[Atlas Retrieval-Augmented Few-Shot Learning]] — related
- [[Generate-then-Read Contextual Documents]] — related
- [[kNN-LM Nearest Neighbor Language Models]] — related (the parallel-interpolation mode)
- [[RETRO Chunked Cross-Attention Retrieval]] — related (intermediate-layer fusion)
- [[FLARE Forward-Looking Active Retrieval]] — related
