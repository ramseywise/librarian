# Linear Issues — Evaluation & Improvement (VIR)

**Fetched:** 2026-04-24
**Project ID:** 0a8d257d-d290-4813-b74f-af58663749b2
**Team:** Businesshealth-Virtual-Assistant (VIR)
**Status:** In Progress
**Target date:** 2026-06-30 (Q2)
**Count:** 43 issues

## Project Description

Establish the foundation to understand, measure, and continuously improve system performance and quality across HC and VA. Three areas:

1. **HC Data Ingestion** (Billy → Intercom → BedrockKB) — blocks MVP
2. **HC Feedback Loop** (CS agent onboarding and validation of data samples)
3. **HC Evaluation** (Intercom/BookKeeping Hero historical conversations for baseline eval) — does not block MVP

**Q3:** HC/VA Evaluation blocked by MVP launch with observability in place → Q3 priority to compare with BookKeeper Hero baseline eval.

---

## Milestones

### M1: Access & Onboarding Complete (target: 2026-05-08)
The team has confirmed access to all required systems, completed onboarding sessions with Dan and the CS team, and fully scoped RAG resources. Nothing else can start until this is done.
- VIR-95: Onboard to Billy Ingestion and Storage to BedrockKB
- VIR-96: Onboarding with CS team + Intercom Workflow Exploration
- VIR-99: Onboard to Intercom Historical Conversations Data
- VIR-100: Onboarding to BookKeeping Hero Data
- Stretch: VIR-98 (Article Content Audit), VIR-101 (EDA on BKH Data)

### M2: RAG Sources Ingested & Documented (target: 2026-05-22)
Billy ingestion configured and running, Intercom extraction initiated, full RAG source picture documented. Annotation guidelines agreed.
- Track 1 (Raw Data): VIR-105, VIR-102, VIR-103, VIR-104, VIR-106, VIR-107
- Track 2 (Human Validation): VIR-118, VIR-119, VIR-120, VIR-121

### M3: Historical Data Set Ingested, Cleaned & Explored (target: 2026-06-05)
BKH and Intercom historical data extracted, GDPR confirmed, initial EDA complete. CS agents completed first annotation batch.
- Track 1 (Intercom Ingestion & Masking): VIR-109, VIR-110, VIR-111, VIR-116, VIR-117, VIR-112, VIR-115, VIR-114
- Track 2 (Data Exploration & Annotation): VIR-113, VIR-125, VIR-108, VIR-133, VIR-124

### M4: Baseline Eval for BookKeeper Hero (target: 2026-06-12)
BKH performance baseline documented. First annotated dataset seeded from BKH explicit feedback.
- Track 1 (Edge Cases): VIR-128, VIR-129, VIR-127, VIR-130

### M5: Human Validated Dataset (target: 2026-06-26)
Initial ~50 conversation eval dataset curated, stratified by top Danish market intents, validated by CS agents.
- Track 1 (Golden Eval Set): VIR-123, VIR-122, VIR-132, VIR-131
- Stretch/Q3: VIR-126, VIR-134, VIR-135, VIR-136, VIR-137, VIR-138

---

## Issues

---

### [VIR-95] Onboard to Billy Ingestion and Storage to BedrockKB
**Status:** To Do | **Priority:** High | **Points:** 5
**Assignee:** Yan Zhang | **Labels:** HC Data Ingestion
**URL:** https://linear.app/shine-co/issue/VIR-95/onboard-to-billy-ingestion-and-storage-to-bedrockkb

**Goal:** Understand the scope of BedrockKB raw documents already ingested from Billy (help center urls, currently being migrated to Intercom) and determine what still needs to be done for MVP.

**Context:** Some Help Center documents have already been ingested for BookKeeping Hero, but there is no clear picture of coverage scope. Before any new ingestion work begins, the team needs to understand what exists, what is missing, and whether a second ingestion pass is needed or if the existing setup can be extended.

---

### [VIR-96] Onboarding with CS Team + Intercom Workflow Exploration
**Status:** To Do | **Priority:** High | **Points:** 8
**Assignee:** Marco Enrique Zimmermann | **Labels:** HC Feedback Loop
**URL:** https://linear.app/shine-co/issue/VIR-96/onboarding-with-cs-team-intercom-workflow-exploration

