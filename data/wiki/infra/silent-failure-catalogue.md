---
title: Silent Failure Catalogue
tags: [infra, llm, reference]
summary: "A code-review checklist of the ways errors disappear — swallowed exceptions, fallbacks indistinguishable from empty, un-awaited promises, retries that exhaust without surfacing, default values filling absent data — organised around one question for every handler: who finds out, and how?"
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/sources/dotclaude-silent-failure-hunter.md
  - data/raw/claude-docs/galactus/skills/review-silent-failure/SKILL.md
  - data/raw/claude-docs/galactus/skills/fog/evals/fixtures/finds-planted-defects/expected.md
  - data/raw/repos/galactus/.claude--skills--fog--evals--fixtures--finds-planted-defects--expected.md
  - data/raw/claude-docs/galactus/skills/fog/evals/fixtures/finds-planted-defects/input/SPEC.md
  - data/raw/repos/galactus/.claude--skills--fog--evals--fixtures--finds-planted-defects--input--SPEC.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-18-ml-parity-consolidated.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-18-ml-parity-consolidated.md
  - data/raw/claude-docs/guacamayo/skills/review-silent-failure/SKILL.md
  - data/raw/repos/ai-project-template/.claude--docs--in-progress--genesis-dryrun--render-review.md
  - data/raw/repos/atlas/.claude--skills--new-agent--specs--cap-forecast.md
  - data/raw/claude-docs/akira/docs/reviews/2026-08-27-b41-operator-identity.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-08-27-b41-operator-identity.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-08-27-b41-operator-identity.md
  - data/raw/claude-docs/playground/docs/reviews/2026-08-27-b41-operator-identity.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-08-27-b41-operator-identity.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-08-27-b41-operator-identity.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-08-27-b41-operator-identity.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b39-operator-board.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b39-operator-board.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b39-operator-board.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b39-operator-board.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b39-operator-board.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b39-operator-board.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b39-operator-board.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-08-01-49-llm-starter-kit.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-08-01-49-llm-starter-kit.md
  - data/raw/claude-docs/ai-project-template/docs/plans/AIT-23-plan.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--AIT-23-plan.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis54-share-metadata.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis54-share-metadata.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis54-share-metadata.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis54-share-metadata.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis54-share-metadata.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis54-share-metadata.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis54-share-metadata.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis56-server-client-boundary.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis56-server-client-boundary.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis56-server-client-boundary.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis56-server-client-boundary.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis56-server-client-boundary.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis56-server-client-boundary.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis56-server-client-boundary.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis57-forms-server-actions.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis57-forms-server-actions.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis57-forms-server-actions.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis57-forms-server-actions.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis57-forms-server-actions.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis57-forms-server-actions.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis57-forms-server-actions.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis71-resultrationale-judge.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis71-resultrationale-judge.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis71-resultrationale-judge.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis71-resultrationale-judge.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis71-resultrationale-judge.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis71-resultrationale-judge.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis71-resultrationale-judge.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-15-dis271-batch-slice-limit.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-15-dis271-batch-slice-limit.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-15-dis271-batch-slice-limit.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-15-dis271-batch-slice-limit.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-15-dis271-batch-slice-limit.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis271-batch-slice-limit.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis271-batch-slice-limit.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis271-batch-slice-limit.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis271-batch-slice-limit.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis271-batch-slice-limit.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-15-dis271-batch-slice-limit.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-15-dis271-batch-slice-limit.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-15-dis226-telemetry-auth-hardening.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-15-dis226-telemetry-auth-hardening.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-15-dis226-telemetry-auth-hardening.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-15-dis226-telemetry-auth-hardening.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-15-dis226-telemetry-auth-hardening.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis226-telemetry-auth-hardening.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis226-telemetry-auth-hardening.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis226-telemetry-auth-hardening.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis226-telemetry-auth-hardening.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis226-telemetry-auth-hardening.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-dis144-langfuse-seam.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-dis144-langfuse-seam.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-dis144-langfuse-seam.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-dis144-langfuse-seam.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-dis144-langfuse-seam.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-dis340-audience-attribute.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-dis340-audience-attribute.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-dis340-audience-attribute.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-dis340-audience-attribute.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-dis340-audience-attribute.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis386-retrieval-foundation.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis386-retrieval-foundation.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis386-retrieval-foundation.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis386-retrieval-foundation.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis386-retrieval-foundation.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-24-dis386-retrieval-foundation.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-24-dis386-retrieval-foundation.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-24-dis386-retrieval-foundation.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-24-dis386-retrieval-foundation.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-24-dis386-retrieval-foundation.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis73-occurrence-remaining.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis73-occurrence-remaining.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis73-occurrence-remaining.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-15-dis73-occurrence-remaining.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis73-occurrence-remaining.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis73-occurrence-remaining.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-15-dis73-occurrence-remaining.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-16-dis275-human-label-persistence.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-16-dis275-human-label-persistence.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-16-dis275-human-label-persistence.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-16-dis275-human-label-persistence.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-16-dis275-human-label-persistence.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-16-dis276-pipeline-health-check.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-16-dis276-pipeline-health-check.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-16-dis276-pipeline-health-check.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-16-dis276-pipeline-health-check.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-16-dis276-pipeline-health-check.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-16-pr306-stacked-issues.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-16-pr306-stacked-issues.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-16-pr306-stacked-issues.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-16-pr306-stacked-issues.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-16-pr306-stacked-issues.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-17-pr320-batched-review.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-17-pr320-batched-review.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-17-pr320-batched-review.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-17-pr320-batched-review.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-17-pr320-batched-review.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-18-batched-288-299-303-304.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-18-batched-288-299-303-304.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-18-batched-288-299-303-304.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-18-batched-288-299-303-304.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-18-batched-288-299-303-304.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-18-dis249-dis288-quality-signals.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-18-dis249-dis288-quality-signals.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-18-dis249-dis288-quality-signals.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-18-dis249-dis288-quality-signals.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-18-dis249-dis288-quality-signals.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-19-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-19-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-19-dis289-relevance-benchmark-corpus.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-19-dis289-relevance-benchmark-corpus.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-19-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-19-pr342-fp16-poll-list.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-19-pr342-fp16-poll-list.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-19-pr342-fp16-poll-list.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-19-pr342-fp16-poll-list.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-19-pr342-fp16-poll-list.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-20-dis343-venue-open-facts.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-20-dis343-venue-open-facts.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-20-dis343-venue-open-facts.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-20-dis343-venue-open-facts.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-20-dis343-venue-open-facts.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-21-dis355-a1-detail-places-similar.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-21-dis355-a1-detail-places-similar.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-21-dis355-a1-detail-places-similar.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-21-dis355-a1-detail-places-similar.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-21-dis355-a1-detail-places-similar.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-21-pr356-dis353-feed-review-followup.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-21-pr356-dis353-feed-review-followup.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-21-pr356-dis353-feed-review-followup.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-21-pr356-dis353-feed-review-followup.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-21-pr356-dis353-feed-review-followup.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-22-dis309-tester-journey-attribution.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-22-dis309-tester-journey-attribution.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-22-dis309-tester-journey-attribution.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-22-dis309-tester-journey-attribution.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-22-dis309-tester-journey-attribution.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-22-dis362-pipeline-harness-card-extract-qc.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-22-dis362-pipeline-harness-card-extract-qc.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-22-dis362-pipeline-harness-card-extract-qc.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-22-dis362-pipeline-harness-card-extract-qc.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-22-dis362-pipeline-harness-card-extract-qc.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-23-dis372-dis374-evidence-stage-data-platform.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-23-dis372-dis374-evidence-stage-data-platform.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-23-dis372-dis374-evidence-stage-data-platform.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-23-dis372-dis374-evidence-stage-data-platform.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-23-dis372-dis374-evidence-stage-data-platform.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-25-dis-403-406-venue-publish-lifecycle.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-25-dis-403-406-venue-publish-lifecycle.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-25-dis-403-406-venue-publish-lifecycle.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-25-dis-403-406-venue-publish-lifecycle.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-25-dis-403-406-venue-publish-lifecycle.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-25-dis214-six-issue-batch.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-25-dis214-six-issue-batch.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-25-dis214-six-issue-batch.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-25-dis214-six-issue-batch.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-25-dis214-six-issue-batch.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-27-pr412-post-merge.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-27-pr412-post-merge.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-27-pr412-post-merge.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-27-pr412-post-merge.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-27-pr412-post-merge.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-28-pr413.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-28-pr413.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-28-pr413.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-28-pr413.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-28-pr413.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-28-pr415.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-28-pr415.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-28-pr415.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-28-pr415.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-28-pr415.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-29-dis416-venue-priority-wiring.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-29-dis416-venue-priority-wiring.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-29-dis416-venue-priority-wiring.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-29-dis416-venue-priority-wiring.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-29-dis416-venue-priority-wiring.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-30-dis358-quality-verdicts-dashboard-monitoring.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-30-dis358-quality-verdicts-dashboard-monitoring.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-30-dis358-quality-verdicts-dashboard-monitoring.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-30-dis358-quality-verdicts-dashboard-monitoring.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-30-dis358-quality-verdicts-dashboard-monitoring.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-15-lending-parity.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-15-lending-parity.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-16-fraud-parity.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-16-fraud-parity.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-06-dis54-share-metadata.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-06-dis54-share-metadata.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-06-dis54-share-metadata.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-06-dis54-share-metadata.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-06-dis54-share-metadata.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-06-dis54-share-metadata.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-06-dis54-share-metadata.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-06-dis56-server-client-boundary.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-06-dis56-server-client-boundary.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-06-dis56-server-client-boundary.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-06-dis56-server-client-boundary.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-06-dis56-server-client-boundary.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-06-dis56-server-client-boundary.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-06-dis56-server-client-boundary.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-06-dis57-forms-server-actions.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-06-dis57-forms-server-actions.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-06-dis57-forms-server-actions.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-06-dis57-forms-server-actions.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-06-dis57-forms-server-actions.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-06-dis57-forms-server-actions.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-06-dis57-forms-server-actions.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-07-dis185-saved-read-path.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-07-dis185-saved-read-path.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-07-dis185-saved-read-path.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-07-dis185-saved-read-path.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-07-dis185-saved-read-path.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-07-dis185-saved-read-path.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-07-dis185-saved-read-path.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-07-dis60-lighthouse-ci.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-07-dis60-lighthouse-ci.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-07-dis60-lighthouse-ci.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-07-dis60-lighthouse-ci.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-07-dis60-lighthouse-ci.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-07-dis60-lighthouse-ci.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-07-dis60-lighthouse-ci.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-06-dis168-skip-link-targets.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-06-dis168-skip-link-targets.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-06-dis168-skip-link-targets.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-06-dis168-skip-link-targets.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-06-dis168-skip-link-targets.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-06-dis168-skip-link-targets.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-06-dis168-skip-link-targets.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis266-env-guard-a3.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis266-env-guard-a3.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis266-env-guard-a3.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis266-env-guard-a3.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis266-env-guard-a3.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-07-dis46-restore-drill.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-07-dis46-restore-drill.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-07-dis46-restore-drill.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-07-dis46-restore-drill.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-07-dis46-restore-drill.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-07-dis46-restore-drill.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-07-dis46-restore-drill.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-10-pr235-catalogue-and-source-rights.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-10-pr235-catalogue-and-source-rights.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-10-pr235-catalogue-and-source-rights.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-10-pr235-catalogue-and-source-rights.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-10-pr235-catalogue-and-source-rights.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-10-pr235-catalogue-and-source-rights.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-10-pr235-catalogue-and-source-rights.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-08-dis202-batch-enrichment.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-08-dis202-batch-enrichment.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-08-dis202-batch-enrichment.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-08-dis202-batch-enrichment.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-08-dis202-batch-enrichment.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-08-dis202-batch-enrichment.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-08-dis202-batch-enrichment.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-11-dis158-relative-image-urls.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-11-dis158-relative-image-urls.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-11-dis158-relative-image-urls.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-11-dis158-relative-image-urls.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-11-dis158-relative-image-urls.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-11-dis158-relative-image-urls.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-11-dis158-relative-image-urls.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis263-accepted-candidate-bridge.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis263-accepted-candidate-bridge.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis263-accepted-candidate-bridge.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis263-accepted-candidate-bridge.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis263-accepted-candidate-bridge.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-02-b41-partner-table.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-02-b41-partner-table.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-02-b41-partner-table.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-02-b41-partner-table.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-02-b41-partner-table.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-02-b41-partner-table.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-02-b41-partner-table.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-04-dis142-redistribution-posture.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-04-dis142-redistribution-posture.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-04-dis142-redistribution-posture.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-04-dis142-redistribution-posture.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-04-dis142-redistribution-posture.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-04-dis142-redistribution-posture.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-04-dis142-redistribution-posture.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-03-round2-dis55-dis59.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-03-round2-dis55-dis59.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-03-round2-dis55-dis59.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-03-round2-dis55-dis59.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-03-round2-dis55-dis59.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-03-round2-dis55-dis59.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-03-round2-dis55-dis59.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-03-dis40-scheduled-ingestion.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-03-dis40-scheduled-ingestion.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-03-dis40-scheduled-ingestion.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-03-dis40-scheduled-ingestion.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-03-dis40-scheduled-ingestion.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-03-dis40-scheduled-ingestion.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-03-dis40-scheduled-ingestion.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis265-activity-date-range.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis265-activity-date-range.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis265-activity-date-range.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis265-activity-date-range.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis265-activity-date-range.md
  - data/raw/repos/librarian/.claude--docs--CHANGELOG.md
