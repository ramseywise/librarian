"""Workflow-loop facts: where work actually sits in groom -> ... -> ship.

Two independent records describe the same work item and neither is authoritative:

* the **plan doc** carries a `Status:` line (the canonical 9-member enum), and
* the **GitHub issue** carries a workflow label (`backlog`, `ready`, ...).

Nothing keeps them in step, so they drift — a plan reaching `EXECUTED` while its issue
still reads `in-progress` is invisible until someone reads both. This module joins them
and reports the disagreements. It is a *reporting* surface: it makes drift visible so a
human acts on it, and deliberately never edits either side.

The status parser here mirrors `~/.claude/hooks/plan_status_validate.sh` exactly —
same tolerant regex, same "first whitespace-delimited token" rule. If the two disagree,
the tab would report drift the hook does not enforce (or hide drift it does), which is
worse than no tab. See ramseywise/librarian#91.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import structlog

log = structlog.get_logger(__name__)

# The canonical enum (ramseywise/guacamayo#74, enforced since #79). Order is the
# pipeline order, which is also the order the dashboard renders them in.
CANONICAL_STATUSES: tuple[str, ...] = (
    "RESEARCH",
    "RESEARCHED",
    "PLANNED",
    "REFINED",
    "READY",
    "IN_PROGRESS",
    "EXECUTED",
    "COMPLETE",
    "SUPERSEDED",
)

# A plan in one of these is finished; an issue for it should not still be open.
TERMINAL_STATUSES = frozenset({"EXECUTED", "COMPLETE", "SUPERSEDED"})

# Workflow labels, in pipeline order (see ~/.claude/refs/agile.md).
WORKFLOW_LABELS: tuple[str, ...] = (
    "backlog",
    "refinement",
    "ready",
    "in-progress",
    "in-review",
    "blocked",
)

# Tolerant detection: leading whitespace and the bold key form (`**Status**:`) both
# occur in the corpus. Copied from plan_status_validate.sh:30 — keep in sync.
_STATUS_RE = re.compile(r"^[ \t]*(?:\*\*)?Status(?:\*\*)?:[ \t]*(.*)$")

# `Issue: #42` / `Issues: #42, #43` / `Issue: ramseywise/librarian#42`
_ISSUE_FIELD_RE = re.compile(r"^[ \t]*(?:\*\*)?Issues?(?:\*\*)?:[ \t]*(.*)$")
_ISSUE_NUM_RE = re.compile(r"#(\d+)")

# `AIT-22-research.md` -> ("AIT", 22)
_FILENAME_REF_RE = re.compile(r"^([A-Z]{2,4})-(\d+)")

# Companion fields the hook requires for two terminal states
# (plan_status_validate.sh:59-62). Same tolerant key form as the Status: line.
_COMPANION_FIELDS: dict[str, str] = {"EXECUTED": "Review", "SUPERSEDED": "Superseded-by"}


def _field_re(name: str) -> re.Pattern[str]:
    return re.compile(rf"^[ \t]*(?:\*\*)?{re.escape(name)}(?:\*\*)?:")


@dataclass(frozen=True)
class PlanDoc:
    """One plan doc's loop-relevant facts."""

    path: str
    repo: str
    status: str  # the raw first token; "" when the line is absent OR its value is blank
    suffix: str  # free text after the token; non-empty means non-conforming
    issue: int | None  # joined issue number, when derivable
    has_status: bool = False  # a Status: line exists, whatever it says
    missing_field: str = ""  # companion field the status requires but the doc lacks

    @property
    def conforming(self) -> bool:
        """True when the hook would let this doc through.

        Three rules, all from plan_status_validate.sh: the token is canonical, it carries
        no suffix, and the companion field its state requires is present. Dropping the
        third would make the tab report clean docs the hook blocks.

        A doc with no Status: line at all is not counted as non-conforming — the hook
        exits 0 on those too (plan_status_validate.sh:39-40), and flagging them here
        would make the tab stricter than the guard. A bare `Status:` with no value is a
        different case: the hook reaches its checks and rejects the empty token, so
        `has_status` has to be tracked separately from an empty `status`.
        """
        if not self.has_status:
            return True
        return self.status in CANONICAL_STATUSES and not self.suffix and not self.missing_field

    @property
    def problem(self) -> str:
        """Why the hook would reject this doc; "" when it would not."""
        if self.conforming:
            return ""
        if self.status not in CANONICAL_STATUSES:
            return f"{self.status or '(empty)'} is not a canonical state"
        if self.suffix:
            return f"Status: carries a suffix ({self.suffix!r})"
        return f"{self.status} requires a '{self.missing_field}:' line"


