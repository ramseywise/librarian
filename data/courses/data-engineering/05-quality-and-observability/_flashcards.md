---
generated_by: tools/slides/flashcards.py
decks:
- data-engineering/05-quality-and-observability/slides/deck.yaml
cards:
- front: Why plant synthetic faults in a feed?
  back: Synthetic faults let us score every check against what really happened.
  lesson: data-engineering/05-quality-and-observability/notes/01-quality-dimensions-and-tests
- front: Which dimension can no query on the table alone ever test?
  back: Each dimension needs more context than the last, and accuracy needs something outside the table.
  lesson: data-engineering/05-quality-and-observability/notes/01-quality-dimensions-and-tests
- front: What happens to a hard rule on a soft fact?
  back: A hard rule on a soft fact gets muted, and then it cannot catch the day that matters.
  lesson: data-engineering/05-quality-and-observability/notes/01-quality-dimensions-and-tests
- front: When do you use dbt for data tests, and how many homes should a rule have?
  back: Use dbt when the model lives in dbt and keep one home per rule so rules do not drift.
  lesson: data-engineering/05-quality-and-observability/notes/01-quality-dimensions-and-tests
- front: What does write-audit-publish do that a report afterwards cannot?
  back: Write-audit-publish stops bad data before it is read, rather than reporting it afterwards.
  lesson: data-engineering/05-quality-and-observability/notes/01-quality-dimensions-and-tests
- front: Why can no rule within a batch catch the faults the rules missed?
  back: Every miss is a question about this batch against time, which no rule within a batch can answer.
  lesson: data-engineering/05-quality-and-observability/notes/01-quality-dimensions-and-tests
- front: How does a spine check differ from an age check after a gap?
  back: The spine keeps firing until someone repairs the hole, and the age check does not.
  lesson: data-engineering/05-quality-and-observability/notes/02-monitors-and-lineage
- front: Why does a naive three-sigma check let a quarter of the data vanish unseen?
  back: Weekly cycles inflate a mixed window, so the naive check lets a quarter of the data vanish unseen.
  lesson: data-engineering/05-quality-and-observability/notes/02-monitors-and-lineage
- front: Why would a chi-squared alarm get worse with more data?
  back: With enough rows, trivial changes become significant, so alert on a distance you can reason about.
  lesson: data-engineering/05-quality-and-observability/notes/02-monitors-and-lineage
- front: How do you key monitoring metrics so a backfill replaces instead of adds?
  back: Key metrics by the data's date rather than the clock, so that a backfill replaces instead of adds.
  lesson: data-engineering/05-quality-and-observability/notes/02-monitors-and-lineage
- front: What does lineage plus run history turn an incident into?
  back: Lineage plus run history turns an incident into a finite list of datasets to check and runs to redo.
  lesson: data-engineering/05-quality-and-observability/notes/02-monitors-and-lineage
- front: Do you need to know the cause before you stop a dashboard showing bad data?
  back: You do not need to know why a metric jumped to stop a dashboard showing it.
  lesson: data-engineering/05-quality-and-observability/notes/03-incident-playbooks
- front: Why make incident roles explicit on a small team?
  back: The common failure is capable people working uncoordinated, so make roles explicit even on a small team.
  lesson: data-engineering/05-quality-and-observability/notes/03-incident-playbooks
- front: How do you make a backfill safe to run twice?
  back: In a stressful incident jobs get run twice, so replace one logical day inside a transaction.
  lesson: data-engineering/05-quality-and-observability/notes/03-incident-playbooks
- front: What is a playbook, and why keep it short?
  back: A playbook is the decision made in advance, when nobody is stressed, so keep it short.
  lesson: data-engineering/05-quality-and-observability/notes/03-incident-playbooks
- front: What is the only return on an incident?
  back: The only return on an incident is a check that catches the next one sooner.
  lesson: data-engineering/05-quality-and-observability/notes/03-incident-playbooks
- front: How do you keep a slow migration step from stalling the application?
  back: Spend very little time holding the strongest lock, and do the slow part under weak locks or in short keyed transactions.
  lesson: data-engineering/05-quality-and-observability/notes/04-schema-and-data-migrations
- front: How do you rename a column while old and new code both run?
  back: Keep old and new code working at every step, and delay the drop, the one step with no rollback, until no reader remains.
  lesson: data-engineering/05-quality-and-observability/notes/04-schema-and-data-migrations
- front: How do you know a backup works?
  back: Only a scheduled restore that checks an invariant proves a backup, and the alert should fire when success is missing.
  lesson: data-engineering/05-quality-and-observability/notes/05-operating-data-stores
- front: What does a pool change when clients outnumber connections?
  back: A pool turns failure into waiting, so pool and queue in front of the database instead of raising `max_connections`.
  lesson: data-engineering/05-quality-and-observability/notes/05-operating-data-stores
- front: Why can a Postgres table or disk grow while no new data arrives?
  back: Dead rows, unread slots and bulk writes fill a disk slowly and without alarm, so graph each one and alert on the trend.
  lesson: data-engineering/05-quality-and-observability/notes/05-operating-data-stores
- front: How do you stop a bad model reaching production without rebuilding everything?
  back: Build what changed and its dependents in a temporary schema as a required check, so a failing test stops the merge with production untouched.
  lesson: data-engineering/05-quality-and-observability/notes/06-dataops
- front: What should page someone about late batches, and what should not?
  back: Page on actionable symptoms that threaten the SLO, and send task failures and scattered late batches to a ticket and the budget review.
  lesson: data-engineering/05-quality-and-observability/notes/06-dataops
- front: What finds a data fault, what bounds it, and what repairs it?
  back: Tests and monitors find it, lineage bounds it, and an idempotent backfill repairs it.
  lesson: data-engineering/05-quality-and-observability/notes/03-incident-playbooks
---
