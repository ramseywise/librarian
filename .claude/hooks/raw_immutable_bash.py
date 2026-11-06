#!/usr/bin/env python3
"""PreToolUse hook (matcher: Bash): keep data/raw/ append-only against shell commands.

Companion to raw-immutable.sh, which only sees Write/Edit. Claude Code delivers hook
input as JSON on stdin: {"tool_name": "Bash", "cwd": "...", "tool_input": {"command": "..."}}.

Policy: creating NEW files under data/raw/ is allowed (scrapers do it); changing or
removing anything that already exists there is not. Exit 2 blocks (message on stderr),
exit 0 allows.

Blocked, when the target resolves into data/raw/ (or, for rm/mv/chmod -R/git rm,
is a parent of it such as `data` or `.`):
  rm, rmdir, unlink, shred, truncate, chmod, chown, chgrp, mv, rename;
  `>` `>>` `>|` and tee onto an EXISTING file; cp/install/rsync/ln/dd/curl -o/wget -O
  onto an existing file, rsync --delete; sed -i, perl -i, ruby -i, awk -i inplace;
  git rm/mv/checkout/restore/clean/reset/stash/apply on those paths;
  find ... -delete / -exec <mutator>; `<anything-with-raw-paths> | xargs <mutator>`;
  python/node/ruby/perl/uv one-liners that mention data/raw and call a write/delete API;
  `bash -c "..."` / `sh -c` / `eval` payloads are parsed recursively.

Limits (string matching is a heuristic, not a sandbox):
  - A script that mutates data/raw/ internally (`python3 tool.py`, `make x`) is invisible
    unless the command line itself names the path.
  - Paths built from variables, command substitution or globs that expand at runtime
    (`rm "$DIR"/x`, `rm $(ls ...)`) cannot be resolved; only a literal `data/raw` text in a
    command that also uses a mutating verb is caught (fallback scan).
  - `cd data/raw` followed by relative ops is tracked for simple `cd X &&`/`;` chains only.
  - Heredoc bodies are not parsed. Symlinks are resolved with realpath, hardlinks are not.
  - `touch` only updates mtime and is allowed.
Test override: RAW_GUARD_ROOT sets the repo root (default: two levels above this file).
"""

from __future__ import annotations

import glob
import json
import os
import re
import shlex
import sys
from pathlib import Path

BLOCK = 2
MAX_DEPTH = 3

ROOT = Path(os.environ.get("RAW_GUARD_ROOT") or Path(__file__).resolve().parents[2])
ROOT = Path(os.path.realpath(ROOT))
RAW = str(ROOT / "data" / "raw")

SEPARATORS = {";", "&&", "||", "|", "|&", "&", "(", ")"}
REDIRECTS = {">", ">>", ">|", "&>", "&>>"}
WRAPPERS = {"sudo", "command", "nohup", "time", "env", "exec", "builtin", "nice", "doas"}
DESTRUCTIVE = {
    "rm", "rmdir", "unlink", "shred", "truncate", "chmod", "chown", "chgrp",
    "mv", "rename", "trash", "chflags",
}  # fmt: skip
COPIERS = {"cp", "install", "rsync", "ln", "ditto"}
INPLACE_EDITORS = {"sed", "perl", "ruby", "awk", "gawk", "sd"}
OUTPUT_FLAG_TOOLS = {"curl": {"-o", "--output"}, "wget": {"-O", "--output-document"}}
GIT_MUTATORS = {
    "rm",
    "mv",
    "checkout",
    "restore",
    "clean",
    "reset",
    "stash",
    "apply",
    "revert",
    "switch",
}
INTERPRETERS = re.compile(r"^(python[\d.]*|uv|node|deno|bun|ruby|perl|php|pypy3?)$")
WRITE_API = re.compile(
    r"write_text|write_bytes|unlink|rmtree|\bremove\(|\brename\(|\breplace\(|shutil|os\.system|"
    r"subprocess|truncate|\.write\(|open\([^)]*['\"][wax+]|writeFile|appendFile|rmSync|unlinkSync|File\.(write|delete)",
)
SHELL_C = {"bash", "sh", "zsh", "dash", "ksh"}
GLOB_CHARS = set("*?[")


def real(tok: str, cwd: str) -> str | None:
    """Absolute, symlink-resolved path for a literal token, or None if not resolvable."""
    if not tok or "$" in tok or "`" in tok:
        return None
    return os.path.realpath(os.path.join(cwd, os.path.expanduser(tok)))


def expand(tok: str, cwd: str) -> list[str]:
    """Paths a token can refer to (glob-expanded when it has wildcards)."""
    p = real(tok, cwd)
    if p is None:
        return []
    if GLOB_CHARS & set(tok):
        hits = [os.path.realpath(h) for h in glob.glob(p)]
        return hits
    return [p]


def in_raw(p: str) -> bool:
    return p == RAW or p.startswith(RAW + os.sep)


def is_ancestor(p: str) -> bool:
    return RAW.startswith(p.rstrip(os.sep) + os.sep)


