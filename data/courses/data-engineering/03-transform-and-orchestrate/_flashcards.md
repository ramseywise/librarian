---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-engineering/03-transform-and-orchestrate/slides/deck.yaml
cards:
- front: In what order does this lecture build a pipeline that is safe to run twice?
  back: The lecture moves from one correct model to a schedule, then to re-runs and backfills, and ends by running the same pipeline in two tools.
  lesson: data-engineering/03-transform-and-orchestrate/readme
- front: Name four things this lecture teaches you to do with a pipeline.
  back: You will be able to make a pipeline traceable, tied to the right day, and boring to run twice.
  lesson: data-engineering/03-transform-and-orchestrate/readme
- front: Which layer is allowed to hold business logic?
  back: Staging is mechanical, core holds the joins and rules, and marts answer questions, so every number has an obvious place to look.
  lesson: data-engineering/03-transform-and-orchestrate/notes/01-transform
- front: How would a too-narrow key show up in row counts?
  back: Test a deduplication key against the data, since the zoomcamp's two-column key removed 960 real trips on ours.
  lesson: data-engineering/03-transform-and-orchestrate/notes/01-transform
- front: Why is the tested table not protected?
  back: A failing dbt test stops the models downstream, but the table it tested has already been replaced.
  lesson: data-engineering/03-transform-and-orchestrate/notes/01-transform
- front: What would a cron script have done in this case?
  back: Retry transient failures within a limit, then stop and skip everything downstream, so old data never goes out under a new date.
  lesson: data-engineering/03-transform-and-orchestrate/notes/02-orchestrate
- front: What breaks when a task reads the clock?
  back: Each task receives the day it is for and writes to a path derived from it, which is what makes re-running one day possible.
  lesson: data-engineering/03-transform-and-orchestrate/notes/02-orchestrate
- front: Why can an orchestrator not tell a dead worker from a paused one?
  back: An orchestrator cannot tell a dead worker from a paused one, or a finished run from correct data, so make writes safe and put a test in the graph.
  lesson: data-engineering/03-transform-and-orchestrate/notes/02-orchestrate
- front: Which one runs before the model builds?
  back: Data tests check today's data after a build, unit tests check logic against mocks before one, and you need both.
  lesson: data-engineering/03-transform-and-orchestrate/notes/03-dbt-tests-snapshots-incremental
- front: Why does a snapshot ignore --full-refresh?
  back: A snapshot records only the states it saw when it ran, so run it as often as the source changes or capture changes at the source.
  lesson: data-engineering/03-transform-and-orchestrate/notes/03-dbt-tests-snapshots-incremental
- front: Which test would have caught the missing row?
  back: A lookback with a unique key handles most late rows, and a periodic full refresh from raw repairs what is later than the window.
  lesson: data-engineering/03-transform-and-orchestrate/notes/03-dbt-tests-snapshots-incremental
- front: Why must insert_overwrite carry the whole partition?
  back: Pick the strategy by how rows change, and prefer replacing whole periods where the data has reliable event time.
  lesson: data-engineering/03-transform-and-orchestrate/notes/03-dbt-tests-snapshots-incremental
- front: Why is overwrite the default rather than merge?
  back: Overwriting a period is the default because a rerun is harmless and rows deleted upstream disappear, which a merge cannot do.
  lesson: data-engineering/03-transform-and-orchestrate/notes/04-idempotency-and-backfills
- front: Which gap from chapter 1 does this close?
  back: Between written and visible there is a place to run tests, so bad data is refused before any reader sees it.
  lesson: data-engineering/03-transform-and-orchestrate/notes/04-idempotency-and-backfills
- front: When is restating history legitimate?
  back: Joining an old day to today's dimension changes old numbers, which can be a legitimate choice but must never be an accidental one.
  lesson: data-engineering/03-transform-and-orchestrate/notes/04-idempotency-and-backfills
