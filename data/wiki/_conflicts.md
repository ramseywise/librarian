---
title: Conflicts
tags: [index, conflict]
summary: Flagged contradictions between sources. Each entry needs human review before resolution.
updated: 2026-07-14
---

# Conflicts

> Unresolved contradictions between sources. Do not delete entries — mark as `Resolved` with a note.
> See `CLAUDE.md` for the conflict handling protocol.

---

## Open Conflicts

## Conflict: CRAG Confidence Threshold — 2026-04-25

**Claim A** (from [[LangGraph CRAG Pipeline]], sourced from `raw/playground-docs/librarian-stack-audit.md`):
> `confidence_threshold` default is **0.3** — `confidence_score >= 0.3` → generate; below → retry

**Claim B** (from `raw/agent-skills/langchain-rag/references/rag-strategies.md`):
> Haiku grades each chunk; **score ≥ 0.5** = relevant. `retry_count` cap = 1 in prod.

**Claim C** (from `raw/agent-skills/advanced-rag-patterns/SKILL.md`):
> CRAG threshold: **grade ≥ 0.7** → generate. Below → reformulate and re-retrieve (max 2 retries).

**Status:** Unresolved — needs human review
**Impact:** Librarian CRAG gate config; the correct `confidence_threshold` value for production.
Note: Claims B and C may refer to a different grader (chunk-level relevance score) vs. Claim A (reranker-level confidence score). These could be measuring different things at different pipeline stages.

---

## Conflict: SANYI Violation-Code Meanings and Severities — 2026-07-14

**Claim A** (from [[SANYI Change-Contract System]], sourced from `raw/claude-docs/project-g/skills/SANYI/SKILL.md` and `README.md`, ingested 2026-07-05):
> BY-1 = "Tunable hardcoded in source" (Medium severity); BY-2 = "Prompt embedded in code" (Medium); BY-3 = "Feature flag not exposed as env var" (Low); BY-4 = "Dead config entry" (Low); JY-1 = "Schema entropy growth" (Medium); JY-2 = "Graph topology change without contract update" (High); JY-3 = "Tool signature drift" (High); BN-1 = "Invariant moved to prompt/config" (Critical).

**Claim B** (from `raw/claude-docs/project-g/skills/SANYI/references/violations.md`, which states of itself: "Codes and severities here are authoritative; SKILL.md and README.md mirror them"):
> BY-1 = "Direct modification of Buyi-guarded code" (blocker); BY-2 = "Semantic downgrade: Buyi invariant made bypassable via flag/config/env" (blocker); BY-3 = "Buyi evidence test deleted or weakened" (blocker); BY-4 = "Declared Buyi invariant has prompt-only implementation" (blocker); JY-1 = "Jianyi budget exceeded" (warning); JY-2 = "Anomalous single-PR growth" (warning); JY-3 = "Unbounded escape hatch" (warning); BN-1 = "Bianyi value hardcoded outside declared layer" (info).

**Status:** Resolved — 2026-07-17
**Resolution:** Claim B is correct. The live SANYI skill copies (librarian, playground, ai-project-template — verified functionally identical, whitespace-only diffs) all carry Claim B's taxonomy in their current `SKILL.md` (BY-1 = "Buyi path edited directly"), confirming the 2026-07-05 ingest captured a pre-reconciliation draft that was later corrected upstream. Updated [[SANYI Change-Contract System]] to Claim B's table; Claim A stays on record here as the historical ingest snapshot.
**Impact (historical):** The two sources assigned **different meanings to the same codes** — e.g. Claim A's BY-1 ("hardcoded tunable") is Claim B's BN-1, while Claim B's BY-1 ("direct modification of Buyi-guarded code") had no equivalent in Claim A.