**Goal:** Get a knowledge share from the CS team on their ways of working and explore how Intercom is used in practice — specifically to understand how to solve HC requests, differentiate when escalation is needed and frictionless UI for how CS agents can view and annotate conversations within the existing workflow.

**Context:** CS agents are central to the HITL queues — they will be the ones annotating conversations for the feedback loop.

---

### [VIR-98] Explore & Audit Article Content
**Status:** To Do | **Priority:** High | **Points:** 5
**Assignee:** Yan Zhang | **Labels:** HC Data Ingestion
**URL:** https://linear.app/shine-co/issue/VIR-98/explore-and-audit-article-content

**Goal:** Explore the Billy domains and any already-ingested sources to understand content structure, identify what should and shouldn't be ingested, and map how article metadata could support retrieval filtering.

**Context:** Before any ingestion pipeline is built, the team needs a clear picture of what content exists, how it is structured, and what quality bar it meets. Includes understanding URL patterns, article types, and available metadata.

---

### [VIR-99] Onboard to Intercom Historical Conversations Data
**Status:** To Do | **Priority:** High | **Points:** 5
**Assignee:** Yan Zhang | **Labels:** HC Feedback Loop
**URL:** https://linear.app/shine-co/issue/VIR-99/onboard-to-intercom-historical-conversations-data

**Goal:** Understand how to access Intercom historical conversation data so it can be used to build the eval dataset and seed the HITL queues.

**Context:** Intercom conversation history is the primary data source for the HC eval set. Before any data exploration or dataset curation can begin, the team needs to understand what data is available, how to access it, what format it comes in, and what constraints apply — API rate limits, data retention windows, language distribution.

---

### [VIR-100] Onboarding to BookKeeping Hero Data
**Status:** To Do | **Priority:** High | **Points:** 3
**Assignee:** Marco Enrique Zimmermann | **Labels:** HC Feedback Loop
**URL:** https://linear.app/shine-co/issue/VIR-100/onboarding-to-bookkeeping-hero-data

**Goal:** Get access to BookKeeping Hero conversation history and understand its structure so it can be used alongside Intercom data for cross-comparison and eval dataset curation.

**Context:** BookKeeping Hero conversation data is a secondary source for seeding the eval dataset — specifically for explicit feedback signals (thumbs up/down) that help identify high-quality and poor-quality model responses. Access is likely via CSV export.

---

### [VIR-101] EDA on BookKeeping Hero Data
**Status:** To Do | **Priority:** High | **Points:** 5
**Assignee:** Marco Enrique Zimmermann | **Labels:** HC Evaluation
**URL:** https://linear.app/shine-co/issue/VIR-101/eda-on-bookkeeping-hero-data

**Goal:** Explore BookKeeping Hero conversation data to understand its structure, quality, and signal availability — and use findings to establish a performance baseline that MVP can be evaluated against.

**Context:** Unlike Intercom data which is used to build the eval dataset, BookKeeping Hero data serves a different purpose here: it represents existing system performance before the HC AI assistant is live. Understanding how conversations are structured and where BKH struggles establishes the baseline the new system must beat.

---

### [VIR-102] Configure & Run Web Crawler on Billy Domains (AWS)
**Status:** Backlog | **Priority:** High | **Points:** 5
**Labels:** HC Data Ingestion
**URL:** https://linear.app/shine-co/issue/VIR-102/configure-and-run-web-crawler-on-billy-domains-aws

**Goal:** Configure the AWS web crawler to crawl billy.dk/support, billy.dk/billypedia, and billy.dk/pris using the agreed filter rules, and produce clean structured output ready for Bedrock KB ingestion.

**Context:** Filter logic and content exclusion rules are defined in VIR-98. Blocked on that ticket completing.

---

### [VIR-103] Explore Available Metadata Across Billy Domains and Define Initial Schema
**Status:** Backlog | **Priority:** High | **Points:** 3
**Labels:** HC Data Ingestion
**URL:** https://linear.app/shine-co/issue/VIR-103/explore-available-metadata-across-billy-domains-and-define-initial