- front: How would a window function remove the ordering problem?
  back: Keep daily partitions independent and derive cumulative figures from them, so that a backfill can run in any order.
  lesson: data-engineering/03-transform-and-orchestrate/notes/04-idempotency-and-backfills
- front: What makes a failed check stop the report?
  back: Dagster declares assets with shared partitions and attached checks, so it can list which days of each table are missing.
  lesson: data-engineering/03-transform-and-orchestrate/notes/05-dagster-and-airflow
- front: What is the state of zone_report when the check fails?
  back: Airflow describes ordered tasks, so a failing check stops what follows, and the meaning for tables is left for you to infer.
  lesson: data-engineering/03-transform-and-orchestrate/notes/05-dagster-and-airflow
- front: Which day does a default cron run process on Jan 14 at 03:00?
  back: A bare cron string in Airflow 3 makes the logical date equal the fire time, so name the timetable or a job reads a partial day.
  lesson: data-engineering/03-transform-and-orchestrate/notes/05-dagster-and-airflow
- front: Why did --max-active-runs 2 fail here?
  back: An Airflow backfill is a request the scheduler executes, so concurrency must respect what the warehouse can write at once.
  lesson: data-engineering/03-transform-and-orchestrate/notes/05-dagster-and-airflow
- front: What matters more than the choice of tool?
  back: Run the one you already have, and remember that neither tool fixes a non-idempotent task or a missing logical date.
  lesson: data-engineering/03-transform-and-orchestrate/notes/05-dagster-and-airflow
- front: Which of these would have caught the $96,000?
  back: Each rule turns something that used to fail silently into something that fails loudly, or cannot fail at all.
  lesson: data-engineering/03-transform-and-orchestrate/notes/05-dagster-and-airflow
- front: Which pillar prices these runs?
  back: Pillar 4 covers the storage these runs write to, where layout and table formats decide the cost and atomicity of each run.
  lesson: data-engineering/03-transform-and-orchestrate/notes/05-dagster-and-airflow
- front: ETL vs ELT?
  back: Whether transformation happens before load in a separate engine or after load inside the warehouse. ELT keeps raw as a replay point, so a bad transform can be rebuilt.
  lesson: data-engineering/03-transform-and-orchestrate/notes/01-transform
- front: What does dbt actually do?
  back: Compiles templated SELECTs to SQL and runs them in the warehouse in dependency order. It moves no data and runs no compute of its own.
  lesson: data-engineering/03-transform-and-orchestrate/notes/01-transform
- front: What do the staging, core and mart layers do?
  back: One-to-one cleanup of sources; facts and dimensions joined across sources; aggregates for one consumer. Each reads only the one before.
  lesson: data-engineering/03-transform-and-orchestrate/notes/01-transform
- front: View, table, incremental or ephemeral?
  back: Pay on read; pay full rebuild on write; pay only new rows, with more logic; inline as a CTE with no object.
  lesson: data-engineering/03-transform-and-orchestrate/notes/01-transform
- front: How does dbt know the build order?
  back: It parses `ref` and `source` calls into a graph and walks it topologically.
  lesson: data-engineering/03-transform-and-orchestrate/notes/01-transform
- front: What does a dbt test return?
  back: The rows breaking the rule. Zero rows passes.
  lesson: data-engineering/03-transform-and-orchestrate/notes/01-transform
- front: What happens when a test fails in `dbt build`?
  back: At `error` severity, downstream nodes are skipped. The tested model is already rebuilt, so its bad rows are visible.
  lesson: data-engineering/03-transform-and-orchestrate/notes/01-transform
- front: Warn or error?
  back: Error for keys and anything a consumer relies on; warn for descriptive columns, and only if someone reads the warnings.
  lesson: data-engineering/03-transform-and-orchestrate/notes/01-transform
- front: Why is an inner join dangerous in a fact?
  back: It drops rows with missing dimension keys, silently. A left join to a default row keeps totals reconciled.
  lesson: data-engineering/03-transform-and-orchestrate/notes/01-transform
