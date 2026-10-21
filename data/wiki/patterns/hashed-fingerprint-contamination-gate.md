---
title: Hashed Fingerprint Contamination Gate
tags: [infra, eval, pattern]
summary: To prove a new repo carries none of a set of excluded material, make the first commit a gate that hashes normalized lines (safe to publish), checks enum and vocabulary sets by overlap and numeric profiles by match, runs the plaintext checks only locally against a quarantine folder, and is calibrated by first making it flag the known-contaminated old tree.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-10-09-clean-room-repo-plan.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-10-09-clean-room-repo-plan.md
  - data/raw/claude-docs/diskoe/docs/research/2026-10-09-ip-provenance-and-clean-room-plan.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-10-09-ip-provenance-and-clean-room-plan.md
---

# Hashed Fingerprint Contamination Gate

From a clean-room plan in the diskoe repo (2026-10-09): starting a new project that must
contain no code, prompt text, vocabulary, scoring numbers or spec text from a body of
material someone else owns. The goal was that the claim be **checkable by a machine, not
just asserted**. The mechanism is general: it fits licence clean-up, forking away from a
vendor codebase, or keeping test data out of a training corpus.

## Step 0: the gate comes before any code

1. **Quarantine folder outside every repo**: the excluded code, exported workflow JSON,
   spec docs. Read-only, never committed.
2. **Fingerprint generator** writes a file into the new repo with:
   - the SHA-256 of every normalized line (whitespace collapsed, at least 25 characters);
   - the SHA-256 of every **vocabulary set** (the sorted values of each enum, check
     constraint, allowed-values list);
   - the SHA-256 of each **numeric profile** (weight vectors, thresholds).

   Hashes reveal nothing about the content, so the fingerprint file can sit in a public
   repo.
3. **Three checks in the gate:**
   - **Line check**: hash every normalized line in the tree; any match fails. Runs in CI.
   - **Set check**: for every string union, enum, `CHECK (... IN (...))` and schema enum,
     fail when **50% or more** of its values appear in one excluded vocabulary set. A
     single common word doesn't fail; reusing the set does. Needs the sets in plain text,
     so it runs **locally only**.
   - **Numeric check**: fail when a numeric array or object matches an excluded profile
     after normalization.
4. **Calibrate against the contaminated tree.** Run it on the old repo first. It must flag
   every file the provenance audit listed. If it misses one, it isn't ready.

Line hashing alone misses the subtle forms of copying. A renamed-but-identical tag
vocabulary or a weight vector typed fresh passes a line check. That is why the set and
numeric checks exist.

## The audit that feeds it

The provenance audit that preceded the gate measured, for each original file, the share
of its non-blank lines still present **verbatim** in the current tree. That "kept %"
sorted files into near-verbatim (≥90%), partly derived (40–89%) and traces (<20%), and
gave the gate its target: 0% kept for every listed file.

## Port by allow-list, with a provenance log

- **Allow-list, not deny-list.** Copy in only modules known to be clean, one at a time,
  after cutting every import edge into excluded files. An import scan lists those edges.
- **New repo, no history.** History contains everything the tree no longer does.
- **`PROVENANCE.md`**, one row per module: "ported" (with an author-only `git log` and a
  0% overlap result) or "written fresh" (with the public source used, e.g. schema.org or
  the OSM spec, and the old file not consulted).
- **Rebuild fixtures from fresh data.** Fixtures holding the old material are
  contamination too.

## Limits

A true clean room separates the person who read the original from the person who
rewrites it. When the same person did both, a rewrite is **evidence** of independent
implementation, not proof. That is acceptable for small standard pieces (parsers,
resolvers), but a gate can't settle questions about who holds rights. Only an agreement
can.

## See Also
- [[Derive the Gate, Don't Copy It]] — related (gates as the mechanical form of a claim)
- [[Artifact Is Not Evidence: Push and Probe]] — related (a stated "clean" is not a measured one)
- [[Differential Parity Testing Against the Original]] — alternative-to (proving sameness vs. proving difference)