@dataclass(frozen=True)
class Drift:
    """A plan doc and its issue disagreeing about where the work sits."""

    repo: str
    path: str
    issue: int
    status: str
    label: str
    reason: str


def parse_plan_doc(path: Path, repo: str) -> PlanDoc:
    """Read one plan doc. Unreadable files yield an empty-status record, never raise."""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        log.warning("loop.plan_unreadable", path=str(path), error=str(exc))
        return PlanDoc(path=str(path), repo=repo, status="", suffix="", issue=None)

    status, suffix, has_status = "", "", False
    for line in lines:
        m = _STATUS_RE.match(line)
        if m:
            has_status = True
            value = m.group(1).strip()
            parts = value.split()
            status = parts[0] if parts else ""
            suffix = value[len(status) :].strip()
            break

    required = _COMPANION_FIELDS.get(status, "")
    missing = ""
    if required and not any(_field_re(required).match(ln) for ln in lines):
        missing = required

    issue = _extract_issue(lines, path.name)
    return PlanDoc(
        path=str(path),
        repo=repo,
        status=status,
        suffix=suffix,
        issue=issue,
        has_status=has_status,
        missing_field=missing,
    )


def _extract_issue(lines: list[str], filename: str) -> int | None:
    """Issue number from an `Issue:` field, else from a `PREFIX-N-` filename.

    Only ~35 of 126 docs carry an `Issue:` line and ~20 use the `PREFIX-N` filename
    convention, so most docs simply do not join. That is reported as coverage rather
    than papered over — an unjoinable doc is not drift.
    """
    for line in lines:
        m = _ISSUE_FIELD_RE.match(line)
        if m:
            nums = _ISSUE_NUM_RE.findall(m.group(1))
            if nums:
                return int(nums[0])
            break
    m = _FILENAME_REF_RE.match(filename)
    return int(m.group(2)) if m else None


def collect_plan_docs(workspace: Path) -> list[PlanDoc]:
    """Every live plan doc under `<workspace>/*/.claude/docs/plans/`.

    Scoped to that exact shape on purpose: librarian also holds *ingested snapshots* of
    other repos' plan docs under `data/raw/claude-docs/`, and counting those would
    double-count the corpus and resurrect statuses that were long since corrected.
    """
    docs: list[PlanDoc] = []
    if not workspace.exists():
        log.warning("loop.workspace_missing", path=str(workspace))
        return docs
    for repo_dir in sorted(p for p in workspace.iterdir() if p.is_dir()):
        plans = repo_dir / ".claude" / "docs" / "plans"
        if not plans.is_dir():
            continue
        for md in sorted(plans.glob("*.md")):
            docs.append(parse_plan_doc(md, repo_dir.name))
    return docs


def status_counts(docs: list[PlanDoc]) -> dict[str, int]:
    """Canonical status -> count. Every enum member is present, including zeros."""
    counts = dict.fromkeys(CANONICAL_STATUSES, 0)
    for d in docs:
        if d.status in counts:
            counts[d.status] += 1
    return counts


def label_counts(issues: list[dict[str, Any]]) -> dict[str, int]:
    """Workflow label -> count of OPEN issues carrying it.

    Closed issues are excluded: the loop view answers "where is work sitting now", and
    a closed issue is not sitting anywhere. An issue with two workflow labels counts
    once under each — that is itself a signal worth seeing.
    """
    counts = dict.fromkeys(WORKFLOW_LABELS, 0)
    for issue in issues:
        if (issue.get("state") or "").upper() != "OPEN":
            continue
        for label in (issue.get("labels") or "").split(","):
            label = label.strip()
            if label in counts:
                counts[label] += 1
    return counts


