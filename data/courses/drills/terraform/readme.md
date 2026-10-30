---
imported_hash: 7499cd1aa93c0fa5
title: Terraform
summary: 'One drill so far: review/web-stack.md, a PR review with nine seeded security, state and reproducibility issues.'
order: 1
kind: reading
source: sisyphus/drills/terraform/README.md
---

# Terraform

One drill so far: [`review/web-stack.md`](review/web-stack.md), a PR review with nine seeded
security, state and reproducibility issues. Terraform shows up in the working repos (galactus, ai-project-template,
the data-engineering course), so drills come from patterns already used there.

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