**Goal:** Review what metadata is actually available from the crawler output across the three Billy domains, and define an initial schema grounded in what the data can realistically support.

**Context:** Schema needs to cover at minimum: market, language, source type, timestamp, and freshness — but fields and structure should be driven by what is available in the data, not assumed upfront.

---

### [VIR-104] Ingest Billy Content into Bedrock KB and Validate
**Status:** Backlog | **Priority:** High | **Points:** 3
**Labels:** HC Data Ingestion
**URL:** https://linear.app/shine-co/issue/VIR-104/ingest-billy-content-into-bedrock-kb-and-validate

**Goal:** Run ingestion of the crawled Billy content into Bedrock Knowledge Base and validate that content is retrievable, accurate, and clean.

**Context:** Final step of the Ingest Billy Raw Articles initiative. Support articles were recently updated so data quality may already be good, but retrieval quality needs to be spot-checked across all three domains.

---

### [VIR-105] Agree Review Scope & Prioritisation
**Status:** Backlog | **Priority:** High | **Points:** 1
**Labels:** HC Data Ingestion
**URL:** https://linear.app/shine-co/issue/VIR-105/agree-review-scope-and-prioritisation

**Goal:** Define what gets validated, in what order, and who owns it — for both Help Center articles and conversation data — before any review work begins.

**Context:** Without agreed scope, the review has no boundaries and will slip. Full audit vs. top-intent coverage first has significant impact on timeline and expert availability.

---

### [VIR-106] Domain Expert Article Review
**Status:** Backlog | **Priority:** High | **Points:** 5
**Labels:** HC Data Ingestion
**URL:** https://linear.app/shine-co/issue/VIR-106/domain-expert-article-review

**Goal:** Accounting/tax and product domain experts work through the prioritised Help Center article list, marking each article as approved for ingestion, needs updating, or exclude.

**Context:** Articles may be technically published but factually outdated relative to current product behaviour. The output of this review directly determines what gets ingested — nothing should enter the pipeline without a clear pass or exclude decision.

---

### [VIR-107] Remediate Flagged Articles
**Status:** Backlog | **Priority:** High | **Points:** 3
**Labels:** HC Data Ingestion
**URL:** https://linear.app/shine-co/issue/VIR-107/remediate-flagged-articles

**Goal:** Update or exclude articles flagged during domain expert review. Ensure all approved content is published before ingestion begins.

**Context:** Remediation scope must be bounded — updates limited to factual corrections, not rewrites, unless explicitly agreed.

---

### [VIR-108] Conversation Data Quality Review
**Status:** Backlog | **Priority:** High | **Points:** 3
**Labels:** HC Data Ingestion
**URL:** https://linear.app/shine-co/issue/VIR-108/conversation-data-quality-review

**Goal:** Assess the cleaned and masked Intercom conversation data for quality, completeness, and usefulness before it feeds downstream tasks such as clustering and benchmarking.

**Context:** Sanity check after extraction and PII masking — checking for over-masking, missing fields, language distribution, and overall signal quality.

---

### [VIR-109] Confirm Intercom API Access & Credentials
**Status:** Backlog | **Priority:** High | **Points:** 1
**Labels:** HC Data Ingestion
**URL:** https://linear.app/shine-co/issue/VIR-109/confirm-intercom-api-access-and-credentials

**Goal:** Verify that Intercom API access is available, credentials are in hand, and rate limits are understood before any engineering work begins.

**Context:** Nothing else in this initiative can start until API access is confirmed. Rate limits directly affect how long a historical backfill will take.

---

### [VIR-110] Confirm Storage Destination & GDPR Position
**Status:** Backlog | **Priority:** High | **Points:** 1
**Labels:** HC Data Ingestion
**URL:** https://linear.app/shine-co/issue/VIR-110/confirm-storage-destination-and-gdpr-position

**Goal:** Ops confirms and provisions Snowflake or S3 as the storage destination. Legal/Ops confirms GDPR and data residency policy before any conversation data lands anywhere.

