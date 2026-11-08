"""Reader feedback: ratings on chat answers, reports on pages and lessons, unanswered questions.

One row per signal in the `feedback` table, owned by a user. Free-text notes are deletable by
their author, rows older than the retention window are pruned, and the admin summary and the
raw-source export (`librarian.ingest.feedback_export`) carry no emails or user ids. Imports only
`librarian.db` and config.
"""

from librarian.feedback.store import (
    KINDS,
    MAX_BODY,
    MAX_TARGET,
    Feedback,
    FeedbackError,
    delete,
    mine,
    prune,
    record,
    since,
)
from librarian.feedback.summary import summary

__all__ = [
    "KINDS",
    "MAX_BODY",
    "MAX_TARGET",
    "Feedback",
    "FeedbackError",
    "delete",
    "mine",
    "prune",
    "record",
    "since",
    "summary",
]