---

# Silent Failure Catalogue

An externally-sourced agent definition (medium confidence) that the galactus repo kept as
a reference for its review dimensions. Its value is the enumeration; the organising
question is the same one [[Collapse Site Detection]] asks of designs.

## The catalogue

| Class | Shape | Tell in code |
|---|---|---|
| Swallowed exception | `except: pass` / `except Exception: continue` / log at debug and proceed | the handler has no caller-visible effect |
| Fallback indistinguishable from empty | `.get(key, [])`, `or {}`, `return None` on failure | the caller cannot tell "nothing" from "failed" |
| Floating promise | async call without `await`/`.then`/error handler | the rejection is lost to the event loop |
| Retry exhaustion | loop retries N times then falls through | nothing after the loop checks whether it succeeded |
| Default filling absence | config/env default applied without logging that the real value was missing | the system runs on a value nobody set |
| Catch-and-rethrow-as-generic | wrapping a specific error in `RuntimeError("failed")` | the cause is gone; the caller matches on nothing |
| Partial success reported as success | batch of 100, 7 failed, return `ok` | aggregate hides per-item outcome |
| Health check that cannot fail | liveness only, no readiness/divergence | the monitor is a detector for the wrong thing |

## The one question

For every handler: **who finds out, and how?** If the answer is "the logs, if someone
reads them", the failure is silent for operational purposes. The catalogue's remediation
is uniform — surface to the caller as a typed error or an explicit abstention, never as a
value that could also mean success.