**Context:** Raw Intercom conversations contain PII. Data must not land in any storage destination until the legal position is confirmed. Hard blocker for the extraction job.

---

### [VIR-111] Explore & Map Intercom Conversation Schema
**Status:** Backlog | **Priority:** High | **Points:** 3
**Labels:** HC Data Ingestion
**URL:** https://linear.app/shine-co/issue/VIR-111/explore-and-map-intercom-conversation-schema

**Goal:** Pull sample conversation data from the Intercom API and document the data shape, available fields, and transformation logic needed to make it usable for downstream tasks.

**Context:** Before building the extraction job we need to understand what we're actually getting — field availability, conversation structure, language distribution, and data volume.

---

### [VIR-112] Build One-Time Extraction & Transform Job
**Status:** Backlog | **Priority:** High | **Points:** 5
**Labels:** HC Data Ingestion
**URL:** https://linear.app/shine-co/issue/VIR-112/build-one-time-extraction-and-transform-job

**Goal:** Implement the one-time job that connects to the Intercom API, extracts historical conversations, transforms them to the agreed format, and lands them in the provisioned storage destination.

**Context:** MVP scope is one-time only — continuous sync is explicitly out of scope until data quality and value are validated. Build cleanly enough that continuous sync can be added later without a full rewrite.

---

### [VIR-113] Validate Extracted Intercom Data & Hand Off to EDA
**Status:** Backlog | **Priority:** High | **Points:** 3
**Labels:** HC Data Ingestion
**URL:** https://linear.app/shine-co/issue/VIR-113/validate-extracted-intercom-data-and-hand-off-to-eda

**Goal:** Spot-check the extracted and transformed conversation data for quality and completeness, and confirm it is ready to feed into the EDA and downstream eval work.

**Context:** Sign-off step before extracted data is consumed by EDA and eval dataset curation. Quality issues caught here are cheaper to fix than after downstream tasks are built on bad data.

---

### [VIR-114] Validate Masking Coverage & Sign Off
**Status:** Backlog | **Priority:** Medium | **Points:** 3
**Labels:** HC Data Ingestion
**URL:** https://linear.app/shine-co/issue/VIR-114/validate-masking-coverage-and-sign-off

**Goal:** Test the masking layer against real sample conversation data to confirm it catches both explicit and contextual PII, and get final sign-off from Legal/Ops before masked data flows downstream.

**Context:** Validation must go beyond obvious fields. Contextual PII — company names, account references, implicit identifiers — is where masking typically fails.

---

### [VIR-115] Implement PII Masking Layer
**Status:** Backlog | **Priority:** Medium | **Points:** 5
**Labels:** HC Data Ingestion
**URL:** https://linear.app/shine-co/issue/VIR-115/implement-pii-masking-layer

**Goal:** Build the masking step based on the agreed approach and integrate it at the confirmed point in the pipeline.

**Context:** Must handle both obvious PII (email, phone) and contextual PII (company names, implicit identifiers) depending on agreed approach. Must not be skippable or bypassable in the pipeline.

---

### [VIR-116] Evaluate & Select Masking Approach
**Status:** Backlog | **Priority:** Medium | **Points:** 3
**Labels:** HC Data Ingestion
**URL:** https://linear.app/shine-co/issue/VIR-116/evaluate-and-select-masking-approach

**Goal:** Run a technical spike to evaluate regex, LLM-based, and hybrid masking approaches against coverage, cost, and latency tradeoffs. Produce a recommendation for sign-off before build begins.

**Context:** Regex alone will miss contextual PII. LLM-based masking improves coverage but adds cost and latency. Right approach depends on legal bar and data volume.

---

### [VIR-117] Legal & Ops Sign-off on Masking Approach
**Status:** Backlog | **Priority:** High | **Points:** 1
**Labels:** HC Data Ingestion
**URL:** https://linear.app/shine-co/issue/VIR-117/legal-and-ops-sign-off-on-masking-approach

**Goal:** Get written confirmation from Legal/Ops on the approved masking approach and the point in the pipeline where masking must be applied before any conversation data is processed.

