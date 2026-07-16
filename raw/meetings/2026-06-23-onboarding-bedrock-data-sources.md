---
source: google_drive
source_id: 10uXN-6JhFr8HC2vc8cP9ZQ-L9KTgDmB9Q1TUNeNM5EA
source_url: https://docs.google.com/document/d/10uXN-6JhFr8HC2vc8cP9ZQ-L9KTgDmB9Q1TUNeNM5EA
type: meeting_notes
date: 2026-06-23
participants: [Ramsey Wise, Marco Zimmermann, Shyamali Pawar]
tags: [bedrock, data-sources, knowledge-base, rag, evaluation, chunking, opensearch, project-g, langfuse]
---

# Onboarding — Bedrock & Data Sources — 2026-06-23

## Summary

Marco walked through the current Bedrock staging KB architecture, data sources, EDA findings, and pending cleanup work. Ramsey aligned the team on evaluation methodology direction.

## Key Decisions

- **KB restricted to Danish Intercom content only**: Remove English articles (duplicate, wrong market focus) and Billipedia entries. Keep pricing page but fix its parsing.
- **Data sources restricted to Intercom pages** going forward to resolve parsing/quality issues.
- **Langfuse selected for evaluation pipeline**: Standardize metrics for stakeholders.
- **Sentence fragmentation check** added to corpus quality checklist.

## Next Steps

- [Marco] Remove English articles and Billipedia from crawler setup
- [Marco] Filter Excel templates inadvertently crawled
- [Marco] Validate chunking, add sentence fragmentation check
- [Marco] Update engineering landing page (Notion/MD)
- [Marco + Yan] Review Ramsey's findings doc; collaborate on Thursday presentation
- [Marco] Upload frequency questions to GitHub
- [Marco] Create evaluation doc for HCA/VA (exclude VA-agent-specific data)
- [Ramsey] Present project-g repo + data/eval pipelines to Shyamali
- [Ramsey] Sync with Yan on evaluation methodology
- [Shyamali] Review all shared docs; prep question list for daily check-ins
- [Shyamali] Create backlog tickets Friday afternoon post-consolidation

## Bedrock Architecture (Staging)

### Current Data Sources (4 total, web-crawled)
1. **Pricing page** (1 page, 59 chunks) — hierarchical chunking; table structure causes chunks too small → pricing info gets cut off. Needs fix.
2. **Billipedia** — encyclopedic marketing articles; to be removed
3. **client-a Intercom articles (Danish)** — target source; keep
4. **client-a Intercom articles (English)** — duplicate/partial translations; to be removed

Production is a copy of staging for now.

### Data Quality Issues
- Duplicate image/copyright chunks not affecting retrieval (low priority) but wasting storage
- Excel templates accidentally crawled → to be filtered
- Dead links: ignorable, will be replaced by updated Intercom content
- Pricing page: table structure → chunks too small → incomplete pricing answers (known failure mode)
- 10% of historical Intercom data includes URLs → limits URL-level grounding coverage

### Metadata
- Current fields: document ID, chunk ID, URL, data source, chunk text, parent text
- Source type always `web`; most other auto-fields are metadata noise
- Additional metadata (slugs, etc.) to be added in future iterations

### EDA Findings (Marco's notebooks in project-g)
- Token count distribution, URL taxonomy, chunk size distribution
- Duplication analysis: mostly image/copyright boilerplate — not a retrieval concern
- Failure mode analysis: ~16 of 18 tested intents showed content gaps (possible methodology bug — Marco to investigate)

## Evaluation Architecture

- **Offline**: project-g repo → eval pipelines → HTML reports (Ramsey)
- **Online**: Longfuse (Jeremy wiring datasets + metrics)
- **Ground truth**: URL-level grounding set (human-verified) → passage-level next step
- **Smoke tests**: Marco's validation matrix — basic scenarios, out-of-scope detection
- **Source fidelity**: Only ~10% of historical Intercom conversations include source URLs → significant gap; prompt-only citation enforcement is insufficient → need a safeguard (score threshold gate or citation presence check before response delivery)

## Failure Taxonomy
- No official taxonomy yet
- Starting points: Ramsey's project-g summary markdown, Yan's report
- Marco investigating content gap analysis (coverage by intent)

## Team Contacts
- **Marco**: Bedrock KB, data sources, EDA, corpus quality
- **Jeremy**: Bedrock Terraform, Longfuse integration
- **Yan**: Escalation analysis, intent taxonomy, evaluation datasets
- **Daniel Tadros**: Bedrock local config walkthrough (session on Thursday)
