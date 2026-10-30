---
title: Native Library Load-Order Collision
tags: [patterns, infra, pattern]
summary: "Two Python packages that each vendor a different build of the same native library (LightGBM and torch both ship libomp.dylib) collide: the first one loaded wins, and if torch's build wins, LightGBM training segfaults with no Python traceback. Pin the import order where it can't be refactored away."
updated: 2026-10-30
sources:
  - data/raw/repos/listen-wiseer/CLAUDE.md
---

# Native Library Load-Order Collision

In listen-wiseer, LightGBM and torch (pulled in through `sentence-transformers`) each
vendor their own `libomp.dylib`. They are **different builds**. The dynamic loader keeps
whichever copy is loaded first. If torch's copy wins, LightGBM training crashes inside its
C library. It is a hard segfault with no Python traceback, so nothing points at the
import order.

## Why it is hard to diagnose

- **The failure depends on import order.** The same training code passes or crashes
  depending on which module some earlier import touched first: a test file, a fixture, a
  CLI entry point.
- **No traceback.** The crash happens in native code, so the usual "read the stack" step
  gives nothing.
- **The obvious env var is the wrong fix.** `KMP_DUPLICATE_LIB_OK` is for Intel MKL's OpenMP
  runtime. These are LLVM builds, so it does not help.

## Fix

Pin the load order at the earliest shared entry point. listen-wiseer imports `lightgbm`
at module scope in `tests/conftest.py`, so LightGBM's libomp loads before anything can
import torch. The import looks unused to a linter or a reviewer. Comment it as
load-bearing and record it in the repo's gotchas list. The same trap applies to any script
that imports torch before training, so put the pinning import in scripts too, not only
in tests.

## Related trap in the same repo

An unused dependency can still break things when it ships a pytest plugin. `deepeval` was
never imported anywhere in the code, but its pytest plugin loaded automatically at
collection. The plugin imported `langchain.schema`, which no longer exists in langchain
1.x, so test collection failed. The fix was to remove the package. "Not imported" does
not mean "not loaded" when a package registers entry points.

## See Also
- [[Listen-Wiseer Project]] — instance-of (where both traps live)
- [[Silent Failure Catalogue]] — extends (a crash with no diagnostic signal)
- [[Index Pin Applies Only to Direct Dependencies]] (another packaging trap from the same repo)