## Relation to the planted-defect eval

The fog skill's behavioural eval plants four of these classes (swallowed `continue`,
empty-match skipping a send, a migration dropping a column a backfill needs, liveness-only
monitoring) alongside three **negative controls** that word-match the catalogue but are
correct (a typed `Ok | Unavailable` return, a unique-constraint pre-send, a hard-coded
character cap). The controls exist because a catalogue like this one, applied by grep
alone, over-fires — see [[Collapse Site Detection]] on scoring precision separately.

## Additions from the galactus review-silent-failure dimension

The galactus dimension extends the catalogue with two classes:

- **Gates without checks.** A gate whose pass/fail depends on an artifact nobody wrote turns
  CI red on *absence* rather than *defect*, and the only fix is to disable it. Write the
  graders first, then enable the gate (see [[Always-Red Check Carries No Signal]]).
- **Silent disagreement with live state.** "An instrument that disagrees with reality and
  says nothing invalidates every row it certifies":
  - `CREATE … IF NOT EXISTS` checks the **name**, not the definition. It is an optimistic
    skip, not a verification.
  - A version-keyed migration or drift map silently evicts a duplicate version, which is
    then reported neither applied nor missing.
  - RLS with no anon select policy returns zero rows that read as "no data" rather than
    "no permission."
  - A numeric budget with nothing measuring it can only be enforced by accident.

