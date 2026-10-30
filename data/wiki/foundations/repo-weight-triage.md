---
title: Repo Weight Triage — GC Before LFS
tags: [foundations, decision]
summary: "When a repo feels too heavy, measure before choosing a fix. Loose objects are reclaimable by git gc, duplicate blobs cost working tree rather than history, and re-fetchable files need a manifest rather than storage. Sequence: gc, dedupe, untrack media, then decide gitignore+manifest. Avoid submodules and LFS at personal-repo scale."
updated: 2026-10-30
sources:
  - data/raw/claude-docs/learn-ai-engineering/docs/research/2026-07-29_LAE-106_vendored-repos-readings.md
  - data/raw/claude-docs/learn-ai-engineering/docs/plans/2026-08-14-LAE-106-consolidate-vendored-course-repos.md
  - data/raw/repos/learn-ai-engineering/.claude--docs--plans--2026-08-14-LAE-106-consolidate-vendored-course-repos.md
---

# Repo Weight Triage — GC Before LFS

A learning repo with a 3.3G working tree and a 1.7G `.git` was flagged for "too many
vendored course repos". Measuring it with read-only commands (`git ls-files`,
`git cat-file`, `du`) showed that both the size of the problem and its cause were wrong.
The method generalizes to any repo that feels too heavy.

## Measure the layers separately

| Layer | Size | What it actually was |
|---|---|---|
| `.git` total | 1.7G | |
| Packed history (`size-pack`) | **395M** | The only permanent part |
| Loose objects | ~1.1G | **Reclaimable by `git gc`**, not history |
| `.git/lfs` cache | 139M | Orphaned: LFS configured, zero files tracked |
| Tracked PDFs | **1.0G** | 405 files: the real weight |
| Vendored course repos | ~70M | Under 10% of the weight; the suspected cause |

Four findings changed the decision:

1. **Most of `.git` was loose objects.** `git gc --aggressive --prune=now` reclaims them with
   no risk and no decisions to make. Run it first, because it changes what the remaining
   problem looks like.
2. **The weight was PDFs, not code.** Even inside the "heavy" vendored repos, most of the
   bytes were three podcast `.mp4` files and a single database dump.
3. **Duplicates cost working tree, not history.** 52 PDFs appeared at more than one path
   (241M). Git stores a blob once by hash, so deduping shrinks the checkout but not the
   pack. The duplication also showed that the per-topic copies were redundant, not curated.
4. **Re-fetchable files need a manifest, not storage.** 120 of the PDFs had arXiv IDs in
   their filenames. A list of IDs plus a fetch script reproduces them exactly and costs no
   storage. Books and handouts with weaker provenance get a manifest of titles and URLs and
   stay on local disk.

## Why not submodules or LFS

- **Submodules** would address under 10% of the weight and add permanent friction (detached
  HEADs, `--recursive` clones, upstreams that disappear). The repos had `-main` suffixes,
  meaning they were ZIP downloads. **There is no upstream commit to pin.** The one genuinely
  separate nested repo already had zero tracked files and only needed a `.gitignore` line.
- **LFS** would work technically, but the existing setup was dead (an orphaned cache, no
  pointers). The free tier's 1GB storage/bandwidth limit was exceeded by the PDFs alone. And
  LFS turns a large-but-working repo into one that breaks confusingly for anyone without
  `git-lfs` installed. If files must stay versioned at this scale, plain tracking beats LFS.

## The sequence

Smallest and safest step first. Re-measure after each step, since an early step may make
the later ones unnecessary:

1. `git gc --aggressive --prune=now`
2. Dedupe identical blobs, keeping the topic-filed copy
3. Untrack media and dumps that should never have been tracked
4. Only then decide gitignore+manifest for the documents. This is the one step that needs
   a judgment call (is the library meant to travel with the clone?)

Every removal uses `git rm --cached`, which untracks without deleting. Untracking does not
shrink existing history; that requires `filter-repo`, which breaks every existing clone and
was not worth it at 395M.

## Follow-up: stop the bleed was executed, then reverted

