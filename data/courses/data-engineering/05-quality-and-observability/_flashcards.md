---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-engineering/05-quality-and-observability/slides/deck.yaml
cards:
- front: What are the five parts of this lecture, in order?
  back: The first three parts find and repair wrong data, and the last two keep the running store and the delivery path safe.
  lesson: data-engineering/05-quality-and-observability/readme
- front: Name four things this lecture teaches you to do.
  back: You will be able to catch a fault, bound its damage, repair it safely and keep the store and the pipeline running.
  lesson: data-engineering/05-quality-and-observability/readme
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
- front: What are four ways a repair goes wrong?
  back: A repair is finished when the blast radius is walked to the end, any filled gap is labelled and the checks that fired are quiet.
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
- front: What are four ways DataOps checks become decorative?
  back: A check that can be merged past, an SLO with no policy and an alert on a cause are all ignored in time, so require the check, agree the policy and page on the symptom.
  lesson: data-engineering/05-quality-and-observability/notes/06-dataops
- front: What finds a data fault, what bounds it, and what repairs it?
  back: Tests and monitors find it, lineage bounds it, and an idempotent backfill repairs it.
  lesson: data-engineering/05-quality-and-observability/notes/03-incident-playbooks
- front: Name the main data quality dimensions.
  back: Completeness, uniqueness, validity, consistency, timeliness, accuracy. Each needs different context, from the table alone up to an outside source.
  lesson: data-engineering/05-quality-and-observability/notes/01-quality-dimensions-and-tests
- front: What is a data test in dbt?
  back: A `SELECT` that returns failing rows. Zero rows means it passes. Generic tests are declared in YAML; singular tests are SQL files.
  lesson: data-engineering/05-quality-and-observability/notes/01-quality-dimensions-and-tests
- front: Why not make every column `not_null`?
  back: A test that fails daily gets muted. Use a tolerance such as GX `mostly`, or warning severity.
  lesson: data-engineering/05-quality-and-observability/notes/01-quality-dimensions-and-tests
- front: How do you test accuracy?
  back: 'Against an independent source: control totals, reconciliation with the producer, or sampling against the real world.'
  lesson: data-engineering/05-quality-and-observability/notes/01-quality-dimensions-and-tests
- front: What can row-level tests not catch?
  back: Missing partitions, late data and shifts that stay within valid ranges. These need a comparison against time or history.
  lesson: data-engineering/05-quality-and-observability/notes/01-quality-dimensions-and-tests
- front: What is write-audit-publish?
  back: Write to a hidden location, run tests there, and expose the data only if they pass. It prevents bad data reaching readers rather than reporting it after.
  lesson: data-engineering/05-quality-and-observability/notes/01-quality-dimensions-and-tests
- front: dbt model contract versus test?
  back: 'A model contract enforces shape (names, types) at build. A test checks values after they exist. You usually want both. A data contract is broader: a cross-team promise that includes meaning and owner.'
  lesson: data-engineering/05-quality-and-observability/notes/01-quality-dimensions-and-tests
- front: Great Expectations or dbt tests?
  back: dbt tests when the model lives in dbt. GX for files and frames outside dbt, or where you want distribution expectations and data docs. Keep one home per rule.
  lesson: data-engineering/05-quality-and-observability/notes/01-quality-dimensions-and-tests
- front: How do you pick thresholds?
  back: Profile real data, adjust with domain knowledge, and prefer limits that encode physical truth over tight ones that go stale.
  lesson: data-engineering/05-quality-and-observability/notes/01-quality-dimensions-and-tests
- front: 'Test or monitor: what''s the difference?'
  back: A test checks a batch against a written rule. A monitor compares a batch with its history, so it finds unanticipated change.
  lesson: data-engineering/05-quality-and-observability/notes/02-monitors-and-lineage
- front: Why isn't `max(loaded_at)` enough for freshness?
  back: A newer partition clears the alert while an older one is still missing. Add a date spine to find holes.
  lesson: data-engineering/05-quality-and-observability/notes/02-monitors-and-lineage
- front: How do you build a volume monitor?
  back: Same-weekday window, median and MAD, a floor on the band. Validate by injecting losses into real history.
  lesson: data-engineering/05-quality-and-observability/notes/02-monitors-and-lineage
