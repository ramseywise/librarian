---
title: WikiSQL and Seq2SQL
tags: [eval, code, benchmark]
summary: "WikiSQL is 80,654 hand-annotated question, SQL and table examples over 24,241 tables; Seq2SQL, which trains the WHERE clause with REINFORCE on an execution reward, reached 59.4% execution accuracy on the test split, 2.3 points above its no-RL variant (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-zhong-2017-seq2sql.md
---

# WikiSQL and Seq2SQL

Zhong, Xiong and Socher ask whether natural-language questions can be translated to SQL over unseen table schemas by using SQL structure and execution-based reinforcement learning. Their hypothesis: the WHERE conditions have no fixed order, so cross entropy unfairly punishes queries that are equivalent, and policy gradient on execution correctness should avoid that.

## The dataset

WikiSQL has 80,654 hand-annotated examples over 24,241 tables, about ten times the size of comparable sets (Geoquery 880, ATIS 5,871, Overnight 26,098, WikiTableQuestions 22,033). The release includes a query execution engine.

## The model

Seq2SQL has three parts: an aggregation classifier, a pointer over the SELECT column, and a pointer decoder for the WHERE clause. The first two use cross entropy. The WHERE decoder is trained first with teacher forcing and then with REINFORCE, with the reward from executing the generated query:

- -2 if the query is not valid SQL;
- -1 if it is valid but executes to an incorrect result;
- +1 if it executes to the correct result.

Two baselines are used: a seq2seq model after Dong and Lapata, and an augmented pointer network.

## Metrics

**Execution accuracy** counts queries whose execution gives the right result. **Logical form accuracy** counts queries that match the ground-truth SQL string exactly.

## Results (self-reported)

Setup: WikiSQL, single runs.

- Seq2SQL: 59.4% execution accuracy and 48.3% logical form accuracy on test; 60.8% and 49.5% on dev.
- Augmented pointer network: 53.3% test execution accuracy. Seq2SQL without RL (teacher-forced WHERE): 57.1%, so RL adds 2.3 points.
- Invalid queries drop from 7.9% to 4.8% thanks to the SQL structure (no-RL Seq2SQL against the augmented pointer network; split not stated), and the aggregation classifier lifts COUNT F1 (65.4 up to 69.2).

## Limits

- Execution accuracy may reward a wrong query that happens to return the right result, while logical form accuracy marks down a correct query whose conditions are in a different order.
- Coverage is limited to one table, one aggregation, one SELECT column and conditions joined by AND, and only the operators =, > and < are generated.
- Each model was run once, with no seeds, variance or significance tests, and the learning rate, batch size and RL epoch count are missing.
- The model sees column names and the question, not table content.
- The questions paraphrase template-generated ones and so may vary less than real user questions (an inference in the extraction, not something the authors concede).

## See Also
- [[Spider Text-to-SQL Benchmark]] — alternative-to
- [[CodeRL Unit-Test Actor-Critic]] — related (execution-based reward for code)
- [[WEBQUESTIONS and Semantic Parsing on Freebase]] — related
