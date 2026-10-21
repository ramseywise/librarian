---
title: Skip Keyed on Config, Not Capability
tags: [eval, infra, pattern]
summary: "A test skip predicate that checks whether an env var is set, instead of whether the import it guards actually works, returns before any import is attempted — so 14 tests across the exact seam a plan was about to build on were green-by-omission, and the reviewer's prescribed path fix was falsified by running it; probe importability, keep the skip as a real fallback, and make the regression floor zero skips rather than green."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-18-ml-parity-consolidated.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-18-ml-parity-consolidated.md
---

# Skip Keyed on Config, Not Capability

From an ML prototyping repo (galactus) consolidating three runs onto one shared run-record
seam. The plan's regression floor said the precedent run was "untouched and green". A
readiness gate found it was not green. It was silent.

## The mechanism

The tests that exercised the record helpers were guarded by a predicate like this:

```python
def _toolkit_available() -> bool:
    root = os.environ.get("ML_PACKAGE_ROOT")
    if not root:
        return False      # returns here; sys.path is irrelevant
    ...
```

The predicate asks *is a variable set?* The question the test needs answered is *can I
import what I am about to test?* The two had once been the same, when the toolkit lived in
an external tree reachable only through that variable. Then the toolkit moved in-repo and
became first-party. The variable stopped mattering to imports but kept gating the tests.

The result: 25 passed, 14 skipped under `-q`. With the variable set, 39 passed, 0 skipped.
The 14 skipped tests covered every helper the plan intended to lift into a shared module,
plus the write/read round-trip. **A skip renders identically to a pass in a quiet run**, so
the divergence risk the plan explicitly accepted ("the shared helper may drift from the
original copy") was undetectable by the suite meant to catch it.

## The prescribed fix was wrong, and only running it showed that

The gate prescribed putting the repo root on `pythonpath` and claimed the suite would go to
0 skips. A re-plan pass ran that experiment before writing it into a step. The count was
**unchanged**, because the predicate returns before it ever reaches an import. `pythonpath`
was neither necessary nor sufficient. The 0-skip figure was real, but it came from setting
the env var. Adopting that as the fix would have kept the very coupling the finding asked
to remove, under a new name.

Rule: a reviewer's prescribed fix is a hypothesis. Run it before writing it into a step.
Re-verifying the gate's evidence is what caught this. The follow-up plan made the fix its
own blocking step rather than a bullet inside the next one, because the correction was only
visible by experiment.

## The fix

- **Probe importability.** The env var only *adds* a path. The predicate then tries the
  real imports and returns `False` only if they fail.
- **Keep the skip as a real fallback.** A checkout where the import genuinely fails should
  still skip with a reason. *A probe that cannot skip is just a crash.*
- **Correct stale skip reasons; don't delete them.** Both skip messages asserted things that
  had become false ("the toolkit dir holds only stale bytecode", "un-skipping would run
  against a tree with no registry"). Skip reasons are load-bearing prose. A false one
  misdirects the next reader.
- **The regression floor becomes "0 skips", not "green".** Both invocation paths (bare and
  with the variable) must report the same counts.

## Un-skipping is an experiment, so preserve its evidence

The un-skip exposed one real coupling. A provenance helper keyed on the same env var and
returned `root: None` when it was unset. That broke an assertion that only passed because the
tests had run with the variable set. The fix kept the invariant the test protects: *the
record always names a fingerprintable tree, and `None` is never an answer.* When the
variable is unset, the helper falls back to the repo itself.

For anything else that failed, the operator rule was **stop and report, do not repair inside
the un-skip step**. The point of un-skipping is to learn what was hidden. A session that
quietly fixes what it finds destroys the evidence that the gap was real. Any such failure
blocks the downstream steps instead of being worked around.

## See Also
- [[Always-Red Check Carries No Signal]] — extends (the "passes for the wrong reason" mirror, here a credential-less skip in test form)
- [[An Unrun Scan Is Not a Clean Scan]] — instance-of (skip and empty result look the same to the consumer)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — alternative-to (a floor on tests collected rather than fixing the predicate)
- [[Silence Reads as Clean]] — instance-of
- [[Eval Falsifiability]] — extends