**Related sub-conflict — SANYI.md file structure:** Resolved the same way, 2026-07-17. `contract-spec.md`'s six exact-match sections (`## 不易 Buyi`, `## 简易 Jianyi`, `## 变易 Bianyi`, `## Migrations`, `## Pending`, `## Debt`, with per-entry fields `paths`/`contract`/`evidence`/`budget`/`current`) are what the live skill parses; the wiki page's "SANYI.md Format" section already reflected them and is now marked authoritative. Claim A's section names (`## Components`, `## Buyi Enforcement`, …) were the same pre-reconciliation draft.

---

## Conflict: Test Coverage in a Code-Test Submission — 2026-08-03

**Claim A** (from [[AIE Code-Test Flaw Taxonomy]], sourced from `data/raw/claude-docs/learn-ai-engineering/docs/research/2026-08-01_code-test_format-and-flaws.md`):
> What strong candidates actually do in the last 20 min … **NOT:** implement multi-turn conversation, add a web UI, tune the prompt template, **write a test suite**, implement a custom embedding model, add caching.

**Claim B** (from new source `data/raw/claude-docs/learn-ai-engineering/docs/research/2026-08-01_code-test_openai-work-trial.md`):
> Even in a 1-hour timed test, include 2–3 tests: happy path, boundary, failure/error path — runnable with one command. Missing tests is (per this source) the single most cited rejection reason.

**Status:** Resolved — 2026-08-04
**Resolution:** Both hold, scoped by window, with A's evidence weighted higher where they overlap. A's "don't spend the last 20 minutes writing tests" is correct for the **1-hour timed** round: it is multi-source (Grigorev dataset, published Meta/Google rubrics), and those rubrics weight correctness > code quality > communication with no testing band at all. B's dial is correct for **1–6h async** submissions graded as pull requests, where the deliverable is reviewed like a PR and test presence is legible. Where B overlaps A — its claim that tests are needed *"even in a 1-hour timed test"* — B is recorded with attribution rather than asserted: it is vendor-published, single-source, and functions as content marketing for mock-interview services, and its "single most cited rejection reason" superlative is uncorroborated. [[Timebox-Scaled Deliverable Bar]] already carries that confidence note inline; no page edit was required beyond dropping the `conflict` tags.
**Impact:** Which behaviour the code-test prep material tells a candidate to spend the final 20 minutes on. The two files are sibling research docs in the same LAE folder, and B is explicitly framed as a correction to A.

**Note on the resolution:** [[Timebox-Scaled Deliverable Bar]] proposes that both are right at different windows — A's advice was derived from a 1-hour timed budget where the ~23-minute hardening pass already consumes the tail, while B addresses 1–6h async submissions graded as pull requests. But B asserts its floor *"even in a 1-hour timed test,"* which is a direct overlap, so the disagreement is real at that window and not fully dissolved by the dial. Confidence also differs: A is multi-source (Grigorev dataset, published Meta/Google rubrics); B is vendor-published single-source content marketing whose "most cited rejection reason" claim is uncorroborated. A secondary tension: B treats testing as a named grading band, while the Meta and Google rubrics quoted in A weight correctness > code quality > communication and name no testing band at all.

---

## Conflict: Should Guardrails Themselves Use an LLM? — 2026-08-04

**Claim A** (from [[Input Guardrails Pipeline]], sourced from `raw/claude-docs/playground/docs/research/agentic-ai/guardrails-pipeline.md`):
> Guardrails must be **deterministic and LLM-free**. They run before any LLM call. An LLM-based guardrail can be bypassed by the same injection techniques it is defending against.

**Claim B** (from [[Prompt Injection]], sourced from `data/raw/repos/learn-ai-engineering/interviewing--notes--prompt-injection.md`, OWASP LLM Prompt Injection Prevention Cheat Sheet):
> A separate model can act as a filter on inputs and outputs of the primary LLM ("LLM-as-judge" / "guardrail model"), at three placements: input screening, output screening, action screening. Explicitly positioned *"alongside the deterministic controls described above, not in place of them."* Concedes the guardrail is itself injectable, and adds that it should have a **different attack surface** than the primary model — a purpose-trained classifier (Llama Guard, ShieldGemma, Granite Guardian, Prompt Guard) rather than a chat model from the same family.

