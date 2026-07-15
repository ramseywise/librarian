---
source: google_drive
source_id: 1RIGOwe9r-EPL92oiKtPfLz7aJzDROsmPILJeB4lhGNg
source_url: https://docs.google.com/document/d/1RIGOwe9r-EPL92oiKtPfLz7aJzDROsmPILJeB4lhGNg
type: meeting_notes
date: 2026-06-26
participants: [Ramsey Wise, Shyamali Pawar, Yan Zhang]
tags: [rag, ingestion, evaluation, ownership, bedrock, langfuse, galactus]
---

# Final Checkin — 2026-06-26

## Summary

Clarified technical ownership boundaries and aligned on evaluation priorities amid concerns about documentation and cross-team communication.

## Key Decisions

- **Team ownership established**: Shyamali owns RAG ingestion, data pipelines, and feedback loops. AI engineering (Yan, Dan) owns VA agents and evaluation datasets.
- **Passage-level grounding dataset** added to backlog: Shyamali to create and human-validate a passage-level conversation grounding dataset.

## Next Steps

- [Shyamali] Create passage-level grounding dataset and perform human validation on a subsample
- [Shyamali] Store Bedrock-ingested articles to S3
- [Shyamali + Ramsey] Attend Longfuse evaluation pipeline meeting Monday at 11am

## Key Discussion Points

- **Chunking strategy**: Dan changed chunking without team alignment. Ramsey pushed back — current simple dense retrieval doesn't benefit much from chunking changes; data parsing/cleaning is the higher priority.
- **Grounding data**: Current grounding dataset is at URL level (human-verified). Team needs passage-level validation. Ramsey suggested using true-positive chunks from his recent evaluation run as a starting point for human validation.
- **MCP servers**: Yan confirmed a Notion page lists current MCP servers, but not all are implemented.
- **VA lifecycle ownership**: Shyamali owns platform (AWS/Go). Dan/Daniel/Yan own VA agent lifecycle. Jeremy owns Longfuse and Bedrock Terraform.
- **Jeremy note**: Jeremy sometimes acts without consulting the team (e.g., used wrong data source for Longfuse — old bookkeeping hero data instead of validated Intercom data).
- **Bedrock ingestion frequency**: Unknown/undecided — needs to be determined once ingestion is cleaned up. Marco working on metadata enrichment.
- **Trace collection**: Not yet operational. Plan is to push ingested articles to S3 and wire VA traces through Longfuse.
- **Evaluation dashboards**: No standard dashboards available. Ramsey built a temporary HTML eval reports pipeline (in Galactus).
- **Failure taxonomy**: No official taxonomy yet. Starting point in Yan's report and Galactus summary markdown.
