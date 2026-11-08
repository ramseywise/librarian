"""librarian.wiki.telemetry against a fixture wiki with known numbers.

Fixture graph (edges are distinct directed page pairs):

    lonely -> hub <-> spoke-one        island-one <-> island-two
              hub -> spoke-two

Six scored pages, six edges, components of 4 and 2. `lonely` is the only orphan: the
tombstone and _index.md both link to it and must not count. All names here are made up.
"""

from __future__ import annotations

import itertools
import json
import subprocess
from datetime import date, timedelta
from pathlib import Path

import pytest

from librarian.wiki.telemetry import (
    METRICS_MAX_ROWS,
    OPERATIONS_KEEP_FULL,
    compute_stats,
    main,
    roll_operations,
)

TODAY = date(2026, 11, 5)
PRIVATE_TITLE = "Acme Secret Roadmap"
PRIVATE_STEM = "acme-roadmap-internal"
SHORT_PRIVATE_TITLE = "Acme Notes"
REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "wiki-lint.sh"


def filler(n: int) -> str:
    return " ".join(["word"] * n)


_summary_ids = itertools.count()


def write_page(
    wiki: Path,
    rel: str,
    title: str,
    body: str,
    *,
    tags: str = "[rag, concept]",
    updated: date = TODAY,
) -> None:
    path = wiki / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    # Unique words per page: identical boilerplate summaries would read as near-duplicates.
    n = next(_summary_ids)
    path.write_text(
        f"---\ntitle: {title}\ntags: {tags}\nsummary: Fixture q{n}a q{n}b q{n}c q{n}d\n"
        f"updated: {updated.isoformat()}\nsources: []\n---\n\n{body}\n"
    )


@pytest.fixture
def wiki(tmp_path: Path) -> Path:
    root = tmp_path / "wiki"
    long = filler(200)
    write_page(
        root,
        "rag/hub.md",
        "Hub Page",
        f"{long}\n\n## See Also\n- [[Spoke One]] — extends\n- [[Spoke Two]]\n\n## Later\n- [[Spoke One]]",
    )
    write_page(
        root, "rag/spoke-one.md", "Spoke One", f"{long}\n\n## See Also\n- [[Hub Page]] — related"
    )
    # Exactly 199 words: the only stub. Exactly 90 days old: the only stale page.
    write_page(
        root, "eval/spoke-two.md", "Spoke Two", filler(199), updated=TODAY - timedelta(days=90)
    )
    write_page(
        root,
        "eval/island-one.md",
        "Island One",
        f"{long}\n\n## See Also\n- [[Island Two]] — depends-on",
    )
    write_page(root, "eval/island-two.md", "Island Two", f"{long} [[island-one]] [[Island One]]")
    # 200 words and exactly 60 days old: on the healthy side of both boundaries.
    write_page(
        root,
        "meta/lonely.md",
        "Lonely Page",
        f"{filler(198)} [[Hub Page]] x",
        updated=TODAY - timedelta(days=60),
    )
    write_page(
        root,
        "rag/old-page.md",
        "Old Page",
        "Retired. See [[Lonely Page]]",
        tags="[rag, tombstone]",
        updated=TODAY - timedelta(days=400),
    )
    (root / "_index.md").write_text("---\ntitle: Index\n---\n\n[[Lonely Page]]\n")
    (root / "_conflicts.md").write_text(
        "**Status:** Unresolved — needs human review\n\n"
        "**Status:** Resolved — 2026-07-17\n\n"
        "> writes `Status: SUPERSEDED`\n"
    )
    write_page(
        root,
        f"private/{PRIVATE_STEM}.md",
        PRIVATE_TITLE,
        f"{long} [[Lonely Page]]",
        tags="[private, concept]",
    )
    write_page(root, "private/acme-notes.md", SHORT_PRIVATE_TITLE, long, tags="[private, concept]")
    return root


@pytest.fixture
def telemetry(tmp_path: Path) -> Path:
    return tmp_path / "telemetry"


def run(argv: list[str], wiki: Path, telemetry: Path) -> int:
    command, *rest = argv
    return main(
        [
            command,
            "--wiki-dir",
            str(wiki),
            "--telemetry-dir",
            str(telemetry),
            "--today",
            TODAY.isoformat(),
            *rest,
        ]
    )


def assert_no_private_name(text: str) -> None:
    lowered = text.lower()
    for name in (PRIVATE_TITLE, SHORT_PRIVATE_TITLE, PRIVATE_STEM, "acme-notes"):
        assert name.lower() not in lowered