**Status:** Unresolved — needs human review
**Impact:** Whether librarian's own guardrail guidance permits a model-based screening layer, and whether [[Input Guardrails Pipeline]]'s stage list should gain an optional LLM stage for indirect-injection detection on retrieved/fetched content.

**Note on the likely resolution:** The two may not fully contradict. A's "LLM-free" is stated as a property of *the pipeline* — the deterministic pre-LLM path — while B positions the guardrail model as an *additional* layer that does not replace any of A's stages. The genuine disagreement is narrower: A treats LLM-based screening as actively unsafe (bypassable by the same technique), B treats it as net-positive because a purpose-trained classifier has a different attack surface and catches indirect injection in untrusted content that regex provably misses. That last point is the strongest argument against A's absolutism — A's stage 4 is pure pattern matching, which OWASP states does not reliably catch indirect injection. Cost/latency is the practical dial: reserve model-based checks for high-risk paths (tool invocation, ingestion of external content), keep deterministic checks on routine traffic.

---

## Conflict: Who writes SUPERSEDED on a plan doc — 2026-10-16

**Claim A** (from `[[Plan-Doc Status Enum]]`, sourced from the GUA-73 status-enum spec):
> The transition table lists `SUPERSEDED` ("replaced by another doc; off-path") with writer "manual".

**Claim B** (from new sources `data/raw/claude-docs/galactus/skills/proto-plan/SKILL.md` and `data/raw/claude-docs/galactus/skills/proto-refine/SKILL.md`):
> `/proto-plan` writes `Status: SUPERSEDED` + `Superseded-by:` on the third arrival of the `EXECUTED → PLANNED` loop-back (bound 2); `/proto-refine` writes it on a NEEDS-SPLIT verdict, naming the split docs.

**Status:** Unresolved — needs human review
**Impact:** Plan-doc status hook and Capability vs Phase Skills (which skills may advance Status:); likely a later galactus evolution of the guacamayo spec rather than an error.

---

## Conflict: PyMC find_MAP availability — 2026-10-16

**Claim A** (from `[[Notebook Dependency Staleness]]`, sourced from `data/raw/repos/learn-ai-engineering/data-science--CURRICULUM.md`):
> `pm.sample(draws, init='MAP')` migrates to `pm.sample(draws)`, or `initvals=pm.find_MAP()`. This implies `pm.find_MAP()` still exists in PyMC 5.

**Claim B** (from new source `data/raw/claude-docs/learn-ai-engineering/docs/research/2026-07-22_pymc_migration.md`):
> Lists `pm.find_MAP()` under "API Removal" ("MAP inference replaced with variational inference; alternative: use `pm.sample()` or scipy") and recommends removing its calls. The source caveats its own API claims as needing verification.

**Status:** Unresolved — needs human review
**Impact:** Notebook Dependency Staleness PyMC table; whether the two "Medium" Bayesian notebooks need a rewrite or only a mechanical port.

---

## Conflict: arXiv API rate limit — 2026-10-17

**Claim A** (from `[[Automated Paper Discovery Pipeline]]`, sourced from `data/raw/claude-docs/learn-ai-engineering/docs/research/2026-07-22_paper_discovery.md`):
> arXiv API: "~30 req/s soft limit with backoff".

**Claim B** (from new source `data/raw/claude-docs/learn-ai-engineering/docs/plans/2026-07-25-LAE-30-34-learning-depth.md`):
> "the API allows 1 request per 3 seconds for automated access" — plan adds `time.sleep(3)` between category requests and recommends bulk export pagination.

**Status:** Unresolved — needs human review
**Impact:** Automated Paper Discovery Pipeline fetch design; how a multi-category weekly fetch must be paced.

---

## Conflict: learn-ai-engineering packed history size — 2026-10-17