It also lists what *not* to flag: commented intentional suppression, best-effort paths that
say so (cache warm-up, analytics), errors handled by a caller you actually read, and
logging-level debates where the error does surface somewhere actionable.

## Additions from template dry-runs (ai-project-template, atlas)

- **Optional-import guard around a mount.** `try: from .integrations import router … except
  ImportError: pass` meant a render without the router file started cleanly, passed its
  health check, and silently lacked the project's headline feature. Guard on the *toggle*,
  not on whether the import succeeds, so a missing file under an enabled toggle fails loudly.
- **The fallback path imports late.** A forecast pipeline's naïve seasonal fallback used
  `math.ceil`, but `math` was imported inside the primary model's `try` block. The fallback
  runs exactly when the primary is unavailable, which is exactly when that import never
  happened. Imports a fallback needs belong at module level. The general form: the
  degraded path is the least-run path, so it must not depend on the healthy path's side
  effects.

## Additions from akira plan reviews (2026-08)

- **Null with two meanings at a swap seam.** A resolver typed `Record | null`, whose
  callers render "link no longer exists" on null, is honest while it is backed by an
  in-memory fixture. Once a database backs it, a timeout returning null shows a dead link
  for an operator who exists. The review downgraded the finding, because this diff had
  no I/O path that could produce it, and recorded it against the item that owns the swap
  ([[Async Seam Before the Table]]).
- **Output that looks correct and does nothing.** A QR board rendered from `localhost`
  produces a perfect-looking code that no phone can reach. A docs note does not cover
  this. It needs a visible dev-only warning in code
  ([[Printed URL Is a Public Contract]]).

## Additions from template starter-kit and CI plans (ai-project-template)

- **A warning wired to the wrong variable is unreachable.** A chat span warned on
  truncation by comparing its `finish_reason` *parameter* — which callers left at its `""`
  default — while the real stop reason arrived later via `set_attribute`. The warning could
  never fire. Fix: a helper that records the reason and the check reads the recorded value.
- **An empty string is a silent failure.** A `generate()` helper returned `""` when the
  model produced no text block, indistinguishable from a legitimate empty answer.
- **A keyword-grep lint proves consideration, not emission.** An SDK lint check passed
  because the file contained the literal token-usage field names — in `print()` calls. It
  verified the concept was mentioned, not that a consumable record was emitted.
- **`workflow_call` swaps the event context.** In a reusable workflow, `github.event` and
  `github.actor` belong to the *caller's* run, so a `github.actor == 'dependabot[bot]'`
  gate silently evaluates false and the job skips green. Pass what you need explicitly
  (e.g. an `inputs.pr_url`).
- **A context manager entered and never exited.** A checkpointer factory called
  `PostgresSaver.__enter__()` to get a long-lived saver and never called `__exit__`, leaking
  the connection pool at shutdown. Keep the `lru_cache` singleton and register the exit
  with `atexit`.

## Additions from akira share-metadata plan (2026-09)

- **A must-not-fail route that discarded the error.** An Open Graph image route must never
  return 500 for a share unfurl, so it renders a generic fallback card when the record is
  missing. It destructured only `data` from the lookup, so a real database failure looked
  exactly like an ordinary not-found and was never logged. The fix: keep the fallback in both
  cases, and log whenever the error code is anything other than the store's "no rows" code
  (PostgREST `PGRST116` for `.single()`). Degrade the response, not the observability.
- **An allowlist comment that justified more than was true.** A lint-exception comment said
  all six hex literals matched design tokens "by value". Only two did; the other four were
  brand-gradient colours from the icon file. An exception's stated reason is a claim to be
  verified like any other.

## Additions from akira frontend and eval plans (2026-09)

- **Degrade-to-empty with no log line.** A server-resolved loader that returns `[]` on a
  query error keeps the render path from throwing. When it also drops `error`, an outage
  looks exactly like a user with no data. Two review rounds found the same thing three
  times: a profile query, a saved-ids loader, and auth Server Actions that swallowed
  email-send errors. The fix was the same each time: log the error and return the same
  safe value. For auth, that keeps the no-enumeration response byte-identical
  ([[Server Shell, Client Leaf]]).
- **Null-on-any-error hides a provider schema rejection.** A judge base class returned
  `null` on any call or parse error. Its first real use graded zero of ten fixtures,
  because the strict structured-output API rejected the shared schema. The run read as
  "judges skipped" ([[Positive-Only Judge Fixtures Measure Recall]]).

