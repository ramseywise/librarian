---
title: AIE Code-Test Flaw Taxonomy
tags: [interview, llm, reference]
summary: The eleven recurring defects in LLM take-home submissions — context overflow, naive chunking, missing retry/timeout, ungrounded generation, JSON drift, swallowed exceptions — each with its detection cue and the minimal fix that fits inside a one-hour timebox.
updated: 2026-08-04
sources:
  - data/raw/claude-docs/learn-ai-engineering/docs/research/2026-08-01_code-test_format-and-flaws.md
---

# AIE Code-Test Flaw Taxonomy

Analysis of 100+ real take-home repos and 1,765 job descriptions produced a stable list of
defects that recur across LLM-engineering submissions. What makes the list useful is not
the defects themselves but the third column: each has a **detection cue** — a mechanical
check performable on someone else's code in seconds — and a fix sized to fit a timebox
that is already mostly spent.

The prompt shape these appear under is consistent: *"here's a CSV / doc corpus / API spec,
build a system to retrieve/classify/extract, show me a working script, and in your README
explain one thing that could break and how you'd fix it."* Not *design* a solution — **ship**
one. Deliverable is a running script plus a README, not a notebook.

## The defects

| Flaw | Detection cue | Minimal fix |
|---|---|---|
| **Context window overflow** | Query that requires the 5th chunk — model ignores it or hallucinates | Compute `available = context_window − system_prompt − max_history − 20% margin` before retrieval; `assert available >= 2000` |
| **Naive fixed-size chunking** | Inspect first 3 chunks for mid-sentence breaks | 50-token overlap (`range(0, len(text), 462)`). *Not* semantic chunking — that's over budget |
| **No retry + backoff** | Does the code catch `RateLimitError`? Does it sleep? | 3-line `for attempt in range(3)` with `sleep(2**attempt)`, or `tenacity` |
| **No timeout on LLM calls** | Search for `timeout` — zero instances means missing | `timeout=30` on the call |
| **Silent hallucination** | Retrieval + LLM call with no grounding assertion | If no cited chunk id appears in the answer, return *"I couldn't find an answer in the documents."* |
| **Unvalidated structured output** | `json.loads()` without try/except; schema described vaguely | JSON mode, or enumerate values in the prompt (`score ∈ {low, medium, high}` — no floats) |
| **Silent exception swallowing** | Bare `except:` followed by `pass` | `except SpecificError as e: log_error(e); raise` |
| **No cost/latency instrumentation** | No print or logger reporting elapsed time, tokens, or cost | Three lines: elapsed, token estimate, dollar estimate |
| **Off-by-one in chunk overlap** | Long doc with known boundaries; measure actual overlap | `assert all(len(c) >= min_chunk_size for c in chunks[:-1])` |
| **Embedding ↔ retrieval mismatch** | Is the embedding model identical at index-build and query time? | One constant used for both. Switching models means re-embedding |
| **No README "what breaks" section** | Does the README acknowledge trade-offs or assume perfection? | Three named breakages, each with its fix |

Four of these — retry, timeout, grounding, JSON validation — are the same API-safety
concerns that [[Safeguards Architecture — Five Protection Layers]] formalises as runtime
layers. The take-home is asking for a hand-rolled subset of that pipeline under time
pressure, which is why the taxonomy reads as a compressed version of production hardening.

## The fixes are cheap, which is the point

Priced individually and summed:

```
context budget assertion   1 min
timeout on LLM calls       1 min
retry logic                3 min
JSON validation            3 min
overlap + min-chunk test   5 min
cost/latency print         3 min
README "what breaks"       5 min
                        ──────
                          ~23 min  (leaves 37 min for core functionality)
```

The whole hardening pass costs roughly a third of a one-hour budget. That pricing is the
argument: these are not omitted because they are expensive, they are omitted because the
candidate never budgeted a hardening phase at all.

## Observed failure rates

