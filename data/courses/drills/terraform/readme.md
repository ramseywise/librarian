---
imported_hash: 18edaf4d19780a7a
title: Terraform
summary: 'One drill so far: review/web-stack.md, a PR review with nine seeded security, state and reproducibility issues.'
order: 1
kind: reading
source: learn-ai-engineering/practice/drills/terraform/README.md
---

# Terraform

One drill so far: [`review/web-stack.md`](review/web-stack.md), a PR review with nine seeded
security, state and reproducibility issues. Terraform shows up in most deployed systems and in the
[data-engineering course](../../data-engineering/00-start-here/readme.md), so drills come from patterns used there.

## Planned topics

| Topic | Drill shape |
|---|---|
| `basics/` | Providers, resources, variables, outputs, `plan`/`apply` reading |
| `state/` | Remote state, locking, `import`, `state mv` after a refactor |
| `modules/` | Extract a module, inputs/outputs, versioning |
| `debug/` | Read a failing plan: dependency cycles, drift, forced replacement |
| `review/` | Spot problems in a given `.tf` diff (security groups, IAM, secrets in state) |

Drills follow the schema in [`../README.md`](../00-start-here/readme.md); `.tf` starters sit beside the
drill file. Build drills should `terraform validate` without cloud credentials; review drills
are read-only and are never applied.