**Claim A** (from `[[Repo Weight Triage — GC Before LFS]]`, sourced from `data/raw/claude-docs/learn-ai-engineering/docs/research/2026-07-29_LAE-106_vendored-repos-readings.md`):
> Packed history (`size-pack`) 395M, with ~1.1G of loose objects reclaimable by `git gc`; `filter-repo` "not worth it at 395M".

**Claim B** (from new source `data/raw/claude-docs/learn-ai-engineering/docs/plans/2026-08-14-LAE-106-consolidate-vendored-course-repos.md`):
> `size-pack` is 1.42 GiB (baseline verified 2026-08-14); "every blob survives in history"; `filter-repo` is "the only thing that reclaims 1.42 GiB".

**Status:** Unresolved — needs human review (measurements two weeks apart; the sources do not say whether a gc packed the loose objects in between or whether history grew)
**Impact:** Repo Weight Triage cost framing of history rewrite — whether eviction is "not worth it" or the main remaining lever.

---

## Conflict: learn-ai-engineering wave ordering — 2026-10-17

**Claim A** (from `[[AI Engineering Curriculum Structure]]`, sourced from `data/raw/claude-docs/learn-ai-engineering/docs/research/2026-07-21_curriculum-architecture_meta.md` and the generative-ai READMEs):
> The discipline wave presumes the application wave, so "the corpus tells you to learn the gen-AI pillars first and layer engineering practice on top".

**Claim B** (from new source `data/raw/repos/learn-ai-engineering/CURRICULUM.md`):
> Path A orders LLM fundamentals (gen-AI pillar 01) → ai-engineering pillars 01–06 → gen-AI pillars 02–07, because "after the ai-engineering discipline, the code patterns will make sense structurally".

**Status:** Unresolved — needs human review (both agree pillar 01 comes first; they disagree on whether gen-AI 02–07 precede or follow the discipline wave)
**Impact:** AI Engineering Curriculum Structure ordering claim and its "how do I do X / why does X break" retrieval heuristic.

---

## Conflict: Rater burden of the κ_HH ceiling study — 2026-10-17

**Claim A** (from `[[Human Agreement Ceiling Protocol]]`, sourced from `data/raw/claude-docs/akira/docs/research/2026-08-27-b15-kappa-protocol.md` and `data/raw/claude-docs/akira/docs/open-questions.md`):
> The ceiling study is "the highest information-per-euro item available: ~33 rater-hours, no pipeline, no traffic."

**Claim B** (from new source `data/raw/claude-docs/akira/docs/plans/2026-08-27-b15-kappa-protocol.md`):
> "~33 rater-hours" is "a legacy figure from a 2-rater partial-overlap design that this plan does not use"; at full overlap the honest totals are 48 h (3 raters), 64 h (4), 80 h (5, target) — "under-quoting the burden by 2.4×".