- front: Why are p-values poor drift alarms at scale?
  back: With enough rows, trivial differences are significant. Threshold on effect size (KS `D`, L-infinity distance).
  lesson: data-engineering/05-quality-and-observability/notes/02-monitors-and-lineage
- front: Data, target and concept drift?
  back: P(inputs), P(outputs), and P(output given input). Only the last needs labels to confirm.
  lesson: data-engineering/05-quality-and-observability/notes/02-monitors-and-lineage
- front: First model alarm when labels arrive late?
  back: Prediction drift, since it needs no ground truth.
  lesson: data-engineering/05-quality-and-observability/notes/02-monitors-and-lineage
- front: What should the reference window be?
  back: Data the model handles acceptably, from the same pipeline, with predictions attached.
  lesson: data-engineering/05-quality-and-observability/notes/02-monitors-and-lineage
- front: Why key metrics by logical date?
  back: So backfills replace, rather than add. A monitor is itself an idempotent pipeline.
  lesson: data-engineering/05-quality-and-observability/notes/02-monitors-and-lineage
- front: What does OpenLineage define?
  back: A standard event model of Jobs, Runs and Datasets with facets, sent as run state events and woven into a graph by a backend.
  lesson: data-engineering/05-quality-and-observability/notes/02-monitors-and-lineage
- front: What is lineage for in an incident?
  back: Blast radius downstream, suspects upstream, and with run history, the list of runs to redo.
  lesson: data-engineering/05-quality-and-observability/notes/02-monitors-and-lineage
- front: Report versus TestSuite in Evidently?
  back: A report describes; a suite asserts and can gate a pipeline.
  lesson: data-engineering/05-quality-and-observability/notes/02-monitors-and-lineage
- front: How do data incidents differ from service incidents?
  back: Damage persists after the cause is fixed and spreads downstream, so repair needs a backfill.
  lesson: data-engineering/05-quality-and-observability/notes/03-incident-playbooks
- front: The priority order in an incident?
  back: Stop the bleeding, restore service, preserve the evidence. Contain before you diagnose.
  lesson: data-engineering/05-quality-and-observability/notes/03-incident-playbooks
- front: What roles does an incident need?
  back: Commander, operations, communications, planning. One group changes the system. One person may hold several.
  lesson: data-engineering/05-quality-and-observability/notes/03-incident-playbooks
- front: How do you make a backfill safe?
  back: Replace one logical partition per transaction, so that a rerun gives the same result. Test by running it twice.
  lesson: data-engineering/05-quality-and-observability/notes/03-incident-playbooks
- front: Why not fix raw data in place?
  back: It is the only record of what the source sent. Apply dated corrections in a layer above.
  lesson: data-engineering/05-quality-and-observability/notes/03-incident-playbooks
- front: What's the point of write-audit-publish here?
  back: Readers see a gap instead of wrong numbers, with no action needed during the incident.
  lesson: data-engineering/05-quality-and-observability/notes/03-incident-playbooks
- front: How do you handle late data downstream?
  back: 'Trigger on arrival: rebuild any output older than its newest input.'
  lesson: data-engineering/05-quality-and-observability/notes/03-incident-playbooks
- front: How do you tell a real shift from a measurement fault?
  back: Compare columns that should move together. Distance up with fares flat is measurement.
  lesson: data-engineering/05-quality-and-observability/notes/03-incident-playbooks
- front: What makes a postmortem useful?
  back: Blameless, with facts, contributing causes, and actions with owners and dates, including at least one new check.
  lesson: data-engineering/05-quality-and-observability/notes/03-incident-playbooks
- front: Can you repair data the source never sent?
  back: No. Re-request it, or publish a labelled estimate. Never present an imputed value as repaired.
  lesson: data-engineering/05-quality-and-observability/notes/03-incident-playbooks
- front: Why can a one-millisecond `ALTER` take a site down?
  back: It needs `ACCESS EXCLUSIVE`. If a long transaction holds any lock, the `ALTER` queues, and every new query queues behind it. Use `lock_timeout` and retry.
  lesson: data-engineering/05-quality-and-observability/notes/04-schema-and-data-migrations
