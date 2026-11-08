"""`librarian wiki sync-check`: taxonomy drift between `data/wiki/` and the code that names domains.

The directories under `data/wiki/` (minus `private/`) are the domain list. This checks that the
three backend derivations still read the disk instead of a literal list, that the frontend
holds no domain list outside `theme/domains.ts`, and compares the fixed colour map with the
directories. DRIFT exits 1; thin/thick domains and colour gaps are notes. Read-only: choosing a
colour for a new domain stays with the `/wiki-sync` skill.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from librarian.config import get_settings

WIKI_DIR = get_settings().wiki_dir
SRC_DIR = Path(__file__).resolve().parents[1]
APP_SRC = get_settings().root / "app" / "src"
THIN_PAGES = 3
THICK_PAGES = 20
# (file under the package, function that must derive the set from disk)
DERIVATIONS = (
    ("wiki/parser.py", "_domain_tag_set"),
    ("retrieval/corpus.py", "wiki_domains"),
    ("wiki/relinker.py", "_domain_tag_set"),
)
_DOMAIN_LIST = r'"(rag|langgraph|adk|infra|memory)"|^\s*(rag|langgraph|adk|infra|memory)\s*:'
_DOMAIN_RE = re.compile(_DOMAIN_LIST)
_KNOWN_BLOCK_RE = re.compile(r"export const KNOWN[^=]*=\s*\{(.*?)\n\};", re.DOTALL)
_KEY_RE = re.compile(r'^\s*(?:"([^"]+)"|([A-Za-z_][\w-]*))\s*:', re.MULTILINE)


@dataclass(frozen=True)
class Finding:
    kind: str  # DRIFT | THIN | THICK | NOTE
    where: str
    message: str


def wiki_domains(wiki_dir: Path) -> dict[str, int]:
    """Page count per domain directory, `private/` left out."""
    return {
        d.name: sum(1 for _ in d.rglob("*.md"))
        for d in sorted(wiki_dir.iterdir())
        if d.is_dir() and d.name != "private"
    }


def known_colours(domains_ts: Path) -> set[str] | None:
    """Keys of `KNOWN` in `theme/domains.ts`, or None when the file or the block is missing."""
    if not domains_ts.is_file():
        return None
    block = _KNOWN_BLOCK_RE.search(domains_ts.read_text())
    if block is None:
        return None
    return {a or b for a, b in _KEY_RE.findall(block.group(1))}


def _derives_from_disk(source: str, func: str) -> str | None:
    """None when `func` reads WIKI_DIR and excludes private; else why it does not."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return "does not parse"
    node = next(
        (n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == func), None
    )
    if node is None:
        return f"{func}() not found"
    names = {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
    strings = {n.value for n in ast.walk(node) if isinstance(n, ast.Constant)}
    literal = [
        n
        for n in ast.walk(node)
        if isinstance(n, ast.Set | ast.List | ast.Tuple)
        and sum(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in n.elts) >= 3
    ]
    if literal:
        return "holds a literal list of domains"
    if "WIKI_DIR" not in names:
        return "does not read WIKI_DIR"
    if "private" not in strings:
        return "does not exclude private/"
    return None


def check(wiki_dir: Path, src_dir: Path, app_src: Path) -> tuple[dict[str, int], list[Finding]]:
    domains = wiki_domains(wiki_dir)
    out: list[Finding] = []
    for name, count in domains.items():
        if count < THIN_PAGES:
            out.append(Finding("THIN", name, f"{count} page(s): merge candidate"))
        elif count > THICK_PAGES:
            out.append(Finding("THICK", name, f"{count} pages: split candidate"))
    for rel, func in DERIVATIONS:
        path = src_dir / rel
        if not path.is_file():
            out.append(Finding("DRIFT", rel, "file not found"))
        elif (why := _derives_from_disk(path.read_text(), func)) is not None:
            out.append(Finding("DRIFT", f"{rel}:{func}", why))
    domains_ts = app_src / "theme" / "domains.ts"
    known = known_colours(domains_ts)
    if known is None:
        out.append(Finding("NOTE", "app/src/theme/domains.ts", "KNOWN colour map not found"))
    else:
        out += [
            Finding("NOTE", d, "no fixed colour in KNOWN (palette fallback colours it)")
            for d in domains
            if d not in known
        ]
        out += [
            Finding("NOTE", k, "ghost KNOWN colour (no data/wiki/ directory)")
            for k in sorted(known - set(domains) - {"private"})
        ]
    if app_src.is_dir():
        for path in sorted([*app_src.rglob("*.ts"), *app_src.rglob("*.tsx")]):
            rel = path.relative_to(app_src).as_posix()
            if rel == "theme/domains.ts" or "__tests__" in path.parts:
                continue
            names: set[str] = set()
            first = 0
            for number, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
                for match in _DOMAIN_RE.finditer(line):
                    names.add(match.group(1) or match.group(2))
                    first = first or number
            if len(names) >= 3:
                msg = f"names {len(names)} domains ({', '.join(sorted(names))}): a list was reintroduced"
                out.append(Finding("DRIFT", f"app/src/{rel}:{first}", msg))
    return domains, out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--wiki-dir", type=Path, default=WIKI_DIR)
    parser.add_argument("--src-dir", type=Path, default=SRC_DIR, help="the librarian package")
    parser.add_argument("--app-src", type=Path, default=APP_SRC)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.wiki_dir.is_dir():
        print(f"sync-check: wiki dir not found: {args.wiki_dir}", file=sys.stderr)
        return 2
    domains, findings = check(args.wiki_dir, args.src_dir, args.app_src)
    drift = [f for f in findings if f.kind == "DRIFT"]
    if args.json:
        print(json.dumps({"domains": domains, "findings": [asdict(f) for f in findings]}, indent=2))
    else:
        print(f"domains ({len(domains)}, private/ excluded, {sum(domains.values())} pages):")
        print("  " + ", ".join(f"{d} {n}" for d, n in sorted(domains.items(), key=lambda x: -x[1])))
        for f in findings:
            print(f"[{f.kind}] {f.where} — {f.message}")
        print(f"sync-check: {len(drift)} drift, {len(findings) - len(drift)} other")
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