## Additions from akira slicing and telemetry plans (2026-09)

- **An implicit API row cap read as "everything".** Selects with no `.range()` were
  capped at PostgREST's default `db-max-rows` (1000). Below the cap nothing shows. Above it,
  an "already enriched" lookup comes back partial and already-enriched rows get
  re-submitted. Paginate explicitly and test the page-2 error path, because a swallowed
  error there returns a partial set as complete
  ([[Bounded Slice After In-Memory Eligibility]]).
- **A sink that hides rejection hides wiring regressions too.** A beacon sink that answers a
  forged id with the same `202 {recorded: 0}` as a capacity drop is right for security. But
  a client refactor that sends the wrong field then fails silently, and call-count tests stay
  green. Assert the payload ([[Indistinguishable Rejection on Best-Effort Sinks]]).

## Additions from akira telemetry and enrichment-attribute plans (2026-09-21)

- **`process.exit()` in a catch skips a chained flush.** Telemetry flushed in `.finally()`
  never ran on the error path, so failed runs lost their traces. Set `process.exitCode`
  and return instead ([[A Trace Is Not a Number of Record]]).
- **A runtime schema strips the column you just selected.** A new enrichment column was
  added to the served-path `select`, but the boundary zod `z.object` did not list it.
  `z.object` drops unnamed keys, so every real read would have silently delivered
  `undefined` to the scorer. Found only by tracing the value through to the scoring
  candidate. Adding a field means adding it to every boundary parser on its path, not just
  the query.
- **Grader-local fixture builders miss a new required field.** Adding the field to the
  vocabulary's required list broke two eval graders that hand-built their own "valid
  payload" literals, separate from the unit-test builders that had been updated. The
  previous attribute had hit the identical miss. Grep for every hand-rolled valid-payload
  literal when a required field is added
  ([[Every Column Names Its Reader]]).

## Additions from akira measurement and retrieval plans (2026-09-24)

- **A read-side schema drops the new field.** A comparison tool's own row schema did not
  declare a new output field, the parser stripped it, and the tool reported 0 yield over
  populated data ([[Read-Side Schema Strips the New Field]]).
- **A paid backfill throws away paid work.** Embed-everything-then-write lost every
  embedding after the first failed insert, and the CLI exited 0 with failures
  ([[Persist Paid Work Per Chunk]]).
- **`create or replace` leaves the old function behind.** Adding defaulted parameters
  created an overload rather than widening the function
  ([[Widening a Postgres Function Creates an Overload]]).
- **A JSON parse failure swallowed into `undefined`** on a client-supplied field, with no
  log. Review marked it moot once the field was removed in favour of a server-verified token.

## Additions from galactus ml-parity plans (2026-08)

- **A gitignore rule over a tracked file is a false assurance.** A copyrighted third-party
  brief had an ignore rule with a comment explaining why it must not be committed. The file
  was already tracked, and ignore rules do not affect tracked files. The fix is
  `git rm --cached` as a separate change. Until it lands, no doc may claim the file is
  ignored.
- **A skip that reads as a pass.** A test skip predicate gated on an env var hid 14 tests
  across the seam a plan was built on ([[Skip Keyed on Config, Not Capability]]).
- **`git revert` restores the writer, never the published numbers.** A committed results
  directory with two write paths (an enforcing helper and an older advisory one) makes
  "independently revertible" false. The fix was to route every writer through one enforcing
  chokepoint, hash the outgoing gitignored data file before replacing it, and add new data
  beside the old file rather than over it. Any step that publishes a real record needs its
  own decision.
- **A rollback that covers the wrong path.** In the planted-defect spec, a send-time feature
  flag is offered as "our rollback". It stops future sends and does nothing for a column
  dropped in the same release.

## Additions from akira code reviews (2026-09-15 to 09-30)

Recurring defect classes across about thirty multi-reporter code reviews. Individual findings
are omitted; each bullet appeared in at least one review and most in several.

- **The dropped Supabase `error`.** `const { data } = await ...` with `error` never captured,
  so an outage reads as empty, not-found or not-saved. It recurred in at least seven reviews,
  including a privacy data export that returned 200 with one section silently empty and a page
  that rendered a 404 on a read failure. One branch needed three review rounds and still ended
  at the round limit. Two lessons the reviews wrote down: *an existing unflagged copy of the
  pattern is not evidence it is acceptable*, and *fail-closed does not stop a read failure
  rendering as "no data"*.
- **Partial failure counted as success.** QC prepare/write errors counted as "evaluated"; a
  single-item CLI exited 0 on a write error; a backfill printed "write complete" after per-row
  failures; a mirror-write failure flag reached no caller or summary.
- **One transient read error aborts the rest of a batch.** Catch per item, record it as failed,
  continue, and keep the backlog resumable ([[Persist Paid Work Per Chunk]]).
- **A chained phase opens a fresh budget.** A QC phase run after enrichment created its own
  spend ledger and so got a second full per-run token ceiling; another CLI looped billed calls
  with no ledger at all. Pass one ledger through the whole run
  ([[Budget Without a Meter Is a Preference]]).
- **Lenient parsers in tooling** — vacuous thresholds, unknown ids accepted, `NaN` limits
  ([[Strict Parsers for Alarm Config]]).
