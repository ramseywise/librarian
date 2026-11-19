---
title: Extracting Training Data from Language Models
tags: [llm, interpretability-and-safety, concept]
summary: "Carlini et al. (2020) recover 604 verbatim training examples, including personal data and code, from black-box GPT-2 XL by sampling widely and ranking samples with membership-inference metrics; larger models memorise more (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-carlini-2020-extracting-training-data-large-language.md
---

# Extracting Training Data from Language Models

Carlini, Tramer, Wallace et al. ask whether an adversary with only black-box query access can recover verbatim training examples from a large language model that shows almost no train-test gap. They state the hypothesis that worst-case training examples are memorised and extractable even then. GPT-2 was trained about 12 epochs on 40GB with training loss only about 10% below test loss (reported).

## Definitions

- A string is **extractable** if some prefix makes it the argmax continuation of length N.
- It is **k-eidetic memorised** if it is extractable and appears in at most k training examples.
- The authors note that the first definition admits pathological cases such as a prompt that says "Repeat the following sentence".

## The attack

1. Draw 200,000 samples of 256 tokens from GPT-2 XL with each of three strategies: top-n, temperature, and prompts taken from Internet text (Common Crawl prefixes).
2. Score every sample set with six membership-inference metrics. The extraction names perplexity and comparisons against references: a smaller LM, zlib compression, lowercased text and a sliding window; it does not list all six.
3. After fuzzy deduplication, keep 100 candidates per configuration from among the 1000 top-scored, then verify them with Google search and with the GPT-2 authors' lookup in the training set.

## Results (self-reported, GPT-2 XL)

- 604 unique memorised training examples among 1,800 inspected candidates (3 sampling x 6 ranking configurations, 100 candidates each).
- The strongest setup, Internet-prefix prompts scored with zlib, has 67 memorised among its 100 candidates. Plain perplexity ranking works poorly for top-n and temperature sampling.
- Pooling all six rankings, top-n sampling yields 191 unique memorised samples and Internet conditioning 273.
- Among memorised samples, 46 name individuals and 32 contain contact details (16 business, 16 private); names from news are not counted.
- High-entropy memorised strings exist even at k=1; one is 87 characters long and appears 10 times inside a single document.
- Seeding beam-search-like decoding with a memorised snippet recovers a 1450-line verbatim source file.
- Context changes recall: with greedy decoding, the prompt "3.14159" gives 25 digits of pi, "pi is 3.14159" gives 799, extra context gives 824, and beam search 500.
- Loose lower bound: 604 memorised hits imply at least 0.1% of 600,000 ordinary generations hold memorised text, though only 1,800 were inspected.

## Size and repetition

- Prompting with one fixed URL prefix and taking 10,000 top-n generations, GPT-2 XL (1.5B) outputs each Reddit URL that was inserted at least 33 times in a single document; Medium (345M) outputs about half of them and Small (117M) none.
- In one setting the 1.5B model memorises more than eighteen times the content that the 124M model does.

## Limits

- Four authors checked the candidates by hand, covering only 1,800, so 604 is a lower bound; recall against the full training set is unmeasured.
- Memorisation depends on the prefix, so simple prompts under-estimate it. None of the 273 Internet-conditioned extractions reproduces reliably from the original short prefix.
- One model family (GPT-2) with public training data, text only. Verification uses a fuzzy 3-gram match with false positives.
- The paper cannot say whether larger models of other families behave alike, and no mitigation is evaluated.

## See Also
- [[Deduplicating Training Data (ExactSubstr and NearDup)]] — extends (measures memorisation under deduplication)
- [[Pretraining Data Age, Quality and Toxicity Ablations]] — related