**Context:** Compliance blocker for the entire GDPR & PII Masking initiative. Without confirmed legal position, no conversation data can move through the pipeline.

---

### [VIR-118] Validate CS Agents are Ready to Annotate
**Status:** Backlog | **Priority:** Medium | **Points:** 1
**Labels:** HC Feedback Loop
**URL:** https://linear.app/shine-co/issue/VIR-118/validate-cs-agents-are-ready-to-annotate

**Goal:** Validate that CS agents are ready to annotate before either HITL queue goes live. Hard dependency for the entire HITL workstream.

**Context:** Validation based on inter-annotator agreement reaching a minimum threshold, not just attendance. Without this gate, annotation quality cannot be trusted.

---

### [VIR-119] Run Training Session with CS Team
**Status:** Backlog | **Priority:** Medium | **Points:** 1
**Labels:** HC Feedback Loop
**URL:** https://linear.app/shine-co/issue/VIR-119/run-training-session-with-cs-team

**Goal:** Deliver a training session with the CS team to walk through annotation guidelines, tagging schema, and tooling before HITL queues go live.

**Context:** Live calibration session is critical to surface misunderstandings that written material alone won't catch. Agents should annotate sample conversations together and discuss disagreements.

---

### [VIR-120] Prepare Training Material and Tooling
**Status:** Backlog | **Priority:** Medium | **Points:** 3
**Labels:** HC Feedback Loop
**URL:** https://linear.app/shine-co/issue/VIR-120/prepare-training-material-and-tooling

**Goal:** Produce training materials CS agents can learn the annotation guidelines from, and ensure annotation tooling is set up and accessible before the training session goes live.

**Context:** Training materials translate the guidelines into something agents can actively learn from — worked examples, edge cases, a reference playbook.

---

### [VIR-121] Define Annotation Guidelines and Tagging Schema
**Status:** Backlog | **Priority:** High | **Points:** 3
**Labels:** HC Feedback Loop
**URL:** https://linear.app/shine-co/issue/VIR-121/define-annotation-guidelines-and-tagging-schema

**Goal:** Define the annotation guidelines and tagging schema CS agents will use across both HITL queues, ensuring tags are specific enough that different agents label consistently.

**Context:** Foundational document for the entire HITL workstream. Tagging criteria must be precise and unambiguous — annotation quality is the basis everything else is built on.

---

### [VIR-122] Summarise Annotations and Route to Feedback
**Status:** Backlog | **Priority:** Medium | **Points:** 3
**Labels:** HC Feedback Loop
**URL:** https://linear.app/shine-co/issue/VIR-122/summarise-annotations-and-route-to-feedback

**Goal:** Synthesise the first batch of CS annotations into structured findings and route outputs to the appropriate downstream workstreams — eval dataset curation and failure-attribution analysis.

**Context:** Annotations serve two purposes: conversations with corrected responses feed the eval dataset; conversations where the model could have done better feed the failure-attribution queue.

---

### [VIR-123] Explore How Agents Annotate First Batch
**Status:** Backlog | **Priority:** Medium | **Points:** 3
**Labels:** HC Feedback Loop
**URL:** https://linear.app/shine-co/issue/VIR-123/explore-how-agents-annotate-first-batch

**Goal:** Run the first annotation round with CS agents on the prepared batch, observe the process, and surface any issues with the tagging schema, tooling, or workflow before scaling up.

**Context:** First real test of annotation guidelines and tooling in practice. Goal is to learn — where do agents hesitate, where do they disagree, what is unclear in the guidelines.

---

### [VIR-124] Prepare First Sampling Batch for CS Annotation
**Status:** Backlog | **Priority:** Medium | **Points:** 3
**Labels:** HC Feedback Loop
**URL:** https://linear.app/shine-co/issue/VIR-124/prepare-first-sampling-batch-for-cs-annotation

**Goal:** Pull and prepare the first batch of sampled conversations from the historical Intercom dataset, ready for CS agents to annotate.

**Context:** Using the sampling plan from VIR-125, covers the practical work of pulling conversations, formatting for annotators, and making them accessible.