Two weeks later a second pass measured the same repo again: 414 tracked PDFs at 1.10 GiB,
73% of tracked bytes, with `size-pack` at **1.42 GiB** (the earlier pass recorded 395M;
a 2026-10 re-measure reads 1.64 GiB, so packed history kept growing rather than a gc merely
packing loose objects. At that size `filter-repo` is the main remaining lever, not "not
worth it"). It split the work into two phases with a
hard boundary between them:

| Phase | Mechanism | Effect on a fresh clone | Cost |
|---|---|---|---|
| **Stop the bleed** | `.gitignore` + `git rm --cached` + a provenance manifest | **None.** Every blob stays in history. | Near zero, reversible |
| **Evict** | `git filter-repo` | Clone shrinks | Rewrites every commit and force-pushes a public repo with a live fork |
| LFS migrate | `git lfs migrate import` | Clone shrinks | The same rewrite, **plus** ongoing quota |

The eviction phase was gated on two things, not one. It needed explicit approval, and the
PDFs had to be migrated somewhere else first, because running `filter-repo` over blobs that
are still tracked deletes them from the working tree on the next checkout.

Phase 1 (untracking 14 vendored course repos, 886 files) ran and passed every check. **The
owner then reverted it** and kept only the provenance manifest and a Dependabot cleanup.
Phase 1 had always been worth little: it could not shrink the clone, so its only benefit
was that the repo stopped growing. Against that, an ignored file does not survive a fresh
clone on another machine. If repo size becomes a real problem, the target is the PDFs, and
removing them needs a history rewrite either way.

Lessons that hold whatever gets decided:

- **Ignore + manifest preserves nothing across machines without a sync layer.** The research
  marked this as its strongest disconfirming evidence: the local precedent "worked" only on
  the one machine where the files already existed. Pair any ignore decision with a verified
  backup destination. Untracking without one is the only truly irreversible move on the
  table.
- **`.gitignore` is inert on tracked paths, and `git check-ignore` prints nothing for them.**
  A test of an ignore rule run *before* untracking fails even when the rule is correct.
  Check with `--no-index`, or test after the `git rm --cached`.
- **Suffix-keyed rules sweep up irreplaceable work.** One `-master` directory looked
  vendored but turned out to be a personal MOOC working copy whose completed assignment
  exists nowhere else. Its provenance matched no public repo. A rule like `**/*-master/`
  would have untracked it along with the real snapshots. Rename misfiled directories so
  their status is obvious from the name.
- **Untracking has downstream config dependencies.** Four of thirteen Dependabot
  `directory:` entries pointed into the vendored directories. Untracking them without
  editing that config leaves the bot scanning paths that are gone.
- **"Unmodified snapshot" claims need an author check.** Research said every vendored
  directory had 2–3 bulk-import commits. Planning found four with 10–29 commits. All of them
  were Dependabot bumps, so the conclusion survived but the evidence did not. Running
  `git log --format='%an'` per directory turned a "Low" risk into a verified "cleared".
- **Acceptance numbers must be arithmetically possible.** The plan asserted the PDF count
  would stay at 414 after untracking, as proof that no PDF was touched. But 7 PDFs lived
  inside the vendored directories, so a *correct* run would have failed its own gate. The
  count was corrected to 407, and the guarantee was narrowed to the readings directory,
  which is the promise that actually mattered.

The asset table in this pass used [[REUSE/ADAPT/SKIP Asset Verdicts]]. The verdicts were
SKIP for submodules (no fork point to track) and ADAPT for `filter-repo` (deferred, not
discarded: it is the only tool that reclaims the space).

## See Also
- [[Git Branch Triage]] — related (the other measure-before-acting git triage)
- [[Automated Paper Discovery Pipeline]] — related (arXiv ID as the immutable key, used here for the re-fetch manifest)
- [[REUSE/ADAPT/SKIP Asset Verdicts]] — instance-of (the follow-up pass's asset table)
- [[Verify Ignore Rules Against a Real File]] — extends (the full set of ignore-rule checks that pass over broken rules)