def add_leaks(wiki: Path) -> None:
    """Line numbers are 1-based in the whole file; frontmatter is 7 lines plus a blank."""
    write_page(wiki, "rag/leaky-link.md", "Leaky Link", f"fine line\nsee [[{PRIVATE_TITLE}]] here")
    write_page(
        wiki, "rag/leaky-title.md", "Leaky Title", f"fine\nwe discussed {PRIVATE_TITLE} today"
    )
    write_page(
        wiki, "rag/short-title.md", "Short Title", f"we discussed {SHORT_PRIVATE_TITLE} today"
    )


class TestStats:
    def test_exact_rates(self, wiki: Path) -> None:
        stats = compute_stats(wiki, TODAY)
        metrics = stats["metrics"]
        assert stats["pages"] == 6
        assert metrics["orphan_rate"] == {"value": round(1 / 6, 4), "status": "broken"}
        assert metrics["average_degree"] == {"value": 2.0, "status": "broken"}
        assert metrics["main_component"] == {"value": round(4 / 6, 4), "status": "watch"}
        assert metrics["stale_rate"] == {"value": round(1 / 6, 4), "status": "report"}
        # hub 2 + spoke-one 1 + island-one 1 = 4 entries. Typed: hub's extends and spoke-one's
        # related. depends-on isn't canonical, and the bullet under ## Later isn't See Also.
        assert metrics["typed_link_rate"] == {"value": 0.5, "status": "healthy"}
        assert metrics["stub_rate"] == {"value": round(1 / 6, 4), "status": "watch"}

    def test_page_count_hubs_domains_conflicts(self, wiki: Path) -> None:
        stats = compute_stats(wiki, TODAY)
        assert stats["hubs"][0] == {
            "page": "rag/hub",
            "title": "Hub Page",
            "inbound": 2,
            "outbound": 2,
        }
        assert stats["domains"] == {"eval": 3, "meta": 1, "rag": 2}
        assert stats["open_conflicts"] == 1

    def test_private_tombstone_and_underscore_links_make_no_edge(self, wiki: Path) -> None:
        pages = {h["page"]: h for h in compute_stats(wiki, TODAY)["hubs"]}
        assert pages["meta/lonely"]["inbound"] == 0

    def test_link_into_private_adds_no_edge(self, wiki: Path) -> None:
        before = compute_stats(wiki, TODAY)["metrics"]["average_degree"]["value"]
        (wiki / "rag" / "hub.md").write_text(
            (wiki / "rag" / "hub.md").read_text() + f"\n[[{PRIVATE_TITLE}]]\n"
        )
        assert compute_stats(wiki, TODAY)["metrics"]["average_degree"]["value"] == before

    def test_healthy_bands(self, tmp_path: Path) -> None:
        root = tmp_path / "ring"
        names = [f"page-{i}" for i in range(5)]
        for i, name in enumerate(names):
            others = " ".join(f"[[{n}]]" for n in names if n != name)
            see_also = f"## See Also\n- [[{names[(i + 1) % 5]}]] — extends"
            write_page(root, f"rag/{name}.md", name, f"{filler(250)} {others}\n\n{see_also}")
        metrics = compute_stats(root, TODAY)["metrics"]
        assert metrics["orphan_rate"]["status"] == "healthy"
        assert metrics["average_degree"] == {"value": 8.0, "status": "healthy"}
        assert metrics["main_component"] == {"value": 1.0, "status": "healthy"}
        assert metrics["stub_rate"]["status"] == "healthy"

    def test_broken_yaml_page_does_not_crash_and_is_counted(self, wiki: Path) -> None:
        (wiki / "rag" / "broken.md").write_text("---\ntitle: Broken: Page\ntags: [\n---\n\nbody\n")
        stats = compute_stats(wiki, TODAY)
        assert stats["pages"] == 7
        assert stats["unparsed_pages"] == 1

    def test_empty_wiki_reports_no_data(self, tmp_path: Path) -> None:
        (tmp_path / "empty").mkdir()
        stats = compute_stats(tmp_path / "empty", TODAY)
        assert stats["pages"] == 0
        assert stats["metrics"]["orphan_rate"] == {"value": 0.0, "status": "no-data"}

    def test_json_and_text_output_never_name_private(
        self, wiki: Path, telemetry: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        add_leaks(wiki)
        assert run(["stats", "--json"], wiki, telemetry) == 0
        out = capsys.readouterr().out
        assert json.loads(out)["pages"] == 9
        assert_no_private_name(out)
        assert run(["stats"], wiki, telemetry) == 0
        text = capsys.readouterr().out
        assert "Orphan rate" in text
        assert_no_private_name(text)


class TestSnapshot:
    def test_same_day_replaces_and_new_day_appends(self, wiki: Path, telemetry: Path) -> None:
        assert run(["snapshot"], wiki, telemetry) == 0
        assert run(["snapshot"], wiki, telemetry) == 0
        path = telemetry / "metrics.jsonl"
        assert len(path.read_text().splitlines()) == 1
        main(
            [
                "snapshot",
                "--wiki-dir",
                str(wiki),
                "--telemetry-dir",
                str(telemetry),
                "--today",
                "2026-11-06",
            ]
        )
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        assert [r["date"] for r in rows] == ["2026-11-05", "2026-11-06"]
        assert rows[0]["metrics"]["average_degree"]["value"] == 2.0

    def test_row_records_the_graph_shape_as_plain_numbers(
        self, wiki: Path, telemetry: Path
    ) -> None:
        run(["snapshot"], wiki, telemetry)
        row = json.loads((telemetry / "metrics.jsonl").read_text().splitlines()[-1])
        assert isinstance(row["clusters"], int)
        assert isinstance(row["unsettled"], int)
        assert 0.0 <= row["stability"] <= 1.0
        # Report-only: not a banded metric, so the health strip never colours it.
        assert not {"clusters", "unsettled", "stability"} & set(row["metrics"])

    def test_row_cap_drops_oldest(self, wiki: Path, telemetry: Path) -> None:
        telemetry.mkdir()
        old = [
            {"date": (TODAY - timedelta(days=i + 1)).isoformat()}
            for i in range(METRICS_MAX_ROWS + 3)
        ]
        (telemetry / "metrics.jsonl").write_text("".join(json.dumps(r) + "\n" for r in old))
        run(["snapshot"], wiki, telemetry)
        rows = (telemetry / "metrics.jsonl").read_text().splitlines()
        assert len(rows) == METRICS_MAX_ROWS
        assert json.loads(rows[-1])["date"] == TODAY.isoformat()
        assert json.loads(rows[0])["date"] == (TODAY - timedelta(days=35)).isoformat()

    def test_row_has_no_private_content(self, wiki: Path, telemetry: Path) -> None:
        add_leaks(wiki)
        run(["snapshot"], wiki, telemetry)
        assert_no_private_name((telemetry / "metrics.jsonl").read_text())

    def test_bad_line_stops_rather_than_rewrites(self, wiki: Path, telemetry: Path) -> None:
        telemetry.mkdir()
        (telemetry / "metrics.jsonl").write_text("<<<<<<< HEAD\n")
        assert run(["snapshot"], wiki, telemetry) == 2
        assert (telemetry / "metrics.jsonl").read_text() == "<<<<<<< HEAD\n"


class TestCheck:
    def test_clean_wiki_passes(
        self, wiki: Path, telemetry: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run(["check"], wiki, telemetry) == 0
        assert "0 blocker(s), 0 warning(s)" in capsys.readouterr().out

    def test_link_blocks_title_warns_and_output_is_clean(
        self, wiki: Path, telemetry: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        add_leaks(wiki)
        assert run(["check"], wiki, telemetry) == 1
        out = capsys.readouterr().out
        assert "BLOCKER" in out and "leaky-link.md:10" in out
        assert "WARN" in out and "leaky-title.md:10" in out
        assert "short-title" not in out  # a title under three words is ignored
        assert_no_private_name(out)

    def test_title_mention_alone_does_not_fail(self, wiki: Path, telemetry: Path) -> None:
        write_page(wiki, "rag/leaky-title.md", "Leaky Title", f"on {PRIVATE_TITLE.lower()} today")
        assert run(["check"], wiki, telemetry) == 0

    def test_link_forms_that_reach_private(self, wiki: Path, telemetry: Path) -> None:
        for i, link in enumerate(
            [f"[[{PRIVATE_STEM}]]", f"[[{PRIVATE_TITLE}|alias]]", f"[[private/{PRIVATE_STEM}.md]]"]
        ):
            write_page(wiki, "rag/leak.md", "Leak", link)
            assert run(["check"], wiki, telemetry) == 1, (i, link)

    def test_underscore_files_and_tombstones_are_scanned(
        self, wiki: Path, telemetry: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        (wiki / "_relink_suggestions.md").write_text(f"- [[{PRIVATE_STEM}]] 0.61\n")
        write_page(wiki, "rag/old.md", "Old", f"[[{PRIVATE_STEM}]]", tags="[rag, tombstone]")
        assert run(["check"], wiki, telemetry) == 1
        out = capsys.readouterr().out
        assert "_relink_suggestions.md:1" in out and "old.md:" in out

    def test_public_page_of_same_name_wins(self, wiki: Path, telemetry: Path) -> None:
        write_page(wiki, "rag/same.md", PRIVATE_TITLE, f"[[{PRIVATE_TITLE}]] and {PRIVATE_TITLE}")
        assert run(["check"], wiki, telemetry) == 0

    def test_tracked_telemetry_scanned_and_asked_is_not(
        self, wiki: Path, telemetry: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        telemetry.mkdir()
        (telemetry / "asked.jsonl").write_text(json.dumps({"topic": f"[[{PRIVATE_TITLE}]]"}) + "\n")
        assert run(["check"], wiki, telemetry) == 0
        capsys.readouterr()
        (telemetry / "operations.jsonl").write_text(
            json.dumps({"detail": f"private/{PRIVATE_STEM}.md"}) + "\n"
        )
        assert run(["check"], wiki, telemetry) == 1
        out = capsys.readouterr().out
        assert "operations.jsonl:1" in out
        assert_no_private_name(out)

    def test_private_missing_exits_zero_with_a_note(
        self, tmp_path: Path, telemetry: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        root = tmp_path / "public-only"
        write_page(root, "rag/page.md", "Page", "[[Anything]]")
        assert run(["check"], root, telemetry) == 0
        assert "no private/" in capsys.readouterr().out

    def test_private_as_symlink_is_followed(
        self, tmp_path: Path, wiki: Path, telemetry: Path
    ) -> None:
        """The worktree layout: data/wiki/private links into the main checkout."""
        moved = tmp_path / "elsewhere"
        (wiki / "private").rename(moved)
        (wiki / "private").symlink_to(moved, target_is_directory=True)
        add_leaks(wiki)
        assert run(["check"], wiki, telemetry) == 1
        assert compute_stats(wiki, TODAY)["pages"] == 9

    def test_single_file_mode(
        self, wiki: Path, telemetry: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        add_leaks(wiki)
        hub = str(wiki / "rag" / "hub.md")
        assert run(["check", "--file", hub], wiki, telemetry) == 0
        capsys.readouterr()
        leaky = str(wiki / "rag" / "leaky-link.md")
        assert run(["check", "--file", leaky], wiki, telemetry) == 1
        out = capsys.readouterr().out
        assert "leaky-link.md:10" in out
        assert_no_private_name(out)
        # A title mention is the whole-wiki check's job, not the hook's.
        assert run(["check", "--file", str(wiki / "rag" / "leaky-title.md")], wiki, telemetry) == 0


class TestSensitiveCheck:
    def _page(self, wiki: Path, text: str) -> Path:
        path = wiki / "rag" / "public-note.md"
        path.write_text(f"---\ntitle: Public Note\ntags: [rag, concept]\n---\n\n{text}\n")
        return path

    def test_secret_blocks_in_whole_wiki_and_hook_checks(self, wiki: Path, telemetry: Path) -> None:
        secret = "sk-" + "a" * 30
        page = self._page(wiki, f"key {secret}")
        assert run(["check"], wiki, telemetry) == 1
        assert run(["check", "--file", str(page)], wiki, telemetry) == 1

    def test_listed_term_blocks(self, wiki: Path, telemetry: Path) -> None:
        (wiki / "private" / "_sensitive-terms.txt").write_text("Globex\n")
        page = self._page(wiki, "we did this at globex")
        assert run(["check"], wiki, telemetry) == 1
        assert run(["check", "--file", str(page)], wiki, telemetry) == 1

    def test_contact_details_warn_only(self, wiki: Path, telemetry: Path) -> None:
        self._page(wiki, "mail jane@realcorp.io")
        assert run(["check"], wiki, telemetry) == 0

    def test_private_stem_inside_a_raw_path_blocks(self, wiki: Path, telemetry: Path) -> None:
        stem = next(p.stem for p in (wiki / "private").rglob("*.md"))
        page = self._page(wiki, f"sources: data/raw/repos/x/.claude--research--{stem}-prep.md")
        assert run(["check"], wiki, telemetry) == 1
        assert run(["check", "--file", str(page)], wiki, telemetry) == 1


class TestLog:
    def test_appends_row(self, wiki: Path, telemetry: Path) -> None:
        assert run(["log", "ingest", "data/raw/web/x.md -> 2 new"], wiki, telemetry) == 0
        row = json.loads((telemetry / "operations.jsonl").read_text())
        assert row == {"date": "2026-11-05", "op": "ingest", "detail": "data/raw/web/x.md -> 2 new"}

    @pytest.mark.parametrize(
        "detail",
        [
            f"merged {PRIVATE_TITLE} into x",
            f"merged {SHORT_PRIVATE_TITLE} into x",  # any length here, unlike check's WARN
            f"merged {PRIVATE_TITLE.upper()} into x",
            f"merged {PRIVATE_STEM} into x",
            f"wrote private/{PRIVATE_STEM}.md",
            f"wrote data/wiki/private/{PRIVATE_STEM}.md",
            "wrote data/wiki/private/some-new-page.md",
        ],
    )
    def test_refuses_private_names(
        self,
        wiki: Path,
        telemetry: Path,
        detail: str,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        assert run(["log", "ingest", detail], wiki, telemetry) == 2
        assert not (telemetry / "operations.jsonl").exists()
        captured = capsys.readouterr()
        assert_no_private_name(captured.out + captured.err)

    def test_word_inside_a_longer_word_is_not_a_title_match(
        self, wiki: Path, telemetry: Path
    ) -> None:
        assert run(["log", "ingest", "Acme Notesworthy things"], wiki, telemetry) == 0

    def test_rejects_multiword_op(self, wiki: Path, telemetry: Path) -> None:
        assert run(["log", "two words", "detail"], wiki, telemetry) == 2

    @pytest.mark.parametrize(
        "detail", ["mail bob@acme.io", "token sk-ant-abcdefghijklmnopqrstuvwx"]
    )
    def test_refuses_contact_details_and_secrets(
        self, wiki: Path, telemetry: Path, detail: str
    ) -> None:
        assert run(["log", "ingest", detail], wiki, telemetry) == 2

    def test_accumulator_rolls_older_entries_by_month(self) -> None:
        rows = [
            {"date": f"2026-09-{i + 1:02d}", "op": "ingest", "detail": str(i)} for i in range(3)
        ]
        rows += [{"date": "2026-10-01", "op": "compact", "detail": "c"}]
        rows += [
            {"date": "2026-11-01", "op": "ingest", "detail": str(i)}
            for i in range(OPERATIONS_KEEP_FULL)
        ]
        rolled = roll_operations(rows)
        assert rolled[0] == {"month": "2026-09", "count": 3, "ops": {"ingest": 3}}
        assert rolled[1] == {"month": "2026-10", "count": 1, "ops": {"compact": 1}}
        assert rolled[2:] == rows[4:]
        assert len(rolled[2:]) == OPERATIONS_KEEP_FULL

    def test_rollup_merges_into_existing_month_row(self) -> None:
        existing = {"month": "2026-09", "count": 2, "ops": {"ingest": 2}}
        rows = [existing, {"date": "2026-09-30", "op": "compact", "detail": "c"}]
        rows += [{"date": "2026-11-01", "op": "x", "detail": ""}] * OPERATIONS_KEEP_FULL
        assert roll_operations(rows)[0] == {
            "month": "2026-09",
            "count": 3,
            "ops": {"ingest": 2, "compact": 1},
        }

    def test_under_ceiling_is_untouched(self) -> None:
        rows = [{"date": "2026-11-01", "op": "x", "detail": ""}] * OPERATIONS_KEEP_FULL
        assert roll_operations(rows) == rows


class TestLogCounts:
    """`log --counts` derives the four numbers from the diff against HEAD."""

    @pytest.fixture
    def repo(self, tmp_path: Path) -> Path:
        root = tmp_path / "repo"
        git = lambda *a: subprocess.run(["git", *a], cwd=root, check=True, capture_output=True)  # noqa: E731
        (root / "wiki" / "rag").mkdir(parents=True)
        git("init", "-q")
        git("config", "user.email", "t@example.com")
        git("config", "user.name", "Tester")
        (root / "wiki" / "rag" / "old.md").write_text("Body [[A]].\n")
        (root / "wiki" / "_conflicts.md").write_text("## Open Conflicts\n")
        git("add", "-A")
        git("commit", "-q", "-m", "seed")
        return root

    def log(self, repo: Path, telemetry: Path, *detail: str) -> int:
        wiki = repo / "wiki"
        return main(["log", "ingest", *detail, "--counts", "--wiki-dir", str(wiki),
                     "--telemetry-dir", str(telemetry), "--repo-root", str(repo),
                     "--today", "2026-11-05"])  # fmt: skip

    def test_counts_new_updated_links_and_conflicts(self, repo: Path, telemetry: Path) -> None:
        wiki = repo / "wiki"
        (wiki / "rag" / "old.md").write_text("Body [[A]], now [[B]].\n\n## See Also\n- [[C]]\n")
        (wiki / "rag" / "new.md").write_text("New [[A]] and [[B]].\n")
        (wiki / "_index.md").write_text("[[Ignored]] [[Too]]\n")
        (wiki / "_conflicts.md").write_text("## Open Conflicts\n\n## Conflict: X — 2026-11-05\n")
        subprocess.run(["git", "add", "wiki/rag/new.md"], cwd=repo, check=True)  # staged or not
        assert self.log(repo, telemetry, "data/raw/web/ (2 files)") == 0
        row = json.loads((telemetry / "operations.jsonl").read_text())
        assert row["detail"] == (
            "data/raw/web/ (2 files) -> 1 new, 1 updated, 4 links, 1 conflicts"
        )

    def test_refuses_hand_written_counts(self, repo: Path, telemetry: Path) -> None:
        assert self.log(repo, telemetry, "x.md -> 2 new") == 2
        assert not (telemetry / "operations.jsonl").exists()


def write_retrieval_log(path: Path, rows: list[dict[str, object]]) -> Path:
    path.write_text("".join(json.dumps(r) + "\n" for r in rows) + "not json\n")
    return path


def search(query: str, n: int, ts: str, tool: str = "search_wiki", **extra: object) -> dict:
    return {"ts": f"{ts}T10:00:00+00:00", "tool": tool, "query": query, "n_results": n, **extra}


class TestGaps:
    def gaps(self, wiki: Path, telemetry: Path, log: Path, courses: Path) -> int:
        return run(
            ["gaps", "--retrieval-log", str(log), "--courses-dir", str(courses)], wiki, telemetry
        )

    def test_asked_section(
        self, tmp_path: Path, wiki: Path, telemetry: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        run(["ask", "graph databases"], wiki, telemetry)
        run(["ask", "Graph  Databases"], wiki, telemetry)
        run(["ask", "hub page"], wiki, telemetry)  # a page exists now: answered
        run(["ask", f"what about {PRIVATE_TITLE}"], wiki, telemetry)
        log = write_retrieval_log(
            tmp_path / "retrieval.jsonl",
            [
                search("never found", 0, "2026-09-01"),
                search("never found", 0, "2026-10-01"),
                search("found later", 0, "2026-09-02"),
                search("found later", 3, "2026-09-03"),
                search("broken index", 0, "2026-09-04", degraded=["no_fts"]),
                search("harness traffic", 0, "2026-09-05", tool="eval"),
                search("in courses", 0, "2026-09-06", tool="search_courses"),
                {
                    "ts": "2026-09-07T10:00:00+00:00",
                    "tool": "read_page",
                    "path": "x",
                    "found": True,
                },
            ],
        )
        assert self.gaps(wiki, telemetry, log, tmp_path / "no-courses") == 0
        text = (telemetry / "gaps.md").read_text()
        assert "- never found | first seen 2026-09-01 | count 2" in text
        assert "- in courses | first seen 2026-09-06 | count 1" in text
        assert "- graph databases | first seen 2026-11-05 | count 2" in text
        for absent in ("found later", "broken index", "harness traffic", "hub page"):
            assert absent not in text
        assert "Skipped 1 empty results from degraded retrieval." in text
        assert "Withheld 1 that name a private page." in text
        assert "Floor:" in text
        out = capsys.readouterr().out
        assert "graph databases" in out and "never found" in out
        assert_no_private_name(text + out)

    def test_missing_log_and_courses_tolerated(
        self, tmp_path: Path, wiki: Path, telemetry: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        missing = tmp_path / "absent"
        assert self.gaps(wiki, telemetry, missing, missing) == 0
        assert "## Asked, not answered" in (telemetry / "gaps.md").read_text()
        assert "Top 0" in capsys.readouterr().out

    def test_course_sections(self, tmp_path: Path, wiki: Path, telemetry: Path) -> None:
        pytest.importorskip("fastapi")
        courses = tmp_path / "courses"

        def write_lesson(rel: str, front: str, body: str) -> None:
            (courses / rel).parent.mkdir(parents=True, exist_ok=True)
            (courses / rel).write_text(f"---\ntitle: Lesson\n{front}---\n\n{body}\n")

        write_lesson("c1/covered/one.md", "wiki: [hub]\n", "[[Hub Page]] and [[Missing Topic]]")
        write_lesson("c1/covered/two.md", "wiki: [missing-topic]\n", "`[[not, a, link]]`")
        write_lesson(
            "c1/empty/three.md", "", f"[[{PRIVATE_TITLE}]] [[Old Page]]\n```\n[[in fence]]\n```"
        )
        write_lesson("c1/00-start-here/four.md", "", "skipped module")
        log = tmp_path / "absent"

        assert self.gaps(wiki, telemetry, log, courses) == 0
        text = (telemetry / "gaps.md").read_text()
        assert "- c1/empty: empty | first seen 2026-11-05 | count 1" in text
        assert "c1/covered" not in text and "00-start-here" not in text
        assert "| count 2" in text and "Missing Topic" in text
        assert "in fence" not in text and "not, a, link" not in text
        assert "Old Page" not in text
        assert "Withheld 2 that point at a private or retired page." in text
        assert_no_private_name(text)

        # First seen survives a regeneration on a later day.
        main(
            [
                "gaps",
                "--wiki-dir",
                str(wiki),
                "--telemetry-dir",
                str(telemetry),
                "--retrieval-log",
                str(log),
                "--courses-dir",
                str(courses),
                "--today",
                "2026-12-01",
            ]
        )
        later = (telemetry / "gaps.md").read_text()
        assert "- c1/empty: empty | first seen 2026-11-05 | count 1" in later


class TestHook:
    """The hook resolves paths from the repo root, so it runs against a copy of that layout."""

    def run_hook(self, tmp_path: Path, wiki: Path, page: str) -> str:
        root = tmp_path / "hookrepo"
        if not root.exists():
            (root / "data").mkdir(parents=True)
            (root / "data" / "wiki").symlink_to(wiki, target_is_directory=True)
            (root / ".venv").symlink_to(REPO / ".venv", target_is_directory=True)
        proc = subprocess.run(
            ["bash", str(HOOK)],
            cwd=root,
            env={"PATH": "/usr/bin:/bin:/usr/local/bin", "CLAUDE_TOOL_INPUT_FILE_PATH": page},
            capture_output=True,
            text=True,
            check=True,
        )
        return proc.stderr

    @pytest.mark.skipif(not (REPO / ".venv" / "bin" / "python").exists(), reason="needs the venv")
    def test_flags_link_into_private_without_naming_it(self, tmp_path: Path, wiki: Path) -> None:
        add_leaks(wiki)
        err = self.run_hook(tmp_path, wiki, "data/wiki/rag/leaky-link.md")
        assert "PRIVATE LEAK" in err
        assert "leaky-link.md:10" in err

    @pytest.mark.skipif(not (REPO / ".venv" / "bin" / "python").exists(), reason="needs the venv")
    def test_clean_page_and_private_page_pass(self, tmp_path: Path, wiki: Path) -> None:
        err = self.run_hook(tmp_path, wiki, "data/wiki/rag/hub.md")
        assert "PRIVATE LEAK" not in err
        write_page(
            wiki, "private/links.md", "Links", f"[[{PRIVATE_TITLE}]]", tags="[private, concept]"
        )
        assert "PRIVATE LEAK" not in self.run_hook(tmp_path, wiki, "data/wiki/private/links.md")


def ont_page(
    wiki: Path, rel: str, title: str, links: str = "", *, tags: str = "[rag, concept]", summary: str
) -> None:
    path = wiki / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\ntitle: {title}\ntags: {tags}\nsummary: {summary}\n"
        f"updated: {TODAY.isoformat()}\nsources: []\n---\n\n{filler(200)}\n\n## See Also\n{links}\n"
    )


def ontology_lines(out: str) -> list[str]:
    return [line for line in out.splitlines() if " ONT00" in line]


class TestOntologyChecks:
    @pytest.fixture
    def tree(self, tmp_path: Path) -> Path:
        return tmp_path / "wiki"

    def test_cycle_reported_once_and_chain_is_not(
        self, tree: Path, telemetry: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # a -> b -> c -> a is a cycle (X is a prerequisite for the page it is written on);
        # d -> e -> f is an acyclic chain.
        ont_page(
            tree, "rag/a.md", "Alpha One", "- [[Gamma Three]] — prerequisite-for", summary="aa"
        )
        ont_page(tree, "rag/b.md", "Beta Two", "- [[Alpha One]] — prerequisite-for", summary="bb")
        ont_page(tree, "rag/c.md", "Gamma Three", "- [[Beta Two]] — prerequisite-for", summary="cc")
        ont_page(tree, "rag/d.md", "Delta Four", "- [[Zed]]", summary="dd")
        ont_page(
            tree, "rag/e.md", "Epsilon Five", "- [[Delta Four]] — prerequisite-for", summary="ee"
        )
        ont_page(
            tree, "rag/f.md", "Zeta Six", "- [[Epsilon Five]] — prerequisite-for", summary="ff"
        )
        assert run(["check"], tree, telemetry) == 0  # a WARN never fails the exit code
        lines = ontology_lines(capsys.readouterr().out)
        assert len(lines) == 1
        assert lines[0].startswith("WARN ONT001") and "3 pages" in lines[0]
        assert "rag/a.md, rag/b.md, rag/c.md" in lines[0]
        assert "rag/d.md" not in lines[0]

    def test_instance_of_mutual_and_project_as_general(
        self, tree: Path, telemetry: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        ont_page(tree, "rag/p.md", "Pee Page", "- [[Ex Page]] — instance-of", summary="p")
        ont_page(tree, "rag/x.md", "Ex Page", "- [[Pee Page]] — instance-of", summary="x")
        # A project listing a pattern as its instance is reversed; the pattern listing the
        # project is the right way round and is not flagged.
        ont_page(
            tree,
            "projects/proj.md",
            "Some Project",
            "- [[Some Pattern]] — instance-of",
            tags="[projects, project]",
            summary="proj",
        )
        ont_page(
            tree,
            "patterns/pat.md",
            "Some Pattern",
            "- [[Other Project]] — instance-of",
            tags="[patterns, pattern]",
            summary="pat",
        )
        ont_page(
            tree,
            "projects/other.md",
            "Other Project",
            "",
            tags="[projects, project]",
            summary="other",
        )
        assert run(["check"], tree, telemetry) == 0
        lines = ontology_lines(capsys.readouterr().out)
        assert sorted(line.split()[1] for line in lines) == ["ONT002", "ONT003"]
        assert any("projects/proj.md lists patterns/pat.md" in line for line in lines)

    def test_near_duplicates_found_and_distinct_titles_not(
        self, tree: Path, telemetry: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        ont_page(
            tree,
            "rag/one.md",
            "Hybrid Search Fusion",
            summary="Combining sparse and dense retrieval scores with reciprocal rank fusion",
        )
        ont_page(
            tree,
            "rag/two.md",
            "Hybrid Search Fusion Methods",
            summary="Combining sparse and dense retrieval scores via reciprocal rank fusion",
        )
        ont_page(
            tree,
            "eval/three.md",
            "Judge Calibration",
            summary="Aligning an LLM grader with human labels",
        )
        assert run(["check"], tree, telemetry) == 0
        lines = ontology_lines(capsys.readouterr().out)
        assert len(lines) == 1 and "ONT004" in lines[0]
        assert "rag/one.md / rag/two.md" in lines[0]

    def test_private_and_tombstone_pages_are_excluded(
        self, tree: Path, telemetry: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        ont_page(tree, "rag/a.md", "Alpha One", "- [[Beta Two]] — prerequisite-for", summary="aa")
        ont_page(
            tree,
            "rag/b.md",
            "Beta Two",
            "- [[Alpha One]] — prerequisite-for",
            tags="[rag, tombstone]",
            summary="bb",
        )
        ont_page(
            tree,
            "private/secret.md",
            "Secret Cycle Page",
            "- [[Alpha One]] — prerequisite-for",
            tags="[private, concept]",
            summary="Hybrid Search Fusion retrieval scores",
        )
        ont_page(tree, "rag/c.md", "Hybrid Search Fusion", summary="Hybrid Search Fusion retrieval")
        ont_page(
            tree,
            "rag/d.md",
            "Hybrid Search Fusion",
            tags="[rag, tombstone]",
            summary="Hybrid Search Fusion retrieval",
        )
        assert run(["check"], tree, telemetry) == 0
        out = capsys.readouterr().out
        assert ontology_lines(out) == []
        assert "Secret Cycle Page" not in out and "private/secret" not in out
