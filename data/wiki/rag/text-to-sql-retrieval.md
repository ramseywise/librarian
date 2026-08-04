---
title: Text-to-SQL as a Retrieval Strategy
tags: [rag, llm, pattern]
summary: "Querying structured data as the second half of a hybrid retriever — dynamic schema subsetting, a semantic layer of retrieved few-shot SQL examples, mechanical validation that replaced a deleted LLM reviewer, and bounded error-as-context retry."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--reliable-agents.md
---

# Text-to-SQL as a Retrieval Strategy

RAG handles unstructured data. Queries requiring **precise filtering, aggregation, or
comparison** are better served by generating SQL against a structured store — *"give me 50
example studies done on rat"*, or retrieving numeric assay results by dosage group.

The framing that matters: Text-to-SQL is not an alternative to RAG, it is **the other
branch of one retriever**. A researcher agent holding both decides per query which
substrate can answer it, because the deciding factor is the shape of the question rather
than the domain. Documented from Bayer's PRINCE platform (built with Thoughtworks), where
the pairing is RAG over decades of preclinical PDF reports plus Text-to-SQL over study
metadata in Amazon Athena.

## The pipeline

| Step | What happens |
|---|---|
| **1. Intent recognition** | Analyze the natural-language query for the data points and filters requested |
| **2. Relevant schema selection** | Inject *only* the schema components the query needs into context |
| **3. Dynamic few-shot prompting** | Retrieve similar query/SQL pairs from a vector-indexed example collection |
| **4. Generation + validation** | Generate SQL; mechanically validate allowed operations |
| **5. Bounded execution** | Execute; cap the result set (50 records) |
| **6. Error-as-context retry** | On failure, feed the DB error back to the model; up to 3 attempts |

## Schema subsetting is retrieval

Step 2 is the step most implementations skip, and it is retrieval in its own right. For a
large schema, dumping every table definition into context both exceeds the budget and
degrades accuracy — the model has more candidate joins to get wrong. Selecting the
relevant subset **reduces complexity for the model and improves generated-SQL accuracy**
simultaneously.

This is the same relationship [[Why Context Is Finite]] describes generally: more context
is not monotonically better, because irrelevant context is a distractor and not merely
inert. A schema is just a document corpus with unusually rigid structure.

## The semantic layer of SQL examples

Step 3 is the most transferable idea here. Converting complex natural language into a
specific SQL dialect (Athena, in this case) is hard for LLMs, and the fix is **dynamic
few-shot prompting**: hand-picked query/SQL pairs covering various complex patterns are
stored in a separate vector-database collection — referred to as the *semantic layer* — and
retrieved by similarity against the incoming query, then injected as in-context examples.

Two properties make this stronger than static few-shot:

- **The examples are query-conditioned.** An aggregation query retrieves aggregation
  examples rather than the same generic three every time.
- **It improves by accretion.** New examples are added as challenging queries are
  encountered, so failures become permanent capability rather than a prompt rewrite. This
  is the [[Harness Engineering]] ratchet applied to a retrieval component.

Contrast with fine-tuning for dialect adherence: same objective, but the semantic layer is
editable, inspectable, and updatable per-example. See [[Few-Shot Prompting]] and
[[Reciprocal Rank Fusion (RRF)]] for the retrieval half.

## Mechanical validation, and the LLM reviewer that got deleted

Generated SQL is validated before execution: **only `SELECT` is permitted**; `DELETE`,
`INSERT`, and `UPDATE` are explicitly blocked. Certain essential columns (study ID, study
title) are always forced into the `SELECT` list so downstream synthesis can identify which
rows an answer came from.

The instructive part is what was removed. An earlier iteration ran an **LLM review step**
over generated SQL, and it was deleted:

> The reviewing LLM sometimes incorrectly flagged valid queries as erroneous, hindering
> efficiency without a commensurate gain in accuracy.

This is a clean case of a general principle — **a verifier is only worth its cost if its
error rate is meaningfully below the generator's.** An LLM reviewing LLM output brings
correlated failure modes and adds its own false positives, and false positives on a valid
query are expensive because they block correct work. The mechanical allowlist that replaced
it has a false-positive rate of zero on the property it checks.

The corollary is not "don't use LLM judges" — it is that the judge must be checking
something the mechanical check *can't*. Injection safety and destructive-operation blocking
are mechanically decidable; semantic query correctness is not, and is also where the
reviewer was unreliable. See [[Verification Loops]] and [[LLM-as-Judge Evaluation]].

## Bounded execution and error-as-context

Results are capped at **50 records per fetch** to prevent flooding the context window. The
retrieval succeeding is not the same as the retrieval being usable.

On failure — syntax error, schema mismatch, execution error — the **database's error
message** is fed back to the same model alongside the generated query and original
context, and a corrected query is generated. Bounded at **3 attempts** before reporting
failure.

The design property worth extracting: the database error is a **high-quality, free,
deterministic verification signal**. It is precise about what is wrong, costs nothing to
produce, and cannot be wrong about it — unlike an LLM judge, which is why the retry loop
survived while the review step didn't. Systems with a substrate that produces real errors
(SQL, compilers, type checkers, test suites) should route those errors back rather than
introducing a model to evaluate the output.

The 3-attempt bound is the other half. Without it, a genuinely unanswerable query loops
indefinitely; with it, exhaustion is itself a signal — either the query is unresolvable or
it is past the model's capability. See [[Agent Retry Taxonomy]] and
[[Loop Detection and the Two-Retry Rule]].

## Routing between RAG and SQL

The researcher agent decides which branch a query takes. As the surface expands across
domains, PRINCE evolved this into a **hierarchy of domain sub-agents** — each owning its
own toolset (toxicology RAG + tox metadata SQL; pharmacology RAG + assay-level SQL) and
prompt instructions encoding that domain's data model, authoritative tables, and concept
interpretations.

The driver was ambiguity that a flat tool list cannot resolve. Many tools operate on
similar concepts — *studies*, *findings*, *assays* — pointing at different datasets with
different schemas. When a user says "the study," the referent depends on the domain. A
single agent with overlapping tools and subtly different data contracts cannot
disambiguate, so **the disambiguation moves into the routing layer** where a domain choice
resolves it once. This is the tool-count anti-pattern in
[[Agent Deployment Anti-Patterns]] and the functional cut in
[[Task Decomposition Patterns]], reached from production pressure.

## See Also
- [[RAG Knowledge Preparation]] <!-- auto-linked -->
- [[RL for Retrieval Policies]] <!-- auto-linked -->
- [[RAG Retrieval Strategies]] — complements (the unstructured branch of the same retriever)
- [[Context Retrieval Strategies]] — complements (schema subsetting as context assembly)
- [[Verification Loops]] — implements (mechanical validation replacing an LLM reviewer)
- [[Agent Retry Taxonomy]] — implements (bounded error-as-context retry)
- [[Few-Shot Prompting]] — depends-on (the semantic layer's mechanism)
- [[Agent Deployment Anti-Patterns]] — complements (tool-count pressure driving the domain split)