- **Unpaged or wrongly paged reads** under PostgREST's silent 1000-row cap
  ([[Page on a Total Order]]).
- **Quarantine fails open.** Malformed rows dropped with one warn and no ratio escalation;
  escalate to error above a threshold and surface the count in the pool diagnostic.
- **A floating `void` promise.** Its rejection escapes both the logger and the surrounding
  try block, and Node may terminate on an unhandled rejection.
- **A Postgres `do instead nothing` rule** turns a loud permission error into a silent 0-row
  success ([[Do-Instead-Nothing Rule Silences a Loud Denial]]).
- **A documented invariant that is false.** A migration header claimed rows were "invisible by
  construction" when only ordering plus a `.limit(200)` hid them; "eligible is a superset of
  placed, by construction" was false because eligibility was capped like placement (fix: union
  the actual placement into the set); a privacy page promised a "complete" trace while one
  surface was never tagged (fix: list it as a completeness limitation rather than widen
  collection); a test whose name asserted the opposite of its body.
- **A governance cross-check that could never go green** — 147 ids defined, 2 backfilled — and a
  header whose reasoning was backwards.
- **A missing aggregation key read as 0.** An absent key for a venue meant "every edge is thin",
  not "zero underserved edges"; defaulting to 0 inverted the priority order.
- **A meaning change with no reader update.** A one-click reject began writing a verdict with an
  empty defect list, which the report then counted as a legacy-format defect.
- **Polymorphic references escape delete guards and foreign keys**, so an assigned-but-unrated
  item could still be deleted.
- **Removing the last dated occurrence leaves stale parent dates** on the parent record.
- **Server Action auth relying on the proxy path matcher.** Next.js resolves an action by its
  `Next-Action` id from any path, so the admin check must live inside the action, sharing one
  pure helper with the proxy.
- **Triggers, CHECKs and advisory locks never executed** because tests mocked the RPC; add a
  real-Postgres integration test including two concurrent writers
  ([[Live-Database Test Harness Hazards]]).
- **RLS gates rows, not columns.** Sensitive note and email columns sat on an anon-readable
  table.
- **An expression index used only for an identical expression.** The query called
  `array_to_string`, the index was on an immutable wrapper, so it seq-scanned. The same query
  `greatest()`-combined an unbounded `ts_rank_cd` with a 0-1 `similarity()`; normalization 32
  fixed the scale.
- **`host.endsWith(rule.host)`** matches `notexample.org` for `example.org`; use
  `host === rule.host || host.endsWith('.' + rule.host)`.
- **A JSON round-trip defeats `!==` self-exclusion.** Every fixture matched itself, producing a
  0.000 to 1.000 jump that looked like tuning; rejected as leakage.
- **Co-fitting.** Heuristic rules designed by reading the corpus the holdout is drawn from; a
  threshold selected on the very sample it gates; baseline rates computed over tune and holdout
  together ([[Write-Time Deterministic Holdout]]).
- **Community-edited text reaches the prompt uncapped.** Cap length and strip markup at parse
  time.
- **Raw account UUIDs in logs or interaction tables**, against a salted-pseudonym rule and with
  no retention path ([[Study-Scoped Pseudonymous Attribution]]).
- **Two non-atomic writes (supersede, then insert).** Acceptable once, where it self-healed,
  failed closed and was the only order a partial unique index permitted; elsewhere fixed with an
  RPC transaction.
- **A withdrawal races an in-flight write.** A foreign-key violation surfaced as a 503; the fix
  was a narrow retry with a null reference, only when `error.code === '23503'` and the message
  names the column.
- **Gates blind to what is unpushed.** A function-grants gate passed without checking the new
  functions; a schema probe covered two tables but not the new ones, and its join discarded
  `error.message` ([[Migration Done Means Pushed and Probed]]).
- **Budget ratchets absorbed on first use.** "An over-budget file may not grow" let a file grow
  531 to 641 lines in the commit that wrote the rule; table-count budgets were repeatedly not
  re-baselined.
- **Wrong-direction import with no lint guard.** The first `agents/` to `core/` import passed
  because the restricted-imports rule was scoped only to `core/`.
- **Smaller recurring items:** a pushed migration edited in place; a guardrail kept as a comment
  rather than converted to a grep test ([[Single-Definition Grep Guard]]); a synchronous
  `JSON.stringify` in the render path for instrumentation (move it into `after()`); a lockfile
  out of sync after a dependency bump; a test-harness truncate list missing new tables; a
  one-off service-role script committed at the repo root.


## Additions from galactus ML parity plans (2026-08)

Review findings on ML prototype runs being brought up to the [[ML Run Reproducibility Bar]]:

- **A catch-all "toolkit available" probe skips a broken tree as green.** The availability
  check caught every exception, so a configured-but-broken toolkit path produced the same
  pass/skip counts as a healthy checkout with no toolkit. Skip only on the specific
  condition you sanctioned (the variable is *unset*), and let everything else fail.
- **A false skip-reason string propagates.** One test's skip reason claimed a directory
  "holds only stale `__pycache__`". The real cause was a missing `"."` in pytest's
  `pythonpath`. A plan copied the reason as fact. One config line gave 38 passed and 0
  skipped.