**Status:** Unresolved — needs human review (the page's intro still quotes ~33 h; the new "Running the study" section records ~80 h)
**Impact:** Information-per-euro ranking of the ceiling study; any budget or recruiting brief quoting the burden.

---

## Conflict: Drop vs harden an unread database view — 2026-10-17

**Claim A** (from `[[Artifact Is Not Evidence: Push and Probe]]`, sourced from `data/raw/claude-docs/akira/docs/research/2026-09-03-rls-closure.md`):
> "Drop an unread surface rather than secure it" — a view no code read should be removed; removing it is the smaller, more honest change.

**Claim B** (from new source `data/raw/claude-docs/akira/docs/plans/2026-09-03-dis118-rls-closure.md`, Open Question 2, resolved by the project owner):
> Keep the view and set `security_invoker = true`; do not drop it. "No reader in this codebase" cannot rule out dashboard queries, saved SQL, BI cards or partner integrations, and a DROP is unrecoverable for them while the flag closes the same exposure reversibly.

**Status:** Unresolved — needs human review (Claim B is the later, executed decision for this instance; whether the general rule should change from "drop" to "harden when consumers are unknowable" is the open question)
**Impact:** RLS-closure guidance in [[Artifact Is Not Evidence: Push and Probe]] and [[Written-but-Inert RLS Policies]].

---

## Ingest Errors

*Sources that failed to parse during ingest.*

---

## Resolved Conflicts

*Conflicts that have been reviewed and resolved.*

## Conflict: Rate-limiter fail posture on the email-link route — 2026-10-17

**Claim A** (from `[[Rate-Limit Keying: Identity Over IP]]`, sourced from `data/raw/claude-docs/akira/docs/research/2026-09-03-dis43-anonymous-rate-limiting.md`):
> Fail-open vs fail-closed is per route: fail open for live poll votes, but for an unauthenticated route that sends email and creates accounts, fail closed.

**Claim B** (from new source `data/raw/claude-docs/akira/docs/plans/2026-09-06-dis197b-sink-hardening.md`):
> The same research doc's §7 "converges on" fail-open; the plan applies fail-open uniformly to all gated routes, including `/api/polls/[id]/email-link`, and addresses account creation separately by setting `shouldCreateUser: false`.

**Additional evidence** (from `data/raw/claude-docs/akira/docs/plans/2026-09-29-dis325-ratelimit-shared-store.md`, added 2026-10-17):
> A later plan describes the shipped limiter as failing open everywhere (consistent with Claim B as built) and recommends that the IP-keyed routes and the mail sender fail closed on a store outage, which matches Claim A's per-route posture as the target.

**Status:** Unresolved — needs human review
**Impact:** Email-link route abuse posture; whether the limiter's store-error path should differ per route. (Related tension: the 2026-09-03 plan's first cut rejected a DB-backed limiter, while the 2026-09-06 plan proposes a Postgres counter table — escalated there as an open question, not decided.)

## Conflict: Was Dependabot auto-merge ungated, and do CI callers pin @v1? — 2026-10-17

**Claim A** (from `[[AI Project Template Scaffold]]`, sourced from `raw/sessions/claude-2026-07-19-none-of-my-cicd-pipelines-run-we-need-to-d7cdbb90.md` / the 2026-07-19 CI/CD standardization plan):
> "Dependabot auto-merge was ungated: it merged without waiting on required checks." … "Callers pin `@v1`, not `@main`."

**Claim B** (from new source `data/raw/claude-docs/ai-project-template/docs/plans/AIT-22-research.md`, verified live via `gh api` 2026-07-28):
> Branch protection already requires the CI check on all 4 production repos, and `gh pr merge --auto` honors it regardless of `needs:` — "auto-merge is not actually ungated for Dependabot PRs on the 3 repos that have `ci.yml`." The downstream callers reference the reusable workflow as `python-ci.yml@main`.

**Status:** Unresolved — needs human review (possibly both true at different times: ungated before branch protection was set, and `@v1` as the intended convention vs `@main` as practice)
**Impact:** The CI/CD standardization section of [[AI Project Template Scaffold]]; [[Gate Dependabot Auto-Merge on Branch Protection]].

## Conflict: Resident-leaning filter — default-deny vs fail-open — 2026-10-17

**Claim A** (from `[[Every Column Names Its Reader]]` § "A Graded Vocabulary With No Cutover Has No Reader", sourced from `data/raw/claude-docs/akira/docs/research/2026-09-21-dis340-audience-attribute.md`):
> The audience attribute is a default-deny, off-by-default hard-filter flag: unknown never passes the filter.

**Claim B** (from new source `data/raw/claude-docs/akira/docs/plans/2026-09-21-dis340-audience-attribute.md`, operator decision in refine pass 2):
> The filter fails OPEN until the backfill runs: only an explicit `'true'` excludes; `null`/`undefined`/`'unknown'` are all served, so the unconditional B2B flag is a no-op on merge day instead of emptying the candidate pool.

