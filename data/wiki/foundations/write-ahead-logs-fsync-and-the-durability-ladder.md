---
title: "Write-Ahead Logs, fsync and the Durability Ladder"
tags: [foundations, concept]
summary: "Saved is a ladder of rungs (process buffer, page cache, device, log, replica, backup), each surviving a different failure; fsync and a checksummed write-ahead log make a crash boring, and replace-by-rename keeps whole files atomic."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--09-persistence.md
---

# Write-Ahead Logs, fsync and the Durability Ladder

"Saved" is not one state but a ladder: process memory, the OS page cache, the device, a write-ahead log, a replica, an object store, a backup that has been restored in a test. Each rung survives a different failure and costs a different amount. For any rung ask, from the client's view: of the writes **acknowledged**, how many survive this failure? Losing an unacknowledged write is a failed request; losing an acknowledged one is a broken promise. Two numbers describe the answer: **RPO** (recovery point objective: the longest acceptable time since the last recovery point, i.e. how much you lose) and **RTO** (recovery time objective: the longest acceptable delay before service returns, i.e. how long you are down).

## Memory, page cache and fsync
A write passes through two caches: `write` fills a buffer inside the process, `flush` hands it to the OS page cache, `fsync` asks the OS to push it to the device and waits. A writer killed with `SIGKILL` at random moments, acknowledging after only the buffered write, lost about 235 records per crash (an 8 KB buffer at 16 bytes per record is 512 records, on average half full); one flush per record closed the gap for that failure.

**A process-kill test cannot tell flush from fsync**, because the kernel keeps the page cache after a process dies. What fsync buys shows only when the machine goes down. A simulation of power loss (labelled as a model; no physical power cut was done) kept a random half of the unsynced pages: without fsync the mean in-order prefix was 1.0 of 100 records and every trial had **holes** (later records survived while earlier ones vanished, so the file matches no moment in the program's history). Ordering is what a barrier gives: if writes before a sync complete before writes after it, a crash may lose recent transactions but will not corrupt the database.

**Cost depends on the platform.** On one laptop a 4 KiB write took 3.4 us, write plus fsync 55.3 us, and write plus a true drive-cache flush 3825.5 us. A plain fsync can stop at the drive; do not read the 55 us as the price of durability, it is the price of stopping short of it. A suspiciously fast fsync usually means a volatile cache took the write.

**Traps below your code:**
- Drives can lie: many SSDs have volatile write-back caches and many do not honour flush commands by default.
- **A failed fsync cannot be retried**: on Linux the failed pages are marked clean, so the retry reports success with the data gone. The fix is to treat it as a crash and recover from the log. A study of file systems and databases found the techniques used to handle fsync failure insufficient.
- The file is not its directory entry: fsync on a file does not necessarily make its directory entry durable; a second fsync on the directory is needed or new files and renames can vanish. A study of eleven widely used systems found 60 crash vulnerabilities from relying on unpromised file-system properties.

## The write-ahead log
Syncing every changed page at random places on disk would be unusably slow, and a crash midway would leave a table half updated. A write-ahead log (WAL) appends a description of the change to one sequential file, syncs that, and only then tells the client. Data pages follow lazily because replay rebuilds them after a crash. One sync can commit many transactions.

A record is length, checksum and payload; recovery replays until the first record that is short or fails its checksum, then truncates there. Tearing a toy log at each of 640+1 byte positions gave 0 bad recoveries; flipping one bit mid-log kept 315 of 640 bytes (the prefix, with an older state). Stopping is right, since replaying past damage could yield a state that never existed. Postgres does the same with a CRC-32C on WAL records. Removing the checksum makes recovery replay past the damage, with wrong values and no error, or misreading everything after a damaged length.

**Replacing a whole file.** Opening for write empties it. Write a temporary file, fsync it, rename it over the old one (atomic on POSIX: a reader sees the old or the new, never a mix), then fsync the directory. Killed partway in 40 trials, in-place writing left a corrupt mix 28 times; rename left 28 old and 12 new, never corrupt. `SIGKILL` proves atomicity here, not durability across a power cut.

## What `synchronous_commit` trades (Postgres)
Killing every server process during a single-row insert loop: with `synchronous_commit = on`, five crashes lost nothing out of about 58,000 acknowledged commits; with `off`, about twice as many commits got through and each crash lost 5 to 36 acknowledged rows, yet the database came back consistent, because replay stops cleanly at a commit boundary. The documented window is three times `wal_writer_delay` (200 ms by default); decide by the data (bank transfers no, event logging quite possibly). **`fsync = off` is different**: the server no longer controls write ordering and it can corrupt the whole cluster. With `on`, commit rate was 14,737 per second under the default sync method on a Mac and 296 under write-through, about 50 times slower, the honest speed of durable commits on that drive with one client (ratios, not absolutes, since the machine was busy).

**The WAL sets crash RTO**: everything since the last checkpoint is replayed on restart. Restart took 0.43 s after 131 MB of WAL, 1.79 s after 690 MB and 6.03 s after 2,099 MB, roughly linear, so `checkpoint_timeout` and `max_wal_size` are RTO settings as much as performance ones (smaller values: faster restart, more write work in normal running).

## Pitfalls
- Testing durability with `kill -9` alone says nothing about power loss; name the failure tested.
- Trusting a fast fsync; retrying a failed fsync; forgetting the directory.
- Setting `fsync = off` for a load and forgetting it.

## See Also
- [[Replication, Backups and the Durability Ladder Above the Disk]] — extends
- [[B-Trees vs LSM-Trees]] — related (both depend on a log for crash safety)
- [[Point-in-Time Recovery from Base Backup and WAL]] — related
- [[Unreliable Networks, Clocks and Process Pauses]] — related (checksums catch bit flips)