def touches(tok: str, cwd: str, ancestors: bool = False) -> bool:
    return any(in_raw(p) or (ancestors and is_ancestor(p)) for p in expand(tok, cwd))


def existing_raw(tok: str, cwd: str) -> bool:
    return any(in_raw(p) and os.path.lexists(p) for p in expand(tok, cwd))


def split_segments(tokens: list[str]) -> list[list[str]]:
    segs: list[list[str]] = [[]]
    for t in tokens:
        if t in SEPARATORS:
            segs.append([])
        else:
            segs[-1].append(t)
    return [s for s in segs if s]


def cands(args: list[str]) -> list[str]:
    """Non-option arguments, plus the value of key=value / --opt=value forms."""
    out = []
    for a in args:
        if "=" in a and (a.startswith("-") or re.match(r"^[a-z]+=", a)):
            out.append(a.split("=", 1)[1])
        elif not a.startswith("-") or a == "-":
            out.append(a)
    return [c for c in out if c]


def copy_conflicts(srcs: list[str], dest: str, cwd: str, rsync: bool) -> bool:
    dp = real(dest, cwd)
    if dp is None or not in_raw(dp):
        return False
    if not os.path.isdir(dp):
        return os.path.lexists(dp)
    for s in srcs:
        for sp in expand(s, cwd) or []:
            base = os.path.basename(sp.rstrip(os.sep))
            if os.path.lexists(os.path.join(dp, base)):
                return True
            if os.path.isdir(sp):
                for _, _, files in os.walk(sp):
                    if any(os.path.lexists(os.path.join(dp, f)) for f in files):
                        return rsync or True
    return False


def check_segment(seg: list[str], cwd: str, raw_upstream: bool, depth: int) -> str | None:
    """Return a reason string if this simple command mutates data/raw/."""
    toks = list(seg)
    # redirects: any target that already exists in raw
    clean: list[str] = []
    i = 0
    while i < len(toks):
        if toks[i] in REDIRECTS and i + 1 < len(toks):
            if existing_raw(toks[i + 1], cwd):
                return f"redirect ({toks[i]}) onto existing {toks[i + 1]}"
            i += 2
            continue
        if toks[i] in (">&", "<", "<<", "<<<", "<&"):
            i += 2
            continue
        clean.append(toks[i])
        i += 1
    toks = clean
    # drop env assignments and wrappers
    while toks and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[0]) or toks[0] in WRAPPERS):
        toks = toks[1:]
    if not toks:
        return None
    verb = os.path.basename(toks[0])
    args = toks[1:]

    if verb in ("cd", "pushd"):
        return None
    if verb == "xargs":
        j = 0
        while j < len(args) and args[j].startswith("-"):
            j += 2 if args[j] in ("-I", "-n", "-P", "-L", "-d", "-E", "-s") else 1
        inner = args[j:]
        if not inner:
            return None
        verb, args = os.path.basename(inner[0]), inner[1:]
        if raw_upstream and (
            verb in DESTRUCTIVE or verb in COPIERS or verb in ("tee", "sed", "perl")
        ):
            return f"xargs {verb} fed from a command that lists data/raw"
    if verb in SHELL_C and "-c" in args:
        k = args.index("-c")
        if k + 1 < len(args) and depth < MAX_DEPTH:
            return check_command(args[k + 1], cwd, depth + 1)
    if verb == "eval" and args and depth < MAX_DEPTH:
        return check_command(" ".join(args), cwd, depth + 1)

    cs = cands(args)

    if verb in DESTRUCTIVE:
        recursive = (
            any(re.match(r"^-[A-Za-z]*[Rr]", a) for a in args if not a.startswith("--"))
            or "--recursive" in args
        )
        anc = verb in ("rm", "mv", "rmdir", "trash") or recursive
        if verb == "mv":
            for c in cs[:-1]:  # every source: moving it out of raw is a deletion
                if touches(c, cwd, ancestors=True):
                    return f"mv of {c}"
            if cs and copy_conflicts(cs[:-1], cs[-1], cwd, False):
                return f"mv overwrites existing file under {cs[-1]}"
            return None
        for c in cs:
            if touches(c, cwd, ancestors=anc):
                return f"{verb} on {c}"
        return None

    if verb in COPIERS:
        if (
            verb == "rsync"
            and any(a.startswith("--delete") or a == "--remove-source-files" for a in args)
            and any(touches(c, cwd) for c in cs)
        ):
            return "rsync --delete/--remove-source-files with data/raw"
        tflag = next(
            (a.split("=", 1)[1] for a in args if a.startswith("--target-directory=")), None
        )
        if "-t" in args and args.index("-t") + 1 < len(args):
            tflag = args[args.index("-t") + 1]
        if tflag:
            if copy_conflicts([c for c in cs if c != tflag], tflag, cwd, verb == "rsync"):
                return f"{verb} overwrites existing file under {tflag}"
        elif len(cs) >= 2 and copy_conflicts(cs[:-1], cs[-1], cwd, verb == "rsync"):
            return f"{verb} overwrites existing file at {cs[-1]}"
        return None

    if verb == "tee":
        for c in cs:
            if existing_raw(c, cwd):
                return f"tee onto existing {c}"
        return None

    if verb == "dd":
        for a in args:
            if a.startswith("of=") and existing_raw(a[3:], cwd):
                return f"dd onto existing {a[3:]}"
        return None

    if verb in OUTPUT_FLAG_TOOLS:
        flags = OUTPUT_FLAG_TOOLS[verb]
        for n, a in enumerate(args):
            val = None
            if a in flags and n + 1 < len(args):
                val = args[n + 1]
            elif a.startswith("--output"):
                val = a.split("=", 1)[-1]
            if val and existing_raw(val, cwd):
                return f"{verb} output over existing {val}"
        return None

    if verb in INPLACE_EDITORS:
        inplace = any(
            re.match(r"^-[A-Za-z0-9]*i", a) or a.startswith("--in-place") or a == "inplace"
            for a in args
            if not (a.startswith("--") and not a.startswith("--in-place"))
        )
        if verb == "sed" or verb == "perl" or verb == "ruby" or verb in ("awk", "gawk", "sd"):
            if inplace and any(touches(c, cwd) for c in cs):
                return f"{verb} in-place edit"
            if verb == "sd" and any(touches(c, cwd) for c in cs):
                return "sd edits files in place"
        return None

    if verb == "git":
        a2 = list(args)
        while a2 and a2[0].startswith("-"):
            if a2[0] == "-C" and len(a2) > 1:
                cwd = real(a2[1], cwd) or cwd
                a2 = a2[2:]
            else:
                a2 = a2[1:]
        if a2 and a2[0] in GIT_MUTATORS:
            for c in cands(a2[1:]):
                if touches(c, cwd, ancestors=True):
                    return f"git {a2[0]} on {c}"
        return None

    if verb == "find":
        roots = [a for a in args if not a.startswith("-") and a not in ("(", ")", "!")]
        hits_raw = any(touches(c, cwd, ancestors=True) for c in roots)
        if hits_raw:
            if "-delete" in args:
                return "find -delete under data/raw"
            for n, a in enumerate(args):
                if a in ("-exec", "-execdir", "-ok", "-okdir") and n + 1 < len(args):
                    v = os.path.basename(args[n + 1])
                    if v in DESTRUCTIVE | COPIERS | {"tee", "sed", "perl", "truncate"}:
                        return f"find -exec {v} under data/raw"
        return None

    if INTERPRETERS.match(verb):
        text = " ".join(toks)
        if re.search(r"data/raw", text) and WRITE_API.search(text):
            return "interpreter one-liner writes/deletes with a data/raw path"
        return None

    return None