- front: How do you detect a pipeline that stopped loading?
  back: 'Source freshness: the newest load timestamp against the clock, since row-level tests pass on old data forever.'
  lesson: data-engineering/03-transform-and-orchestrate/notes/01-transform
- front: When would you write a macro?
  back: When the same expression appears in two models or must differ by adapter. Not merely to shorten SQL.
  lesson: data-engineering/03-transform-and-orchestrate/notes/01-transform
- front: Why not build dashboards on staging?
  back: The metric definition then moves into the BI tool, and two dashboards will disagree.
  lesson: data-engineering/03-transform-and-orchestrate/notes/01-transform
- front: What does an orchestrator do that cron does not?
  back: Dependencies, per-task retries, parameterised runs, backfill, run history and alerting, and it stops downstream on failure.
  lesson: data-engineering/03-transform-and-orchestrate/notes/02-orchestrate
- front: What is a logical date?
  back: The period a run is for, separate from when it executes. It makes a late run or a re-run process the right data.
  lesson: data-engineering/03-transform-and-orchestrate/notes/02-orchestrate
- front: Why can't a job that reads `now()` be backfilled?
  back: Every re-run computes today's data, so the failed period can't be reproduced.
  lesson: data-engineering/03-transform-and-orchestrate/notes/02-orchestrate
- front: What is a backfill, mechanically?
  back: The schedule's runs for a range, minus those that succeeded, each one isolated by its logical date.
  lesson: data-engineering/03-transform-and-orchestrate/notes/02-orchestrate
- front: When is a retry safe?
  back: When the failure is transient and the task is idempotent. Otherwise it wastes attempts or duplicates data.
  lesson: data-engineering/03-transform-and-orchestrate/notes/02-orchestrate
- front: Sensor vs schedule?
  back: A schedule assumes data arrives on time, a sensor waits for evidence that it has. A sensor needs a timeout.
  lesson: data-engineering/03-transform-and-orchestrate/notes/02-orchestrate
- front: How should tasks pass data?
  back: Through storage, passing only paths or keys between tasks. It makes each step restartable and keeps the orchestrator small.
  lesson: data-engineering/03-transform-and-orchestrate/notes/02-orchestrate
- front: Why does the task graph need test tasks?
  back: A successful run only proves code finished. A test in the graph blocks publishing wrong numbers.
  lesson: data-engineering/03-transform-and-orchestrate/notes/02-orchestrate
- front: Why adopt an orchestrator on day 0?
  back: It forces pipelines into separate units that hand off through storage, so later triggers are configuration rather than a refactor.
  lesson: data-engineering/03-transform-and-orchestrate/notes/02-orchestrate
- front: Why are the zoomcamps' tools different?
  back: Each cohort re-recorded with a different tool. The concepts carry across, and any one API is about a week's work.
  lesson: data-engineering/03-transform-and-orchestrate/notes/02-orchestrate
- front: What is a singular test, and a generic one?
  back: A SQL file that returns failing rows; the same thing parameterised, attachable to columns in YAML.
  lesson: data-engineering/03-transform-and-orchestrate/notes/03-dbt-tests-snapshots-incremental
- front: Name a test you would write beyond the built-ins.
  back: Reconciliation of fact to source on counts and sums, and uniqueness of the fact's grain after joins.
  lesson: data-engineering/03-transform-and-orchestrate/notes/03-dbt-tests-snapshots-incremental
- front: Data test vs unit test?
  back: A data test checks today's data after build. A unit test checks logic on mocked rows before the build.
  lesson: data-engineering/03-transform-and-orchestrate/notes/03-dbt-tests-snapshots-incremental
- front: '`warn_if` / `error_if`?'
  back: Thresholds on the failing-row count that let one test warn at a low count and fail at a high one.
  lesson: data-engineering/03-transform-and-orchestrate/notes/03-dbt-tests-snapshots-incremental
