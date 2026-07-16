---
source: google_drive
source_id: 1pwOE81ihjrhMphy-Ky1pMHoVNZjM3rw7Oi-d4bOpB24
source_url: https://docs.google.com/document/d/1pwOE81ihjrhMphy-Ky1pMHoVNZjM3rw7Oi-d4bOpB24
type: meeting_notes
date: 2026-06-25
participants: [Ramsey Wise, Daniel Tadros, Shyamali Pawar, Marco Zimmermann]
tags: [bedrock, aws, local-config, onboarding, retrieval, vector-db, opensearch]
---

# Bedrock Local Config — 2026-06-25

## Summary

Detailed walkthrough of AWS Vault access and Bedrock architecture for local dev setup. Focused on retrieval-only (not generate) mode and production vector DB management.

## Key Decisions

- **Raw chunk retrieval over generate**: App uses `retrieve` not `retrieve_and_generate` — allows the application layer to handle the retrieved chunks.
- **Manual vector DB creation in production**: Don't rely on automatic setup; manually manage OpenSearch Serverless for high-traffic production environments.

## Next Steps

- [Daniel Tadros] Send AWS Vault setup Notion link to Shyamali
- [Shyamali] Request ML account access from Dan
- [Shyamali] Configure Bedrock locally; run evaluations; determine ideal knowledge base config
- [Shyamali] Present final KB config to Jeremy (for staging/prod implementation)
- [Shyamali] Reschedule Jeremy onboarding session

## Technical Details

### AWS Access
- Uses AWS SSO + AWS Vault for local credential management
- Add profiles (`p-staging`, `p-production`, `p-dev`) to local AWS config
- Connect via: `aws-vault exec <profile> -- <command>`
- Fix subshell errors by removing existing session before reconnecting

### Bedrock App Architecture
- Python app (`pyproject.toml` deps, env vars for KB ID and region `eu-north-1`)
- `/chunks` endpoint: queries KB with score threshold 0.4 + deduplication
- Identical setup to project-g project — use project-g `.env.example` as reference

### Knowledge Base Setup
- Create new service roles (let Amazon manage permissions)
- Data sources: web crawler or S3 (JSON/text files)
- Apply resource tags for cost tracking by platform team
- Web crawler settings: source URLs, sync scope (host-only / same-host / subdomain), throttling, URL regex filters

### Chunking & Parsing
- Current: hierarchical chunking (parent chunk size, child token size, overlap tokens)
- Other options: fixed-size, semantic, no-chunking
- Lambda functions can be integrated for boilerplate removal

### Embedding & Vector DB
- Embedding: Amazon Titan Text Embedding v2 (available in current region)
- Vector DB: Amazon OpenSearch Serverless (primary option)
- Production: manually create vector DB for high-performance handling