- front: Which lock does `CREATE INDEX` take, and how do you avoid it?
  back: '`SHARE`, which blocks writes. `CREATE INDEX CONCURRENTLY` takes a weaker lock, does two scans and runs outside a transaction; on failure it leaves an `INVALID` index to drop.'
  lesson: data-engineering/05-quality-and-observability/notes/04-schema-and-data-migrations
- front: How do you add `NOT NULL` to a big table safely?
  back: '`ADD CHECK ... NOT VALID`, then `VALIDATE`, then `SET NOT NULL`, which skips the scan. Then drop the check.'
  lesson: data-engineering/05-quality-and-observability/notes/04-schema-and-data-migrations
- front: When does adding a column rewrite the table?
  back: With a volatile default, a stored generated column or an identity column. A constant default is stored in the catalog.
  lesson: data-engineering/05-quality-and-observability/notes/04-schema-and-data-migrations
- front: Walk through renaming a column in production.
  back: Add new column. Dual write. Backfill in batches. Verify. Deploy reads from new. Stop writes to old. Drop old later.
  lesson: data-engineering/05-quality-and-observability/notes/04-schema-and-data-migrations
- front: Why can't a backfill alone be correct?
  back: The application keeps changing rows after the batch passes them. Start dual writes first and verify afterwards.
  lesson: data-engineering/05-quality-and-observability/notes/04-schema-and-data-migrations
- front: What makes a backfill safe to run?
  back: Small keyed transactions, a predicate that makes it rerunnable, a pause or brake on database health and replica lag.
  lesson: data-engineering/05-quality-and-observability/notes/04-schema-and-data-migrations
- front: What does autogenerate do with a rename?
  back: Writes an add and a drop, because it cannot detect renames. Read each script.
  lesson: data-engineering/05-quality-and-observability/notes/04-schema-and-data-migrations
- front: When can you no longer roll back?
  back: After contract. Until then old code still works against the schema. After, restore from backup.
  lesson: data-engineering/05-quality-and-observability/notes/04-schema-and-data-migrations
- front: How do you know a warehouse move is correct?
  back: Parallel run, then compare per partition and key, not just totals. Totals can match while every day differs.
  lesson: data-engineering/05-quality-and-observability/notes/04-schema-and-data-migrations
- front: How do you change embedding models?
  back: Build a second index, dual write or replay changes, evaluate, swap an alias atomically, keep the old one for rollback. Vectors from different models are not comparable.
  lesson: data-engineering/05-quality-and-observability/notes/04-schema-and-data-migrations
- front: Why isn't a replica a backup?
  back: It replays mistakes quickly. It protects against losing a machine, not against a bad `DELETE`.
  lesson: data-engineering/05-quality-and-observability/notes/05-operating-data-stores
- front: What does point-in-time recovery need?
  back: A base backup, every archived WAL segment since, a `restore_command` and a target. It starts a new timeline.
  lesson: data-engineering/05-quality-and-observability/notes/05-operating-data-stores
- front: Dump or physical backup?
  back: Dump for logical copies, one table or a version move. Physical plus WAL for any point in time and a large database. Many teams run both.
  lesson: data-engineering/05-quality-and-observability/notes/05-operating-data-stores
- front: What happens at `max_connections`?
  back: New clients get an error. Fix it with pooling, which turns errors into queueing. Raising the limit allocates more resources and adds contention.
  lesson: data-engineering/05-quality-and-observability/notes/05-operating-data-stores
- front: What does transaction pooling break?
  back: 'Session state: `SET`, `LISTEN`, session advisory locks and `PREPARE`. Migrations should use a direct connection.'
  lesson: data-engineering/05-quality-and-observability/notes/05-operating-data-stores
- front: Why does a Postgres table grow with no new rows?
  back: Updates leave dead row versions until vacuum. Plain `VACUUM` reuses space and `VACUUM FULL` returns it, under an exclusive lock.
  lesson: data-engineering/05-quality-and-observability/notes/05-operating-data-stores
- front: What stops vacuum from working?
  back: The oldest open transaction or snapshot, old replication slots, or `hot_standby_feedback` from a standby.
  lesson: data-engineering/05-quality-and-observability/notes/05-operating-data-stores