- **`getattr(metrics, "roc_auc", None)` disarms an alarm silently.** Combined with
  per-model `None` tolerance, an upstream rename maps every model to `None`, and the
  final-metric alarm checks nothing while the run exits 0. Read defensively, then
  **reject `None` at record assembly**.
- **A property-to-method change, stored uncalled, serializes a repr.** Upstream turned
  `beats_baseline` from a property into a method. The summary stored the bound method, and
  `default=str` wrote its repr. The run's headline honesty question could no longer be
  answered from its own artifact. Make the writer raise on non-serializable values rather
  than coercing them.
- **An unresolved `Path` comparison let a dry run overwrite a tracked fixture.** A
  relative path and the default path compared unequal although `.resolve()` showed the same
  file. A synthetic dry run would have overwritten a real report that 17 tests use as
  ground truth. Compare resolved paths.
- **"Closed" is not "merged".** An upstream issue was closed while its branch was
  unmerged, so a reader rendering from `main` got no module and died at import. No doc
  named the branch.

## Additions from akira code reviews (2026-09-05 to 09-15)

Defect classes from the earlier review wave that the section above does not already name.

- **A function goes silent when a second caller moves it onto the render path.** An
  unchanged read helper that returned `[]` on a dropped `error` was harmless behind an API
  route, where a failure was a visible failed request. A new server-page caller turned the
  same failure into "you have saved nothing". Re-check a helper's error contract whenever a
  diff adds a caller in a different failure context.
- **Correct swallow, missing log.** Account actions bound by a no-enumeration contract must
  always resolve success, so swallowing the database error is right, but swallowing it with
  no `logger.error` makes a real outage invisible to operators too. The fix logged and kept
  the contract.
- **An unguarded browser-storage write before navigation.** `sessionStorage.setItem(...)`
  immediately before `router.push(...)` throws when storage is disabled, navigation never
  happens, and the user is stuck with no error.
- **A raw error string serialized to the browser through a client prop.** A server page passed
  `error.message` to a `'use client'` component that only tested it for truthiness. It never
  rendered, but Next.js serializes every client prop into the RSC payload, so a PostgREST
  message naming the failing table and column sat in the page source. "In the page source"
  and "on screen" are different bars. Pass a boolean instead.
- **CI upload silently drops a dot-directory.** `actions/upload-artifact` v4+ defaults
  `include-hidden-files: false`, so a `.lighthouseci` results folder never reached the
  artifact.
- **A secret's trailing newline swallowed a shell `\` continuation.** An interpolated secret
  ended in a newline, so the rest of a `VAR=... \` prefix chain was cut and `next start` ran with
  no environment; only the routes using the admin client 500'd. Moving the vars into a YAML
  `env:` block plus a non-empty guard fixed it.
- **`2>&1` merges stderr into a captured value.** Makefile recipes captured a project ref with
  `ref="$(... 2>&1)"`, so any Node or npx deprecation warning would turn the ref into several
  lines. Capture stdout only, let the reason reach the terminal on stderr, and have the printer
  fail closed unless the value matches the expected shape.
- **Collapsed outcomes in a drill script.** `2>/dev/null || echo UNKNOWN` then exit 0 merged
  "feature genuinely off", "API rejected the call" and "network failure" into one benign line,
  and nothing tested that a failed verdict reached the CLI's exit code, so an inverted exit would
  have passed ([[Restore Drill: Rebuild-from-Migrations Visibility Probe]]).
- **A malformed 200 page reads as the last page.** `totalCount = body.data?.totalCount ??
  rawEvents.length` plus `if (rawEvents.length === 0) break` turned a proxy or maintenance body
  without `data` into a clean end of pagination. The truncated count fed a measurement used to
  pick an ingestion segment, so the failure produced a confidently wrong recommendation.
  Distinguish "no data key" from "empty array", or check pages fetched against the total.
- **RLS with no policy returns an empty set, not an error.** A new read path built on the anon
  client queried a table that had RLS enabled and no policy, so every request quietly took the
  legacy fallback ([[Written-but-Inert RLS Policies]]).
- **An optional dependency no caller passes.** `options.ledger?.record(...)` was a permanent
  no-op because the only production caller passed two arguments, so batch spend was recorded
  nowhere while the plan promised a run summary.
- **Coercion that turns detectable garbage into plausible garbage.** `String(image)` on a
  schema.org ImageObject produced `"[object Object]"`, which a relative-URL detector used to
  flag. A new resolver then turned it into `https://<venue>/event/[object%20Object]`, an
  absolute URL on an allowed host, and the only check that could see it went quiet. The same
  resolver passed `javascript:`, `data:` and `file:` URLs through unchanged; resolve to
  `undefined` unless the protocol is `http:` or `https:`.
- **A call-recording fake hides column and filter errors.** A fake Supabase client whose filter
  methods are passthroughs and which ignores `.select(...)` column lists lets a wrong column name
  pass every test and fail in production ([[A Fake That Conforms to a Broken Seam]]).
- **A guard that fails open on a read error.** Pre-insert duplicate checks destructured only
  `data`, so `(null?.length ?? 0) > 1` was false and the insert proceeded unchecked. Fail closed
  on the read, and page the read with `.order('id')` before `.range()`
  ([[Bounded Slice After In-Memory Eligibility]]).