---

### [VIR-125] Define Sampling Strategy for Historical Intercom Data
**Status:** Backlog | **Priority:** High | **Points:** 3
**Labels:** HC Feedback Loop
**URL:** https://linear.app/shine-co/issue/VIR-125/define-sampling-strategy-for-historical-intercom-data

**Goal:** Define the scope, selection logic, and volume for the first batch of historical Intercom conversations to be sampled for CS agent annotation.

**Context:** MVP sampling is manual — not about building a trigger mechanism, but making deliberate decisions on which conversations to pull. Sampling should be stratified to cover the most frequent intent categories.

---

### [VIR-126] Summarise Edge Case Annotations for Feedback
**Status:** Backlog | **Priority:** Medium | **Points:** 3
**Labels:** HC Feedback Loop
**URL:** https://linear.app/shine-co/issue/VIR-126/summarise-edge-case-annotations-for-feedback

**Goal:** Synthesise CS agent annotations from the edge case batch into structured failure-attribution findings and route outputs to the eval dataset and downstream improvement work.

**Context:** Edge case annotations are specifically about failure attribution — why conversations went wrong and clustering failure modes. Findings feed the failure-attribution taxonomy.

---

### [VIR-127] Define Risk Signal Triggers and Thresholds
**Status:** Backlog | **Priority:** Medium | **Points:** 3
**Labels:** HC Feedback Loop
**URL:** https://linear.app/shine-co/issue/VIR-127/define-risk-signal-triggers-and-thresholds

**Goal:** Turn the EDA findings into a concrete written trigger spec — which signals fire, at what thresholds, and how they compose — so that a future engineering implementation has a clear, signed-off spec to build against.

**Context:** Spec-only for MVP. No engineering implementation in scope yet. Threshold calibration is the key risk — too low overwhelms agents, too high misses failures.

---

### [VIR-128] Define Edge Case Sampling Strategy
**Status:** Backlog | **Priority:** Medium | **Points:** 3
**Labels:** HC Feedback Loop
**URL:** https://linear.app/shine-co/issue/VIR-128/define-edge-case-sampling-strategy

**Goal:** Define which friction signals to use for manual edge case selection in the MVP, how many conversations to pull, and how to avoid overlap with the random sampling queue.

**Context:** MVP edge case sampling is manual — no automated trigger being built. Decides which conversations to pull from historical dataset based on EDA findings.

---

### [VIR-129] EDA on Friction Signals
**Status:** Backlog | **Priority:** High | **Points:** 5
**Labels:** HC Feedback Loop
**URL:** https://linear.app/shine-co/issue/VIR-129/eda-on-friction-signals

**Goal:** Run exploratory data analysis across available friction signals — escalations, thumbs down, Intercom conversation history patterns — to understand their distributions, overlaps, and predictive value for real HC failures.

**Context:** Before edge cases can be selected or triggers defined, the team needs to know what friction signals actually look like in practice — frequency, correlation, and whether they correlate with actual model failures.

---

### [VIR-130] Curate Edge Case Dataset from Failure-Attribution Analysis
**Status:** Backlog | **Priority:** Medium | **Points:** 3
**Labels:** HC Evaluation
**URL:** https://linear.app/shine-co/issue/VIR-130/curate-edge-case-dataset-from-failure-attribution-analysis

**Goal:** Build a targeted edge case subset of the eval dataset drawn from failure-attribution findings, covering the most important failure modes identified through the edge case annotation queue.

**Context:** Complements the main ~50 conversation dataset with a focused set of harder, failure-mode-specific examples for testing the eval harness on known weak spots.

---

### [VIR-131] Curate Initial Eval Dataset (~50 Conversations)
**Status:** Backlog | **Priority:** Medium | **Points:** 5
**Labels:** HC Evaluation
**URL:** https://linear.app/shine-co/issue/VIR-131/curate-initial-eval-dataset-50-conversations

**Goal:** Curate the initial versioned eval dataset of ~50 conversations covering key Danish market intent categories, stratified by high-impact intents and seeded from BookKeeping Hero explicit feedback and CS agent annotations.