**Status:** Unresolved — needs human review (likely Claim B supersedes A as the later, executed decision; A may still describe the intended end state once the backfill is complete)
**Impact:** [[Every Column Names Its Reader]] audience-attribute sections; any future exclusion-style hard filter added over an unpopulated column.

## Conflict: Natural-key merge refresh vs re-crawl never overwrites — 2026-10-17

**Claim A** (from `[[Re-Crawl Adds, Never Overwrites]]`, sourced from `data/raw/claude-docs/akira/docs/plans/2026-09-14-dis264-enrichment-input-shaping.md`):
> Once a content row exists, nothing in the importer issues a content UPDATE. A natural-key sibling with a different description is counted and withheld, not written.

**Claim B** (from new source `data/raw/claude-docs/akira/docs/plans/2026-09-16-dis295-event-edition-identity.md`, see `[[Coalesce Against a Never-Null Source]]`):
> On a natural-key match, the merge refreshes the parent's descriptive fields (coalesced, rank-ruled for provenance) while `review_status` is still `draft` or `needs_review`.

The dis264 plan itself lists this decision against the never-overwrite rule as an open tension. The two may only overlap for rows still in review.

**Status:** Unresolved — needs human review
**Impact:** Importer write path for existing rows; content_hash baselines and re-enrichment skip gates.

## Conflict: Does RRF protect a rank-1 exact-name lexical hit? — 2026-10-17

**Claim A** (from `[[Reciprocal Rank Fusion (RRF)]]`, sourced from `data/raw/claude-docs/akira/docs/research/2026-09-24-dis386-semantic-retrieval.md`):
> A rank-1 exact-name lexical hit (`1/(k+1)`) outweighs a mediocre semantic rank, which protects name matching.

**Claim B** (from new source `data/raw/claude-docs/akira/docs/plans/2026-09-25-dis386-lexical-rrf.md`, execution log):
> At `k=60` an id appearing in both lists at rank `r < 62` scores `2/(60+r)` and beats a single-list rank-1 hit (`1/61`); with two 2-item lists the double-appearance case numerically wins. The test asserts the real arithmetic, documented inline so it is not "fixed" to match intuition.

**Status:** Unresolved — needs human review
**Impact:** The name-matching guarantee of hybrid (lexical + semantic) retrieval; whether exact-name hits need a separate boost or pin outside RRF before the arm is flipped on.

## Conflict: Which ML frame has a stated label horizon? — 2026-10-17

**Claim A** (from `[[ML Frame Sourcing — License, Horizon, Prevalence]]`, sourced from `data/raw/claude-docs/galactus/docs/DESIGN-ml-frame-sourcing.md` and `data/raw/claude-docs/galactus/docs/decisions/ml-frame-sourcing-decisions.md`):
> Constraint 2 is a time column supporting a temporal split. The fraud set's `Time` column (seconds since first transaction) is enough; the credit set has none, which is recorded as a limitation.

**Claim B** (from new source `data/raw/claude-docs/galactus/docs/plans/2026-08-18-ml-frame-sourcing.md`, see `[[Label Horizon vs Sampling Window]]`):
> The constraint is a *source-stated label horizon*. The credit frame's horizon ("default payment next month") is confirmed in the curated variables table. The fraud frame has no stated label horizon: `Time` fixes only the ~2-day sampling window, and under "inferred horizon = unavailable" the frame fails. The fraud licence (ODbL) is also unverified.

The two sources may be using "horizon" to mean different things (a temporal-split column vs. a label-observation window). The later plan scoped execution to credit only and left fraud to an operator decision.

**Status:** Unresolved — needs human review
**Impact:** Fraud-run frame choice and its "3/3 frames with stated horizon" evaluation target; whether the credit run's lack of a time column still counts as a recorded limitation.

## Conflict: Is LangChain the layer beneath LangGraph, or built on top of it? — 2026-10-17

