"""Product measurement over chat telemetry, feedback and study state (phase 4b).

`librarian eval compare` (one experiment, variant by variant), `librarian metrics product`
(answers, grounding, ratings, spend and study counts) and `librarian metrics check-release`
(did grounding or the down-rating rate fall after a release). Read-only: nothing here writes to
the database, `logs/` or `data/`, and nothing promotes a variant.
"""