- **A NaN safety ceiling.** `Number(flagValue('max-rows') ?? 500)` turned `500x` into `NaN`,
  and `count > NaN` is always false, so a typo disabled the row ceiling on an irreversible
  archive sweep. Four review dimensions raised it independently. Parse limit flags as
  positive integers and exit before any read or write when the value is not one.

## Additions from akira review rounds (2026-09-02 to 09-05)

- **Query error folded into "not found".** `if (error || !data) return null` made a
  transient DB error, or a table that had not been pushed yet, render a real partner's QR
  code as "this code is no longer active". The fix was to throw on `error` before the
  empty check, so an unknown code still returns null. Two sibling data sources already
  threw. **Check new code against its closest siblings' error convention.**
- **Loud but not diagnosable.** The round-2 throw had no log line and no `error.tsx`
  anywhere. Round 3 added a log line before every throw naming the operation and the
  key, so one bad code can be told apart from an outage. It also added a once-per-process
  schema diagnosis naming the missing migration. **The once-only gate wraps only the extra
  diagnosis, never the per-call line,** so a second, different failure is never suppressed.
- **`console.*` is not a sink.** A degraded join (a posture chunk query failing) logged
  with `console.warn`, but only the structured logger is read in production. Once the
  default-deny filter is on, an incomplete join and a genuine "not approved" give the
  same outcome with no record of which it was. Use the logger at error level, with the
  failed and total counts as structured fields. The `no-console` lint rule was scoped to
  page files. A follow-up review *measured* the gap (4 remaining calls, all in route
  handlers) and filed it rather than widening the rule mid-branch.
- **An allowlist that fails by not rendering.** An image optimizer that allowed any HTTPS
  host was an SSRF exposure. But narrowing it to a static allowlist (13 hosts at the time)
  breaks every new source silently, because a disallowed host just fails to render. On a
  catalogue that is still growing, that trade-off belongs to the owner, not to a review
  fix.
- **Removing a variable disables its other readers.** A fix instruction said to stop
  setting a run-id env var in the workflow. A shutdown handler read that same variable
  directly, so following the instruction literally would have silently disabled the
  SIGTERM handler added the round before. The fix agent caught it. The handler now reads
  the in-memory run id first. **Grep every reader of a variable before deleting its
  writer.** See [[The Run Record Belongs to the Process]].
- **A dispatch scope that omits a plan step looks like a silent-failure finding.** Round
  1 scoped the fix agent to two files and left out the operator-dashboard step. The
  reviewers then flagged that a daily spend-cap hit was indistinguishable from success,
  because CI emails only on failure. The lane was widened.

## See Also
- [[Collapse Site Detection]] — alternative-to (design-time vs code-review-time hunt for the same class)
- [[Silent Fallthrough in String-Keyed Discovery]] — instance-of
- [[Hydration Gap Silent Input Loss]] — instance-of
- [[Production Hardening Patterns]] — extends
- [[Prototype Hardening Pass]] — extends (a pre-demo walk over these classes)
- [[Always-Red Check Carries No Signal]] — extends
- [[Layered Ingestion Failure Posture]] — extends (STALE_SUCCESS, per-field validity floors, fail-closed empty builds)
- [[A Check Must Say Why It Could Not Check]] — extends (an undiagnosed red is the dual of a silent green)
- [[Settings Field Names Are a Shared Env Namespace]] — extends
- [[In-Band Stream Errors Read as Bad Answers]] — instance-of
- [[Printed URL Is a Public Contract]] — extends (the invisible-failure QR guard)
- [[Gate Dependabot Auto-Merge on Branch Protection]] — related (the workflow_call actor gate)
- [[Rate-Limit Keying: Identity Over IP]] — related (limited vs write-failed told apart only by log level)
- [[Server Shell, Client Leaf]] — related (degrade-to-empty loaders that dropped the error)
- [[Positive-Only Judge Fixtures Measure Recall]] — related (null-on-error judge contract)
- [[Empty-String Env Override Defeats Nullish Coalescing]] — related (an empty env var read as configured by `??`)
- [[Transactional Email Sender Setup]] — related (DKIM misalignment and auth-mail throttling fail into the spam folder, not an error)
- [[Branch Gated on State Only It Writes]] — instance-of (a conditional branch whose precondition only it could write)
- [[Read-Side Schema Strips the New Field]] — instance-of
- [[Skip Keyed on Config, Not Capability]] — instance-of (a skipped test reads as a pass under `-q`)
- [[Persist Paid Work Per Chunk]] — instance-of
- [[Widening a Postgres Function Creates an Overload]] — instance-of
- [[Strict Parsers for Alarm Config]] — instance-of
- [[Page on a Total Order]] — instance-of
- [[Do-Instead-Nothing Rule Silences a Loud Denial]] — instance-of
- [[A Constraint Cannot Tell a Regression From a Legacy Null]] — related
- [[Audit-Don't-Assert Release Checklist]] — extends (true/false/error rows refuse to fold an unrun check into a pass)
- [[Freshness Key Blind to Content Semantics]] — instance-of (a persisted index whose rebuild check misses builder changes, then search falls back silently)
- [[Closed-Vocabulary Parser Silently Drops Invented Types]] — instance-of
- [[Native Library Load-Order Collision]] — instance-of