- front: What does `store_failures` do?
  back: Writes failing rows to a table, so they can be inspected without rerunning the test.
  lesson: data-engineering/03-transform-and-orchestrate/notes/03-dbt-tests-snapshots-incremental
- front: What is a snapshot, and what are its columns?
  back: A Type 2 history of a mutable source, with `dbt_valid_from`, `dbt_valid_to`, `dbt_scd_id`, `dbt_updated_at`.
  lesson: data-engineering/03-transform-and-orchestrate/notes/03-dbt-tests-snapshots-incremental
- front: What can a snapshot not capture?
  back: Intermediate states between runs. It samples, and a missed run can't be rebuilt.
  lesson: data-engineering/03-transform-and-orchestrate/notes/03-dbt-tests-snapshots-incremental
- front: Timestamp or check?
  back: Timestamp when `updated_at` is reliable, as it records true change time. Check otherwise, on the listed columns.
  lesson: data-engineering/03-transform-and-orchestrate/notes/03-dbt-tests-snapshots-incremental
- front: Why doesn't `--full-refresh` affect snapshots?
  back: Rebuilding would destroy the history it exists to hold.
  lesson: data-engineering/03-transform-and-orchestrate/notes/03-dbt-tests-snapshots-incremental
- front: What does `is_incremental()` check?
  back: Target exists, model is incremental, and no `--full-refresh`.
  lesson: data-engineering/03-transform-and-orchestrate/notes/03-dbt-tests-snapshots-incremental
- front: What does `unique_key` do?
  back: Replaces existing rows with the same key. Without it most adapters append, and any overlap duplicates.
  lesson: data-engineering/03-transform-and-orchestrate/notes/03-dbt-tests-snapshots-incremental
- front: How do you handle late-arriving rows?
  back: A lookback window with `unique_key`, sized from measured lateness, plus periodic full refresh and reconciliation.
  lesson: data-engineering/03-transform-and-orchestrate/notes/03-dbt-tests-snapshots-incremental
- front: What does `on_schema_change` do to old rows?
  back: Nothing. No setting backfills; that takes a full refresh or a one-off update.
  lesson: data-engineering/03-transform-and-orchestrate/notes/03-dbt-tests-snapshots-incremental
- front: What is microbatch?
  back: One bounded, replaceable query per period of `event_time`, so a period can be retried or backfilled alone.
  lesson: data-engineering/03-transform-and-orchestrate/notes/03-dbt-tests-snapshots-incremental
- front: When do you make a model incremental?
  back: When a measured rebuild cost justifies carrying two code paths.
  lesson: data-engineering/03-transform-and-orchestrate/notes/03-dbt-tests-snapshots-incremental
- front: What does idempotent mean for a pipeline?
  back: Running a task again for the same period leaves the same state as running it once.
  lesson: data-engineering/03-transform-and-orchestrate/notes/04-idempotency-and-backfills
- front: How do you make a batch load idempotent?
  back: Overwrite the partition for the logical date in one transaction, or upsert on a natural key.
  lesson: data-engineering/03-transform-and-orchestrate/notes/04-idempotency-and-backfills
- front: Overwrite or merge?
  back: Overwrite by default, as it also reflects upstream deletes. Merge when no period owns the row, as in CDC.
  lesson: data-engineering/03-transform-and-orchestrate/notes/04-idempotency-and-backfills
- front: What makes a task impure?
  back: The clock, latest-state dimensions, unordered dedupe, unseeded randomness, live API reads, reading whatever is in the folder.
  lesson: data-engineering/03-transform-and-orchestrate/notes/04-idempotency-and-backfills
- front: What is functional data engineering?
  back: 'Beauchemin''s framing: pure tasks, overwritten partitions, immutable raw inputs, so any output can be recomputed.'
  lesson: data-engineering/03-transform-and-orchestrate/notes/04-idempotency-and-backfills
