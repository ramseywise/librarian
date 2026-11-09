"""Pre-review lint: the mechanical defects ingest reviews keep finding on paper pages.

    uv run librarian ingest precheck data/wiki/eval/mle-bench.md
    uv run librarian ingest precheck <pages> --since HEAD

Each page's body and `summary:` (other frontmatter and `## See Also` left out) is compared with the raw files in
its `sources:`, and `page:line [check] text` is printed for:

- `acronym`: an expansion written next to an acronym, `Words Like This (WLT)` or
  `WLT (words like this)`, that no source spells out.
- `affiliation`: a lab, company or university named on the page but in no source.
- `strip-name`: an author surname from a source that carries contact details (triage route
  `strip`, where people are referred to by role).
- `cross-page`: a sentence that links another page and makes a claim about it ("consistent
  with [[X]]"). The source rarely says what another wiki page found; check it does.

`--since REV` limits findings to lines added since that revision, as for `ingest overlap`.
Exit 1 when anything is reported. Run it with `ingest overlap` before the ingest reviewer.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from librarian.ingest.overlap import _body_lines, _rel, _resolve, added_lines
from librarian.ingest.sensitive import scan_text

_ACR_AFTER_RE = re.compile(r"((?:[A-Za-z][\w-]*[\s-]+){1,8}?)\(([A-Z][A-Za-z0-9]*[A-Z0-9])\)")
_ACR_BEFORE_RE = re.compile(r"\b([A-Z][A-Za-z0-9]*[A-Z0-9])\s+\(([a-z][\w\s-]{3,80})\)")
_WORD_RE = re.compile(r"[a-z0-9]+")
_ORG_RE = re.compile(
    r"\b(?:Google DeepMind|DeepMind|Google Research|Google|Meta AI|Meta|FAIR|Microsoft Research|"
    r"Microsoft|Anthropic|OpenAI|Apple|Amazon|NVIDIA|IBM|Salesforce|Alibaba|Tencent|ByteDance|"
    r"Baidu|Huawei|Shanghai AI Lab(?:oratory)?|MIT|CSAIL|Stanford|Berkeley|CMU|"
    r"Carnegie Mellon|Princeton|Harvard|Oxford|Cambridge|ETH Zurich|EPFL|Tsinghua|"
    r"Peking University|Allen Institute|AI2|Mila|Vector Institute|"
    r"University of [A-Z][a-z]+(?: [A-Z][a-z]+)?)\b"
)
_CLAIM_RE = re.compile(
    r"consistent with|agrees? with|in line with|contradicts|differs? from|unlike|"
    r"which (?:found|showed|reports?)|confirms|echoes|matches",
    re.IGNORECASE,
)
_LINK_RE = re.compile(r"\[\[[^\]]+\]\]")
_AUTHORS_RE = re.compile(r"^Authors:\s*(.+?)(?:\.\s*Venue:|$)", re.MULTILINE)
_SOURCE_NAMES_RE = re.compile(r'^SOURCE:\s*"[^"]*",\s*([^(\n]+?)\s*(?:\(|arXiv|\.\s)', re.MULTILINE)
_STRIP_CATEGORIES = {"email", "phone", "iban"}
# Tokens a name list ends on that are not surnames ("Databricks Research", "Venue: n/a").
_NOT_SURNAMES = {"Venue", "Research", "Lab", "Labs", "Institute", "University", "Inc", "Team"}


@dataclass(frozen=True)
class Finding:
    page: Path
    line: int
    check: str
    text: str


def _initials(words: list[str]) -> str:
    return "".join(w[0] for w in words if w).upper()


def _spelled(phrase: str, haystack: str) -> bool:
    return " ".join(_WORD_RE.findall(phrase.lower())) in haystack


def _surnames(source: str) -> set[str]:
    names: set[str] = set()
    for pattern in (_AUTHORS_RE, _SOURCE_NAMES_RE):
        for m in pattern.finditer(source):
            for person in re.split(r",|\band\b|;", m.group(1)):
                tokens = [t.strip("*.") for t in person.split() if t.strip("*.")]
                if tokens and tokens[-1][:1].isupper() and len(tokens[-1]) > 2:
                    names.add(tokens[-1])
    return names - _NOT_SURNAMES


def _acronyms(line: str, haystack: str) -> list[str]:
    out: list[str] = []
    for m in _ACR_AFTER_RE.finditer(line):
        acr = m.group(2)
        words = re.split(r"[\s-]+", m.group(1).strip())
        caps = "".join(c for c in acr if c.isupper() or c.isdigit())
        for k in range(len(words)):
            tail = words[k:]
            if _initials(tail) == caps and not _spelled(" ".join(tail), haystack):
                out.append(f"{' '.join(tail)} ({acr})")
                break
    for m in _ACR_BEFORE_RE.finditer(line):
        acr, phrase = m.group(1), m.group(2)
        caps = "".join(c for c in acr if c.isupper() or c.isdigit())
        words = re.split(r"[\s-]+", phrase.strip())
        if _initials(words) == caps and not _spelled(phrase, haystack):
            out.append(f"{acr} ({phrase})")
    return out


def precheck(page: Path) -> list[Finding]:
    lines, listed = _body_lines(page)
    raw_body = page.read_text().splitlines()
    # The summary is checked too: index-add copies it into _index.md.
    summary = next((i + 1 for i, ln in enumerate(raw_body) if ln.startswith("summary:")), None)
    if summary is not None:
        lines = [(summary, raw_body[summary - 1]), *lines]
    sources = [_resolve(s) for s in listed]
    texts = [p.read_text(errors="replace") for p in sources if p.is_file()]
    joined = "\n".join(texts)
    haystack = " ".join(_WORD_RE.findall(joined.lower()))
    strip_names: set[str] = set()
    for text in texts:
        if {f.category for f in scan_text(text)} & _STRIP_CATEGORIES:
            strip_names |= _surnames(text)
    found: list[Finding] = []
    for lineno, _ in lines:
        text = raw_body[lineno - 1]
        for hit in _acronyms(_LINK_RE.sub(" ", text), haystack):
            found.append(Finding(page, lineno, "acronym", hit))
        for m in _ORG_RE.finditer(_LINK_RE.sub(" ", text)):
            org = m.group(0)
            if org not in joined and org.replace("University", "Univ.") not in joined:
                found.append(Finding(page, lineno, "affiliation", org))
        for name in sorted(strip_names):
            if re.search(rf"\b{re.escape(name)}\b", text):
                found.append(Finding(page, lineno, "strip-name", name))
        for sentence in re.split(r"(?<=[.;])\s+", text):
            if _LINK_RE.search(sentence) and _CLAIM_RE.search(sentence):
                found.append(Finding(page, lineno, "cross-page", sentence.strip()[:120]))
    return found


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    ap.add_argument("pages", nargs="+", type=Path, help="wiki pages to check")
    ap.add_argument("--since", metavar="REV", help="only lines added since this revision")
    args = ap.parse_args(argv)
    found = 0
    for page in args.pages:
        fresh = added_lines(page, args.since) if args.since else None
        for f in precheck(page):
            if fresh is not None and f.line not in fresh:
                continue
            found += 1
            print(f"{_rel(f.page)}:{f.line} [{f.check}] {f.text}")
    if found:
        print(f"{found} finding(s): fix or confirm against the source", file=sys.stderr)
        return 1
    print(f"OK {len(args.pages)} page(s): no precheck findings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
