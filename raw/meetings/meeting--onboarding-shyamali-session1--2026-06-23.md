---
source: google_drive
source_id: 1PKJjT6-QB2Ij0IM2dTjaO40zLnxQ8s0LiVXOm98Ewqo
source_url: https://docs.google.com/document/d/1PKJjT6-QB2Ij0IM2dTjaO40zLnxQ8s0LiVXOm98Ewqo
type: meeting_notes
date: 2026-06-23
participants: [Ramsey Wise, Shyamali Pawar]
tags: [onboarding, va-agents, hca, typescript, python, evaluation, bedrock, langfuse, galactus]
---

# Onboarding with Shyamali — 2026-06-23

## Summary

Session 1 of Shyamali's onboarding. Covered VA and HCA repository structure, current stack decisions, evaluation challenges, and how Shyamali should orient her first week.

## Key Decisions

- Transition plan: Current VA is TypeScript/Google ADK (MVP). Future plan is Python agents as core logic, with TS repo as frontend/backend bridge.
- Shyamali's focus: RAG evaluation and platform work (AWS/Go). Not responsible for VA agent code changes.
- Communication: Use `#va-data-evaluation-galactus` Slack channel; postpone ticket creation until after onboarding week.

## Next Steps

- [Shyamali] Request access to VA and HCA staging environments (contact Daniel Tadros)
- [Shyamali] Request Langfuse access (contact Dan)
- [Shyamali] Track all open questions daily; consolidate into running list
- [Ramsey] Share guidance document with Shyamali
- [Shyamali] Notify Dan via `#va-data-evaluation-galactus` that ticket creation is postponed until post-onboarding
- [Ramsey] Add Shyamali to the Slack channel

## Architecture Overview

### Repos
- **VA Agents repo** (TypeScript, Google ADK): Houses both VA and HCA. Main agent config + prompt + tool calls.
- **Key tool**: `support_knowledge` → calls Bedrock KB → returns ID, score, title, URL, text → passed to Gemini agent
- **VA is in production (staging+prod)**; HCA is not in production (blocked pending evaluation)

### VA Tool Call Flow
1. User query → VA agent (TS/Google ADK)
2. 3 parallel multi-query RAG calls to Bedrock → up to 15 URLs returned
3. Best results selected → passed to Gemini for response

### HCA Issues (Dan's additions — not in prod)
- Added claims extraction ("yellow highlighter" metaphor), reciprocal rank fusion, language detection, iterative RAG with retry loop (max 6 steps)
- No re-ranker, discards earlier selections — not well-thought-through
- Sebastian blocked HCA from prod until proper evaluation is done

## Performance Issues
- VA hit rate has a ceiling due to Bedrock ingestion pipeline issues and bad parsing of Billy pages
- False positives: VA retrieves Billipedia articles (non-support)
- HCA has no re-ranker and is discarding retrieval results
- Historical Intercom data uses Billy DK URLs, not the Shine Intercom URLs → evaluation mapping needed

## Evaluation Approach
- Two data sets: Bookkeeping Hero (structured tabular) and Intercom data
- Billy DK → Shine.co URL mapping being compiled by Ramsey (human-verified by Anders)
- Ground truth: URL-level grounding set; Ramsey building updated version with correct mappings
- Longfuse: used for datasets + experiments; Jeremy wiring it for online evaluation
- Galactus: offline evaluation pipeline → HTML eval reports (temporary dashboard substitute)

## Team Contacts
- **Daniel Tadros**: VA/HCA backend + staging access
- **Jeremy**: Longfuse, MCP, Bedrock Terraform
- **Yan**: Evaluation data sets, escalation analysis
- **Dan**: Ask via channel only; don't engage 1:1 for technical direction
- **Anders**: Bedrock subscription/alpha access