def check_command(command: str, cwd: str, depth: int = 0) -> str | None:
    prepared = command.replace("\r", " ").replace("\n", " ; ")
    try:
        lex = shlex.shlex(prepared, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        tokens = list(lex)
    except ValueError:
        # Unbalanced quotes etc.: fall back to a coarse text scan.
        if re.search(r"data/raw", command) and re.search(
            r"\b(rm|mv|truncate|chmod|sed\s+-\S*i|perl\s+-\S*i|shred|tee)\b|>>?\s*\S*data/raw",
            command,
        ):
            return "unparseable command mentions data/raw with a mutating verb"
        return None

    raw_upstream = False
    cur = cwd
    for seg in split_segments(tokens):
        reason = check_segment(seg, cur, raw_upstream, depth)
        if reason:
            return reason
        if seg and os.path.basename(seg[0]) in ("cd", "pushd") and len(seg) > 1:
            cur = real(seg[1], cur) or cur
        if any(touches(c, cur, ancestors=False) for c in cands(seg[1:]) if c not in REDIRECTS):
            raw_upstream = True
    # Fallback: unresolved ($VAR, $(...)) path text beside a mutating verb.
    if (
        re.search(r"data/raw", command)
        and re.search(r"[$`]", command)
        and re.search(r"(^|[\s;&|(])(rm|mv|truncate|shred|chmod)\s", command)
    ):
        return "mutating verb with an unresolvable data/raw path"
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if payload.get("tool_name", "Bash") != "Bash":
        return 0
    command = (payload.get("tool_input") or {}).get("command") or ""
    cwd = payload.get("cwd") or str(ROOT)
    if not command or (
        "data/raw" not in command
        and not re.search(r"\b(rm|mv|git|find|chmod|truncate|cd)\b", command)
    ):
        return 0
    reason = check_command(command, os.path.realpath(cwd))
    if reason:
        sys.stderr.write(
            f"BLOCKED: {reason}.\n\n"
            "data/raw/ is append-only: creating new files is fine, but existing files must never be\n"
            "edited, overwritten, moved or deleted. If a source changed, add a new dated file instead.\n"
        )
        return BLOCK
    return 0


if __name__ == "__main__":
    sys.exit(main())