- front: What is wraparound?
  back: Transaction IDs are finite. If autovacuum can't freeze rows, Postgres eventually refuses new transaction IDs. Alert on `age(datfrozenxid)`.
  lesson: data-engineering/05-quality-and-observability/notes/05-operating-data-stores
- front: How do you measure replica lag?
  back: '`pg_stat_replication`: LSN differences in bytes, and the `write_lag`, `flush_lag` and `replay_lag` times.'
  lesson: data-engineering/05-quality-and-observability/notes/05-operating-data-stores
- front: Why was a standby query cancelled?
  back: A conflict with WAL replay, typically from a vacuum on the primary, past `max_standby_streaming_delay`.
  lesson: data-engineering/05-quality-and-observability/notes/05-operating-data-stores
- front: What fills a Postgres disk unexpectedly?
  back: WAL from bulk writes, a slot with no consumer, bloat, and rewrites needing a second copy.
  lesson: data-engineering/05-quality-and-observability/notes/05-operating-data-stores
- front: How do you do a major upgrade?
  back: '`pg_upgrade`, dump and restore, or logical replication. Read every release''s migration notes and test clients first.'
  lesson: data-engineering/05-quality-and-observability/notes/05-operating-data-stores
- front: What is DataOps in one line?
  back: 'Applying software delivery habits to data: version control, automated tests, isolated environments, automated deploys and service levels.'
  lesson: data-engineering/05-quality-and-observability/notes/06-dataops
- front: Is Snowflake vs Airflow a sensible comparison?
  back: No. Snowflake stores and computes, and Airflow schedules. They sit in different layers and often run together.
  lesson: data-engineering/05-quality-and-observability/notes/06-dataops
- front: What does `state:modified+` do?
  back: Compares the project with a saved manifest and selects changed nodes and everything downstream.
  lesson: data-engineering/05-quality-and-observability/notes/06-dataops
- front: What does `--defer` do?
  back: Resolves refs to unselected nodes missing from the current environment using the saved manifest, so CI can read production for what it didn't build.
  lesson: data-engineering/05-quality-and-observability/notes/06-dataops
- front: How do you stop a bad model from reaching production?
  back: Build and test it in a temporary schema on the pull request, as a required check.
  lesson: data-engineering/05-quality-and-observability/notes/06-dataops
- front: Why avoid top-level code in an Airflow DAG file?
  back: The scheduler parses the file repeatedly, so that code runs each time and slows it down.
  lesson: data-engineering/05-quality-and-observability/notes/06-dataops
- front: Where do secrets go?
  back: In a secret manager or the CI system, passed as environment variables. Rotate anything that reaches git.
  lesson: data-engineering/05-quality-and-observability/notes/06-dataops
- front: What is drift, and what catches it?
  back: Real infrastructure no longer matching config. A plan shows it, because it refreshes before comparing.
  lesson: data-engineering/05-quality-and-observability/notes/06-dataops
- front: What's the danger in applying a Terraform plan?
  back: 'Replacement: some changes destroy and re-create the resource. Read plans for destroys and guard stateful ones.'
  lesson: data-engineering/05-quality-and-observability/notes/06-dataops
- front: How do you deploy data with a real rollback?
  back: Build beside the old version, audit, swap a view, and keep the old build for a while.
  lesson: data-engineering/05-quality-and-observability/notes/06-dataops
- front: Give an example of a freshness SLO.
  back: 99% of hourly batches arrive within 30 minutes, over a four-week rolling window.
  lesson: data-engineering/05-quality-and-observability/notes/06-dataops
- front: What's an error budget for?
  back: It's the failure you've agreed to accept. Spending it triggers an agreed policy, such as pausing risky changes.
  lesson: data-engineering/05-quality-and-observability/notes/06-dataops
- front: What should page someone?
  back: Actionable symptoms that threaten an SLO, not every task failure.
  lesson: data-engineering/05-quality-and-observability/notes/06-dataops
- front: What does a semantic layer solve?
  back: One definition per metric, used by every tool, in place of SQL copied into each dashboard.
  lesson: data-engineering/05-quality-and-observability/notes/06-dataops
- front: How do you keep a reverse ETL sync safe to rerun?
  back: Upsert by stable ID, send only records whose fingerprint changed, and record a send only after it succeeds.
  lesson: data-engineering/05-quality-and-observability/notes/06-dataops
---