**Claim A** (from `[[Framework Selection — LangChain vs LangGraph vs Deep Agents]]` and `[[LangChain Fundamentals — create_agent, Tools, Structured Output]]`, sourced from `raw/agent-skills/framework-selection/SKILL.md`):
> LangChain is the foundation layer (models, tools, chains); LangGraph sits on top of it, and Deep Agents on top of LangGraph.

**Claim B** (from new source `data/raw/repos/learn-ai-engineering/ai-engineering--04-loop--deep-agents.md`, a copy of the upstream "Frameworks, runtimes, and harnesses" docs):
> Agent frameworks are generally higher level and run on agent runtimes — LangChain 1.0 is built on top of LangGraph; you don't need to know LangGraph to use LangChain.

Possibly both partly right: the integration packages (models, tools) are a dependency of everything, while the `create_agent` loop executes on the LangGraph runtime.

**Status:** Unresolved — needs human review
**Impact:** The layer diagram in Framework Selection and the "foundation layer" summary of LangChain Fundamentals; how the stack is explained when choosing a framework.

## Conflict: Does the golden-hash test enforce a PROMPT_VERSION bump? — 2026-10-17

**Claim A** (from `[[Offline Prompt Experiment Runner]]` and `[[Frozen Version Stamps on Logged Results]]`, sourced from `data/raw/claude-docs/akira/docs/plans/2026-09-15-dis272-enrichment-prompt-experiments.md`):
> A golden-hash test pins the per-vertical hashes, so prompt drift without a version bump fails CI.

**Claim B** (from new source `data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis272-prompt-identity-phase1.md`, finding SG-001):
> The test pins the three template hashes and the `PROMPT_VERSION` literal. A developer who edits the prompt can re-pin only the hash literals and pass, leaving `PROMPT_VERSION` stale. No test can inspect intent, so the comment was corrected: the test makes the bump a visible review obligation, not an enforced one; `prompt_hash` stays truthful either way.

