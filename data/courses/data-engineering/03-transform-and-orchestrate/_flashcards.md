---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-engineering/03-transform-and-orchestrate/slides/deck.yaml
cards:
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
---
