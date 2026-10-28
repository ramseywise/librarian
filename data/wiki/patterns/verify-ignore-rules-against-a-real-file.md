---
title: Verify Ignore Rules Against a Real File
tags: [infra, pattern]
summary: "Git ignore rules and repo-hygiene hooks fail silently in ways that make a test pass over a rule that does not work. Examples: anchored patterns die on rename, `data/` makes a `!` negation inert, `git add -f` masks the break, `check-ignore` is silent on tracked paths and passes on paths with no file, and nbstripout rewrites notebooks that have no outputs. Verify each rule against a real untracked file, in the order that makes the check meaningful."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-16-repo-hygiene-tracked-content.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-16-repo-hygiene-tracked-content.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-15-lending-parity.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-15-lending-parity.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-07-23-librarian-structure-alignment.md
---

# Verify Ignore Rules Against a Real File

From a galactus hygiene sweep. The sweep untracked a third party's recruiting brief, a
notebook carrying an internal warehouse schema in its outputs, and stray run artifacts.
An adversarial review of the plan confirmed six defects, and almost every one was a check
that would have gone **green over a rule that does not work**. An ignore rule is a claim
about future files. The only way to test it is against a real file in the state the rule
has to handle.

## The gotchas

- **Anchored patterns stop matching after a directory rename.** A rule written as
  `ml-lending/docs/report.html` kept reading that way after the move to `runs/ml/lending/`.
  The file it "protected" had been tracked all along, and only one of three runs had a
  rule that survived the rename. When you rename a directory, grep `.gitignore` for the
  old path.
- **`data/` makes a `!data/.gitkeep` negation inert.** Git does not descend into an
  excluded directory, so nothing inside it can be re-included. Use `data/*` to ignore the
  contents while keeping the directory traversable. Both forms were verified empirically.
- **`git add -f` masks a broken rule.** A plan step force-added the `.gitkeep` past the
  rule. That would have greened a test of a non-working negation.
- **Fixing one check can break another.** `git check-ignore -v` returns **rc=0** on a
  negation match, while bare `check-ignore` returns rc=1. An assertion of `test $? -eq 1`
  with `-v` therefore fails exactly when the rule is *correct*, and that pushes the
  executor toward the `git add -f` that was just forbidden.
- **`check-ignore` is silent on tracked paths.** Untrack first (`git rm --cached`), then
  check. The order is load-bearing, so document it, or someone will "tidy" it backwards.
  See also [[Repo Weight Triage — GC Before LFS]].
- **`check-ignore` is a pure path query.** It passes over a path with no file behind it.
  One step's assertions would have shipped a PII-warning rule for a directory the branch
  had never held, because that directory existed only in the main checkout's working tree.
  Confirm the path exists on the branch (`git ls-tree -r origin/main`) before trusting a
  green result.
- **nbstripout is not a no-op on a notebook with no outputs.** It strips per-cell
  `execution` metadata and **renumbers cell ids positionally**: 303 of 570 lines changed.
  Inserting one cell then shifts every later id, so every future diff of that notebook
  becomes whole-file. `--keep-id` cut the change to 209 lines and stopped the
  renumbering. Make it mandatory, and assert that ids are not `['0','1','2',...]` after
  the first strip.
- **`pre-commit install` is machine-local.** It writes `.git/hooks/`, which is invisible
  to CI and to a fresh clone. The rollback list must include `pre-commit uninstall`. If it
  does not, an aborted change leaves hooks installed from a config that was just
  reverted. The hook guards one working copy; anyone else needs it as a documented setup
  step, or as a CI check.
- **Untracking does not erase history.** `git rm --cached` keeps the file locally and in
  history. Only a rewrite removes it. Write the "rewrite before any publication" condition
  into the ignore rule's comment, where it will be seen.
- **Never park a deferral in a gitignored doc.** The plan "accepted" history exposure on
  the condition of recording a blocker on any open-sourcing item. No such item existed,
  and the only record was the plan doc itself, which a global gitignore excluded.
  A deferral nobody can see is not a deferral.

## Decisions that held

- **Mechanism first, then instances.** Install the hook and demonstrate it stripping a
  real notebook. The instance fixes then become the mechanism's first proof, not a manual
  pass that happens to coincide with it.
- **Untrack or ratify is a per-item judgment.** One tracked report was *ratified* (kept,
  docs corrected) because it was a live test fixture for 17 tests in a private repo. Before
  `git rm --cached`, check for a live consumer, and check that the consumer reads the path
  you think it reads. One "only consumer" pointed at a different, empty path.
- **Scrubbing outputs is not scrubbing content.** A warehouse schema can survive in
  *source* cells after the outputs are stripped. Check at cell depth.

## Ignored but still tracked (librarian, 2026-07)

The repo gitignored its `raw/` and `wiki/` trees, yet about 760 files under them were
still tracked, because `git rm --cached` was never run when the ignore rules were added.
Ignore rules only affect untracked files. An alignment plan found this by checking
`git ls-files` against the ignore list, not by reading `.gitignore`.

## See Also
- [[Repo Weight Triage — GC Before LFS]] — extends (the same `check-ignore`-on-tracked-path trap, in a weight-reduction pass)
- [[An Unrun Scan Is Not a Clean Scan]] — instance-of (a check that passes because it never touched a file)
- [[Silence Reads as Clean]] — instance-of
- [[ML Run Reproducibility Bar]] — prerequisite-for (element 5, the data-handling sweep)