**Context:** Foundation of the offline eval harness — seeds the judge grader and expands incrementally as new golden traces and failure modes surface through review queues.

---

### [VIR-132] Eval Dataset Schema Definition
**Status:** Backlog | **Priority:** Medium | **Points:** 3
**Labels:** HC Evaluation
**URL:** https://linear.app/shine-co/issue/VIR-132/eval-dataset-schema-definition

**Goal:** Define the schema for the versioned eval dataset, ensuring compatibility with the eval harness and downstream graders before any curation begins.

**Context:** Schema must support capability tests and judge graders. Needs to accommodate: intent category, source signal (thumbs up / CS annotation), trace ID, ground truth response, and version-conflict flag. Schema versioning is important.

---

### [VIR-133] EDA on Intercom Data
**Status:** Backlog | **Priority:** High | **Points:** 3
**Labels:** HC Evaluation
**URL:** https://linear.app/shine-co/issue/VIR-133/eda-on-intercom-data

**Goal:** Conduct exploratory data analysis on Intercom conversation data to understand what we have before committing to a dataset schema or curation strategy.

**Context:** Before building the eval set, need a clear picture of raw data: conversation structure, intent distribution, turn counts, context window sizes, and data quality. Directly informs stratification strategy and schema design.

---

### [VIR-134] Automated Data Correctness Validation
**Status:** Backlog | **Priority:** Low | **Points:** 3
**Labels:** HC Data Ingestion
**URL:** https://linear.app/shine-co/issue/VIR-134/automated-data-correctness-validation

**Goal:** Implement ongoing health monitoring for the Bedrock KB — detecting broken links, empty content blocks, and outdated content across ingested sources.

**Context:** Low priority for Q2 — likely starts Q3. Not blocking for launch but should be scoped and scheduled early post-MVP before content drift becomes a problem.

---

### [VIR-135] Coverage Benchmarking
**Status:** Backlog | **Priority:** Low | **Points:** 3
**Labels:** HC Data Ingestion
**URL:** https://linear.app/shine-co/issue/VIR-135/coverage-benchmarking

**Goal:** Use a representative set of real Intercom questions to query the RAG system pre-launch and validate that indexed content provides sufficient grounding to prevent hallucinations.

**Context:** Low priority for Q2 — likely starts Q3. One-time pre-launch validation. Test query set must be drawn from representative questions, not synthetic ones.

---

### [VIR-136] Support Ticket Clustering
**Status:** Backlog | **Priority:** Low | **Points:** 5
**Labels:** HC Evaluation
**URL:** https://linear.app/shine-co/issue/VIR-136/support-ticket-clustering

**Goal:** Group historic Intercom tickets by topic similarity to understand knowledge base coverage gaps and inform ongoing content strategy.

**Context:** Low priority for Q2 — likely starts Q3. Exploratory in nature. Blocked on GDPR masking being complete so clean data is available.

---

### [VIR-137] Failure-Attribution Taxonomy
**Status:** Backlog | **Priority:** Low | **Points:** 3
**Labels:** HC Evaluation
**URL:** https://linear.app/shine-co/issue/VIR-137/failure-attribution-taxonomy

**Goal:** Cluster failure cases from the edge case annotation queue, define a formal failure-attribution taxonomy, and build a structured edge case dataset from it to guide ongoing annotation and eval harness expansion.

**Context:** Low priority for Q2 — likely starts Q3. The taxonomy formalises what "failure" means across the system, grouping failure modes into a stable classification.

---

### [VIR-138] LLM-as-Judge Grader
**Status:** Backlog | **Priority:** Low | **Points:** 5
**Labels:** HC Evaluation
**URL:** https://linear.app/shine-co/issue/VIR-138/llm-as-judge-grader

**Goal:** Build an offline evaluation tool that scores conversational outputs against the eval dataset using a judge prompt, and calibrate it against human labels before scores are trusted.

**Context:** Low priority for Q2 — likely starts Q3. Automates quality scoring across the eval dataset — covering factual correctness, source grounding, escalation appropriateness, and tone. Must be calibrated against human labels before scores are used.
