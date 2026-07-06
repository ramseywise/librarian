---
name: github-projects
description: Use when a skill needs to sync with GitHub Projects V2 — provides GraphQL templates for status updates, iteration assignment, sub-issue management, and issue creation.
---

## Configuration

Read from CLAUDE.md `GitHub Project Integration` section:

| Variable | CLAUDE.md field |
|----------|-----------------|
| `{REPO}` | `Repository:` (`owner/repo`) |
| `{ORG}` | owner part of `{REPO}` |
| `{PROJECT_NUMBER}` | last segment of project URL |
| `{PROJECT_ID}` | `Project ID:` |
| `{STATUS_FIELD_ID}` | `Status field ID:` |
| `{ITERATION_FIELD_ID}` | `Iteration field ID:` |
| `{STATUS_BACKLOG/READY/IN_PROGRESS/IN_REVIEW/DONE}` | option IDs from `Status options:` |

If no GitHub Project Integration section exists in CLAUDE.md, skip all project sync — TASKS.md is source of truth. If CLAUDE.md configures a different tracker (Linear etc.), adapt accordingly.

All operations are **best-effort** — append `|| true` and log failures without stopping.

## GraphQL Templates

### Get item ID (by issue number, via repository)
```bash
gh api graphql -f query="{
  repository(owner: \"{ORG}\", name: \"{REPO_NAME}\") {
    issue(number: {ISSUE_NR}) {
      projectItems(first: 5) { nodes { id project { number } } }
    }
  }
}" --jq ".data.repository.issue.projectItems.nodes[] | select(.project.number == {PROJECT_NUMBER}) | .id"
```

### Get item ID (by issue number, via organization — for issues not yet in project)
```bash
gh api graphql -f query='{
  organization(login: "{ORG}") {
    projectV2(number: {PROJECT_NUMBER}) {
      items(first: 200) { nodes { id content { ... on Issue { number } } } }
    }
  }
}' --jq ".data.organization.projectV2.items.nodes[] | select(.content.number == {ISSUE_NR}) | .id"
```

### Set status
```bash
gh api graphql -f mutation="mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: \"{PROJECT_ID}\" itemId: \"{ITEM_ID}\"
    fieldId: \"{STATUS_FIELD_ID}\"
    value: { singleSelectOptionId: \"{STATUS_OPTION_ID}\" }
  }) { projectV2Item { id } }
}" || true
```

### Add issue to project (returns item ID)
```bash
gh project item-add {PROJECT_NUMBER} --owner {ORG} \
  --url "https://github.com/{REPO}/issues/{NR}" \
  --format json | jq -r '.id'
```

### Set iteration
```bash
gh api graphql -f mutation="mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: \"{PROJECT_ID}\" itemId: \"{ITEM_ID}\"
    fieldId: \"{ITERATION_FIELD_ID}\"
    value: { iterationId: \"{ITERATION_ID}\" }
  }) { projectV2Item { id } }
}" || true
```

### List available iterations
Execute as two separate Bash calls — (1) `date +%Y-%m-%d`, then (2):
```bash
gh api graphql -f query="{
  organization(login: \"{ORG}\") {
    projectV2(number: {PROJECT_NUMBER}) {
      field(name: \"Iteration\") {
        ... on ProjectV2IterationField {
          configuration { iterations { id title startDate } }
        }
      }
    }
  }
}" --jq '.data.organization.projectV2.field.configuration.iterations[]'
```

### Add sub-issue to epic
```bash
gh api repos/{REPO}/issues/{EPIC_NR}/sub_issues \
  --method POST -H "X-GitHub-Api-Version: 2026-03-10" \
  -f sub_issue_id={TASK_ISSUE_GLOBAL_ID} || true
```

### Prioritize sub-issue (place after another)
```bash
gh api repos/{REPO}/issues/{EPIC_NR}/sub_issues/priority \
  --method PATCH -H "X-GitHub-Api-Version: 2026-03-10" \
  -f sub_issue_id={CURRENT_ID} -f after_id={PREVIOUS_ID} || true
```