- front: What is write-audit-publish?
  back: Build to a staging location, test it, and make it visible atomically only if it passes.
  lesson: data-engineering/03-transform-and-orchestrate/notes/04-idempotency-and-backfills
- front: How do you handle late data?
  back: Assign rows by event time, land them, and re-run the affected partition and what's downstream of it.
  lesson: data-engineering/03-transform-and-orchestrate/notes/04-idempotency-and-backfills
- front: Why can a backfill change history unexpectedly?
  back: A join to a current-state dimension applies today's attributes to old periods. Join as of the logical date.
  lesson: data-engineering/03-transform-and-orchestrate/notes/04-idempotency-and-backfills
- front: What is `depends_on_past` for?
  back: A task whose partition reads the previous one, such as a cumulative table. It must run in order.
  lesson: data-engineering/03-transform-and-orchestrate/notes/04-idempotency-and-backfills
- front: How do you avoid order dependence?
  back: Compute a cumulative with a window over the daily table, making it a pure function of its input.
  lesson: data-engineering/03-transform-and-orchestrate/notes/04-idempotency-and-backfills
- front: How do you run a large backfill safely?
  back: Small slice first, a concurrency limit, a cost estimate, reconcile afterwards, and tell consumers.
  lesson: data-engineering/03-transform-and-orchestrate/notes/04-idempotency-and-backfills
- front: How do you make a side effect safe?
  back: A deterministic idempotency key checked before sending, ideally honoured by the receiver. Otherwise choose at-least-once or at-most-once.
  lesson: data-engineering/03-transform-and-orchestrate/notes/04-idempotency-and-backfills
- front: What is the core difference between Dagster and Airflow?
  back: Dagster's nodes are assets, the tables that should exist; Airflow's are tasks, the work to run. Dagster can say which partitions are missing; Airflow reports which runs happened.
  lesson: data-engineering/03-transform-and-orchestrate/notes/05-dagster-and-airflow
- front: What does a backfill look like in each?
  back: 'Dagster: select partitions, one run each by default. Airflow 3: `airflow backfill create` with a date range, and the scheduler carries it out. Both depend on the task being idempotent.'
  lesson: data-engineering/03-transform-and-orchestrate/notes/05-dagster-and-airflow
- front: What changed about cron in Airflow 3?
  back: '`create_cron_data_intervals` defaults to `False`, so a cron string means `CronTriggerTimetable` and the logical date equals the fire time. `ds` then names the current day.'
  lesson: data-engineering/03-transform-and-orchestrate/notes/05-dagster-and-airflow
- front: How do you stop a bad table reaching a report?
  back: A blocking check in Dagster; a task before the report in Airflow. The checked table is already written in both, so the guarantee is about what's downstream.
  lesson: data-engineering/03-transform-and-orchestrate/notes/05-dagster-and-airflow
- front: What does `@asset` in Airflow 3 give you and not give you?
  back: Scheduling on data events without an edge between Dags. It does not give per-partition state, and asset-triggered runs have no logical date.
  lesson: data-engineering/03-transform-and-orchestrate/notes/05-dagster-and-airflow
- front: How do dbt and an orchestrator fit together?
  back: '`dagster-dbt` maps models to assets and tests to checks; Cosmos maps a project to a Dag of tasks. Without one, `dbt build` is one opaque step.'
  lesson: data-engineering/03-transform-and-orchestrate/notes/05-dagster-and-airflow
- front: Why might a parallel backfill fail?
  back: Concurrent runs collide on a shared output or a single-writer store. Limit active runs or partition the writes.
  lesson: data-engineering/03-transform-and-orchestrate/notes/05-dagster-and-airflow
- front: Which would you choose?
  back: Whichever the team runs, unless starting fresh. A second orchestrator costs more than either's features. Idempotency and logical dates matter more than the choice.
  lesson: data-engineering/03-transform-and-orchestrate/notes/05-dagster-and-airflow
---
