---
imported_hash: 4daa529cec0caac4
title: 1 — Regular Expressions
summary: 're.search(r"^From: ", line) # a Match or None: is the pattern anywhere?'
order: 7
kind: reading
section: Informatics / Notes
source: learn-ai-engineering/programming/python/02-informatics/notes/01-regular-expressions.md
---

# 1 — Regular Expressions

> A regex is a tiny pattern language for "find text shaped like this". Use it to *extract* fields from messy text. Use `split()` and `startswith()` when they're enough.

---

## The core calls

```python
import re

re.search(r"^From: ", line)                # a Match or None: is the pattern anywhere?
re.findall(r"\S+@\S+", line)               # a list of every match
re.findall(r"^From .* (\d\d):", line)      # with a group, findall returns the group only
m = re.search(r"(?P<user>[\w.]+)@(?P<host>[\w.]+)", line)
m.group("host") if m else None
re.sub(r"\s+", " ", text)                  # replace
```

**Always use raw strings** (`r"..."`) so that `\d` reaches the regex engine instead of being treated as a Python escape.

## The syntax you need

| Pattern | Matches |
|---|---|
| `.` | Any character except a newline |
| `\d` `\w` `\s` | A digit, a word character `[A-Za-z0-9_]`, whitespace |
| `\D` `\W` `\S` | The opposites |
| `[aeiou]`, `[^,]`, `[0-9.-]` | A character class, a negated class, a range |
| `*` `+` `?` `{2,4}` | 0+, 1+, 0 or 1, between 2 and 4 repeats |
| `*?` `+?` | **Non-greedy** versions: match as little as possible |
| `^` `$` | Start and end of the string (or of each line, with `re.MULTILINE`) |
| `( … )` | Capture group. `(?: … )` groups without capturing |
| `a\|b` | Alternation |
| `\.` `\$` `\(` | A literal special character |

## Greedy vs non-greedy

```python
re.findall(r"<.+>", "<b>hi</b>")    # ['<b>hi</b>']: greedy takes as much as it can
re.findall(r"<.+?>", "<b>hi</b>")   # ['<b>', '</b>']
```

## When not to use regex

- Splitting on a fixed delimiter: use `str.split`.
- HTML or XML: use a parser ([note 03](03-web-data-json-xml.md)). A regex can't reliably handle nesting.
- Email or URL validation: use a library. A regex for that is either too strict or wrong.
- Anything you can't explain from its pattern string a week later. Compile it with `re.VERBOSE` and add comments, or write a small parser instead.

---

## Exercises

[`practice/exercises/01_regex.py`](../practice/exercises/01_regex.py)