def detect_drift(docs: list[PlanDoc], issues: list[dict[str, Any]]) -> list[Drift]:
    """Plan docs whose Status disagrees with their issue's state or workflow label.

    Three disagreements are reported, each meaning work is misrepresented on one side:

    * a **terminal** plan (EXECUTED / COMPLETE / SUPERSEDED) whose issue is still open —
      the board shows work that is actually finished;
    * a **non-terminal** plan whose issue is already closed — the plan doc is the stale
      one. This is by far the most common shape in the live corpus (measured 2026-08-02:
      of 30 joinable docs, 28 pointed at a closed issue), because closing an issue is one
      command while updating a plan's `Status:` is a manual edit nothing prompts for;
    * an **IN_PROGRESS** plan whose open issue is not labelled `in-progress` or
      `in-review` — the board shows work as unstarted while it is underway.

    The first two are deliberately symmetric. Reporting only the first would have made
    the tab read "0 drift" against a corpus where nearly every joinable plan doc was
    stale — a detector that cannot fire on the dominant failure is worse than none.
    """
    by_key = {(i.get("repo"), i.get("number")): i for i in issues}
    drifts: list[Drift] = []
    for doc in docs:
        if doc.issue is None:
            continue
        issue = by_key.get((doc.repo, doc.issue))
        if issue is None:
            continue
        state = (issue.get("state") or "").upper()
        labels = {label.strip() for label in (issue.get("labels") or "").split(",")}
        workflow = sorted(labels & set(WORKFLOW_LABELS))
        label = ", ".join(workflow) if workflow else "(none)"

        if doc.status in TERMINAL_STATUSES and state == "OPEN":
            drifts.append(
                Drift(
                    repo=doc.repo,
                    path=doc.path,
                    issue=doc.issue,
                    status=doc.status,
                    label=label,
                    reason=f"plan is {doc.status} but issue is still open",
                )
            )
        elif doc.status and doc.status not in TERMINAL_STATUSES and state == "CLOSED":
            drifts.append(
                Drift(
                    repo=doc.repo,
                    path=doc.path,
                    issue=doc.issue,
                    status=doc.status,
                    label=label,
                    reason=f"issue is closed but plan is still {doc.status}",
                )
            )
        elif (
            doc.status == "IN_PROGRESS"
            and state == "OPEN"
            and not (labels & {"in-progress", "in-review"})
        ):
            drifts.append(
                Drift(
                    repo=doc.repo,
                    path=doc.path,
                    issue=doc.issue,
                    status=doc.status,
                    label=label,
                    reason="plan is IN_PROGRESS but issue is not labelled in-progress/in-review",
                )
            )
    return drifts


def non_conforming(docs: list[PlanDoc]) -> list[PlanDoc]:
    """Docs whose Status: the hook would reject.

    Non-empty only for docs untouched since the guard landed — the hook fires on
    Write/Edit, so a doc nobody has edited keeps its pre-enum value indefinitely.
    """
    return [d for d in docs if not d.conforming]


def collect_issues(repo_name: str, owner: str = "ramseywise") -> list[dict[str, Any]]:
    """Issue facts via `gh`. Returns [] when gh is absent or the repo has no remote.

    Mirrors `gitstore.collect_prs`. Labels are stored as a comma-joined string rather
    than a join table: the only query is "which workflow label does this carry", and a
    second table for a handful of known labels would not earn its keys.
    """
    if not shutil.which("gh"):
        log.info("loop.gh_missing", repo=repo_name)
        return []
    try:
        out = subprocess.run(
            [
                "gh",
                "issue",
                "list",
                "-R",
                f"{owner}/{repo_name}",
                "--state",
                "all",
                "--limit",
                "300",
                "--json",
                "number,title,state,labels,createdAt,closedAt",
            ],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        log.warning("loop.gh_failed", repo=repo_name, error=str(exc))
        return []
    if out.returncode != 0 or not out.stdout.strip():
        return []
    try:
        payload = json.loads(out.stdout)
    except json.JSONDecodeError:
        log.warning("loop.issue_parse_failed", repo=repo_name)
        return []

    rows: list[dict[str, Any]] = []
    for issue in payload:
        labels = ",".join(sorted(lbl.get("name", "") for lbl in (issue.get("labels") or [])))
        rows.append(
            {
                "repo": repo_name,
                "number": issue.get("number", 0),
                "title": issue.get("title", ""),
                "state": (issue.get("state") or "").upper(),
                "labels": labels,
                "created_date": (issue.get("createdAt") or "")[:10],
                "closed_date": (issue.get("closedAt") or "")[:10],
            }
        )
    return rows