**Status:** Unresolved — needs human review (likely Claim B, the later review of the built code, supersedes the plan's intent)
**Impact:** Whether `prompt_version` can be trusted as an experiment/analysis axis without cross-checking `prompt_hash`; the two eval pages' description of the backstop.

## Conflict: Cross-sweep finding fingerprint formula, design vs as built — 2026-10-17

**Claim A** (from `[[Cross-Sweep Finding Fingerprint]]`, sourced from `data/raw/claude-docs/guacamayo/docs/research/2026-07-27-cross-repo-intelligence.md`):
> `FindingFingerprint = sha256(file + symbol_scope + category + normalized_title)[:12]`. `symbol_scope` pins a location that survives line-number churn.

**Claim B** (from new source `data/raw/repos/nonprofit-success-ai/.claude--docs--research--2026-08-18_dssg-second-brain_codemap-review.md`, a code review of guacamayo `review/fingerprint.py`):
> `_digest` keys on `f"{file_path}|{start_line}|{category}|{reporter}|{title}"` (sha256). There is no repo or user component.

The as-built key uses `start_line` (line churn changes the fingerprint) and adds `reporter`. Either the design was never implemented as written, or the implementation drifted.

**Status:** Unresolved — needs human review
**Impact:** Whether the trend states (persistent/recurring/resolved) survive line-number shifts. The page's claim that fingerprints survive line churn may not hold for the shipped code.

## Conflict: Is DeepEval part of listen-wiseer's eval harness? — 2026-10-17

**Claim A** (from `[[Listen-Wiseer Project]]`, Tech Decisions table and eval harness layout, sourced from earlier playground/plan docs):
> Eval framework is LangFuse + RAGAS + DeepEval; DeepEval's `ToolCorrectnessMetric` fills the agent eval gap, and Tier 3 graders are "RAGAS + DeepEval".

**Claim B** (from new source `data/raw/repos/listen-wiseer/CLAUDE.md`, high-confidence repo doc):
> `deepeval` removed (2026-07-19). It was never imported anywhere in `src/`, `evals/` or `tests/`, but its pytest plugin autoloaded and broke collection. `ragas` + `langfuse` (both actually used) carry the eval harness.

**Status:** Unresolved — needs human review (likely Claim B: the repo's own CLAUDE.md describes the built code; Claim A records a planned design)
**Impact:** The Listen-Wiseer Project page's eval stack description and any recommendation citing DeepEval's ToolCorrectnessMetric as used in practice.

## Conflict: Judge calibration sample size and whether a calibrated judge may gate a release — 2026-10-30

**Claim A** (from `[[LLM-as-Judge Evaluation]]`, sourced from `data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/eval-approaches.md` and `data/raw/claude-docs/akira/docs/research/2026-09-03-divergence-since-waslosheute-mvp.md`):
> Calibrate the judge with 5–10 sample inputs with human-graded "good" outputs. The judge is a regression detector, never a launch gate; humans decide whether movement is real.

**Claim B** (from new source `data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--05-llm-as-judge.md`, with `notes--04-graders.md`):
> Calibrate with 100–200 human PASS/FAIL labels split train/dev/test, measuring TPR and TNR on the held-out split. A judge is experimental (cannot gate) until calibrated; a calibrated judge may block a release at its calibrated threshold.

The two may partly reflect different contexts (a discovery-stage rubric smoke test and a product whose human inter-rater ceiling was low, vs a general production procedure), but they disagree on both the calibration bar and the gating rule.

**Status:** Unresolved — needs human review
**Impact:** Whether release gates in new builds may rest on an LLM judge; how much human labeling to budget before a judge is trusted. Related: [[Judge Calibration (TPR, TNR and Corrected Pass Rate)]], [[Grader States (Heuristic, Calibrated, Experimental)]], [[Human Agreement Ceiling Protocol]].

## Conflict: Graph UI rendering library (React Flow vs Cytoscape.js) — 2026-10-30

**Claim A** (from `[[Librarian Graph Explorer]]` and `[[Librarian KB — Build Plan]]`, sourced from `data/raw/claude-docs/playground/react-flow-ui.md`, `data/raw/repos/librarian/.claude--docs--plans--2026-10-30-frontend-audit-fixes.md`):
> The graph is rendered with React Flow (`@xyflow/react`); the 2026-10-30 audit plan lists "Replacing React Flow or the layout algorithms" as out of scope. The KB plan's decision table records "React Flow (not Cytoscape, not sigma.js)".

**Claim B** (from new source `data/raw/repos/librarian/README.md`):
> `app/frontend/` — "React + Vite graph UI — Cytoscape.js force-directed graph, chat panel, live wiki watch"; the architecture diagram also labels the UI "React + Cytoscape + chat agent".

Likely a stale README line (the frontend's package manifest lists `@xyflow/react`), but the wiki does not resolve it silently.

**Status:** Unresolved — needs human review
**Impact:** README accuracy for the graph UI; any page describing the frontend stack.

## Conflict: Does few-shot CoT outperform zero-shot CoT? — 2026-10-30

**Claim A** (from `[[Few-Shot Prompting]]`, sourced from `data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt--prompt-engineering.md`):
> Few-shot CoT — examples that show the reasoning chain — "outperforms either technique alone on multi-step tasks".

**Claim B** (from new source `data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--09-evaluating-prompts.md`, citing Clavié et al. 2023):
> On a job-posting classification task, zero-shot CoT (F1 81.4) beat few-shot CoT (F1 78.4); the examples anchored the model. The task needed no expert knowledge.

The two may refer to different task types (genuinely multi-step reasoning vs single-label classification), but Claim A is stated without that qualifier.

**Status:** Unresolved — needs human review
**Impact:** Default technique choice when adding reasoning to a prompt; [[Prompting Technique Selection]], [[Evaluating Prompts]], [[Chain of Thought]].