| Failure | % of candidates | What it signals |
|---|---|---|
| No grounding check | ~30% | Didn't reason about hallucination — the AIE-specific risk |
| No README / "what breaks" | ~25% | Doesn't signal judgment or maturity |
| Context window overflow | ~20% | Doesn't do token budgeting |
| No timeout | ~15% | Hobby code, not production code |
| JSON validation missing | ~15% | Trusts the model too much |
| Silent exception swallowing | ~10% | Didn't test error paths |

The top two are both *judgment* failures rather than implementation failures — nothing in
either requires skill the candidate lacks.

## Pragmatism is a proxy for finishing

The graded signal is not sophistication. It runs the other way:

| Signal | What it shows |
|---|---|
| One embedding model, not three | Understands token cost and latency |
| Off-the-shelf retrieval, not a custom ranker | Knows when to buy vs. build |
| Chunk size stated **with a one-line justification** | Thought about it; didn't copy a tutorial |
| One round of retrieval, not multi-hop | Isn't solving a problem that doesn't exist yet |
| Cost or latency printout | Thinking like an infra engineer |

The published rubrics (Meta: problem-solving 35–40%, code quality 25–30%, verification
15–20%, communication 10–15%; Google: correctness + efficiency + clarity + edge cases)
weight correctness above all, and pragmatism appears nowhere as a band. The research
resolves this by noting what pragmatism *causes*:

> In a 60-min timebox, it's a proxy for **finishing** — if you over-engineer, you won't
> ship. Graders see finished code; incomplete elegant code doesn't score.

So the observed behaviour of strong candidates in the final twenty minutes is not polish
or refactoring but: one manual inspection of retrieval quality, a README with an explicit
cost/latency trade-off, instrumentation, a grounding check, a timeout. Explicitly **not**:
multi-turn conversation, a web UI, prompt tuning, a test suite, caching.

Note the tension there — "not a test suite" is correct advice *at the one-hour grain only*,
and inverts as the window widens; see [[Timebox-Scaled Deliverable Bar]].

## When AI tools are permitted

Policy varies and is not inferable: permitted at Meta and Google pilots, restricted at
Anthropic (*"submit unaided unless told otherwise"*), unstated elsewhere. Where permitted,
the weighting shifts from implementation toward problem decomposition, prompt quality, and
output verification.

The anti-patterns are all one failure wearing different clothes — shipping generated code
you have not read:

- Paste a generated pipeline without examining it (graders can tell; *"you don't know what
  your code does"*)
- Accept a hallucinated API without testing it — submission is simply broken
- Prompt vaguely (*"build a RAG system"*), producing a generic solution to a different
  problem than the one asked
- Let the README claim OpenAI while the code calls Anthropic

And the conclusion is not about detection:

> It's not about *detecting* AI use (it's allowed). It's about **verifying
> understanding.** If your AI-generated code breaks and you can't fix it, you fail.

The strong version is division of labour: generated boilerplate for loading and parsing,
hand-owned system design and safety logic, with the README stating plainly which was which.

## Format status

The 1-hour *timed* variant is emerging rather than canonical. Most real assessments are
either live 45–60 min with an interviewer present or async 2–4 hours. Direct evidence for
solo 1-hour timed take-homes at major AIE companies was sought and not found — LangChain
runs open-ended "build a feature on our codebase," Anthropic a 3–6h async assignment plus
debrief. Treat the one-hour framing as a drill, not a prediction of the round you'll get.

## See Also
- [[Timebox-Scaled Deliverable Bar]] — extends (how these expectations scale with the window)
- [[Safeguards Architecture — Five Protection Layers]] — complements (the production form of the same four API-safety fixes)
- [[System Design Interview Study Guide]] — alternative-to (design round vs. shipping round)
- [[RAG Interview Study Guide]] — prerequisite-for (the domain knowledge the defects assume)
- [[CRAG Retry Logic]] — instance-of (the grounding/retry check done properly)
