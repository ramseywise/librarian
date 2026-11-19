---
title: Python Foundations Reference
tags: [programming, reference]
summary: "Compact Python-for-Everybody-level reference — types and operators with their traps (floor division, truthiness, short-circuit guards), return-don't-print functions, loop patterns and their built-ins, strings and files, collections and aliasing, regex, HTTP, JSON/XML APIs, classes and sqlite3 — plus the course's rules of thumb."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/programming--python--README.md
  - data/raw/repos/learn-ai-engineering/programming--python--01-foundations--notes--01-values-and-conditionals.md
  - data/raw/repos/learn-ai-engineering/programming--python--01-foundations--notes--02-functions.md
  - data/raw/repos/learn-ai-engineering/programming--python--01-foundations--notes--03-loops.md
  - data/raw/repos/learn-ai-engineering/programming--python--01-foundations--notes--04-strings-and-files.md
  - data/raw/repos/learn-ai-engineering/programming--python--01-foundations--notes--05-collections.md
  - data/raw/repos/learn-ai-engineering/programming--python--02-informatics--notes--01-regular-expressions.md
  - data/raw/repos/learn-ai-engineering/programming--python--02-informatics--notes--02-network-and-http.md
  - data/raw/repos/learn-ai-engineering/programming--python--02-informatics--notes--03-web-data-json-xml.md
  - data/raw/repos/learn-ai-engineering/programming--python--02-informatics--notes--04-objects.md
  - data/raw/repos/learn-ai-engineering/programming--python--02-informatics--notes--05-databases.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch09-modularity-ml-writing-testable-legible-code.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch10-standards-coding-creating-maintainable-ml-code.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch13-ml-development-hubris.md
  - data/raw/papers/2026-11-08-python-for-data-analysis-ch02-python-language-basics-ipython-jupyter-notebooks.md
  - data/raw/papers/2026-11-08-python-for-data-analysis-ch03-built-data-structures-functions-files.md
---

# Python Foundations Reference

The beginner-to-scripting spine of the Python track, structured after Charles Severance's
*Python for Everybody* (paraphrased). The engineering-level language features live in their own
pages: [[Python Data Model and Idioms]], [[Python Generators and Lazy Iteration]],
[[Python Closures and Decorators]], [[Python Exceptions and Context Managers]],
[[Python Type Hints and Dataclasses]], [[Python Packaging and Tooling]] and
[[Python Concurrency Models]].

## Rules of thumb

- Functions **return** values. Printing is for the edge of the program.
- Use `with` for anything that must be closed or released: files, connections, locks.
- Catch the narrowest exception you can actually handle. Let the rest crash with a traceback.
- `None` as a default, never `[]` or `{}`.
- Values reach SQL as `?` parameters, never through f-strings.
- Type every function signature. Validate data from outside the program (Pydantic), and trust it afterwards.
- Iterate lazily (generators) over anything that might be large.

## Values, operators and conditionals

- Variables are names bound to values; assignment never copies. Convert explicitly:
  `int("3.5")` raises `ValueError`, `int(float("3.5"))` truncates.
- `/` always returns a float (`7 / 2 == 3.5`). `//` floors toward −∞: `-7 // 2 == -4`, not −3.
  `"1" + 1` is a `TypeError`.
- Comparisons chain (`0 <= score <= 1`). `and`/`or` short-circuit, so put the guard first:
  `x != 0 and 10 / x > 2`.
- Falsy: `0`, `0.0`, `""`, `[]`, `{}`, `None`. Write `if items:`, not `if len(items) > 0:`.
- Wrap only the line that can fail in `try`, and name the exception. A bare `except:` swallows typos and Ctrl-C.
- Debugging: read tracebacks bottom-up (last line names the exception); semantic errors need printed intermediates or small `assert` cases.

## Functions

- No `return` means the function returns `None` (`x = print(...)` gives `None`).
- **Return, don't print**: a returning function is testable (`assert average([1, 2, 3]) == 2`) and reusable; keep calculation and I/O separate.
- Keyword arguments are clearer for optional settings. **Never use a mutable default**: it is created once at `def` time and shared by every call (see [[Python Data Model and Idioms]]).
- Assigning to a global inside a function creates a new local; pass values in and return results rather than using `global`.

## Loop patterns and their built-ins

Every loop pattern is "set up before, update inside, use after" — and each has a built-in:

| Pattern | Built-in |
|---|---|
| Count | `len(xs)`, `sum(1 for x in xs if cond)` |
| Total | `sum(xs)` |
| Largest | `max(xs, default=None)` — a hand loop must start from `None`, not `0`, or all-negative data breaks |
| Search | `target in xs`, `any(cond(x) for x in xs)` |
| Filter / transform | `[x for x in xs if cond(x)]`, `[f(x) for x in xs]` |

- Prefer `for` over `while`; the hand-managed counter is where off-by-one errors live.
- `for i in range(len(xs))` almost always means `enumerate`; walk two sequences with `zip`.
- `for … else` runs `else` only if the loop didn't `break` — legal but confusing; a helper with an early return is usually clearer.

## Strings and files

- Strings are immutable sequences: slicing excludes the end (`s[:i] + s[i:] == s`), every method returns a new string.
- `split()` with no argument splits on any whitespace run; `split(",")` keeps empty fields (`"a,,b"` → `['a', '', 'b']`). `find` returns `-1` when absent.
- f-string formats: `{amount:,.2f}`, `{ratio:.1%}`, `{n:>5}`, `{n:05d}`, and `{value=}` for debugging.
- Read files line by line inside `with open(path, encoding="utf-8")` for constant memory. **Always pass `encoding`** — the default is OS-dependent. `"w"` truncates, `"a"` appends; `write()` adds no newline. Use `pathlib.Path` for paths.

## Collections

- `b = a` aliases the same list; passing a list to a function lets it mutate the caller's list. Copy with `a.copy()`, `a[:]`, `list(a)`.
- `xs.sort()` sorts in place and returns `None`; `sorted(xs)` returns a new list.
- Dicts: O(1) average lookup/insert/`in`; keys must be hashable; insertion order kept (3.7+). Counting idiom `counts[w] = counts.get(w, 0) + 1`, or `Counter` / `defaultdict(list)`.
- Tuples are immutable and hashable, so they work as keys (`{(lat, lon): city}`).
- Multi-key sort via tuple comparison: `sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))` — `key=` replaces the old decorate-sort-undecorate pattern.

## Regular expressions

- Always use raw strings (`r"\d"`). `re.search` returns a Match or `None`; `re.findall` with a group returns the group only; named groups `(?P<host>…)`.
- Greedy vs non-greedy: `<.+>` on `<b>hi</b>` takes the whole string; `<.+?>` gives `['<b>', '</b>']`.
- Don't use regex for fixed delimiters (`split`), HTML/XML (nesting — use a parser), or email/URL validation (use a library). If a pattern is unreadable a week later, use `re.VERBOSE` with comments or a small parser.

## HTTP

HTTP is text over a socket: request line + headers + blank line out; status line, headers, blank line, body back.
2xx success, 3xx follow `Location`, 4xx your mistake (429 = too many requests), 5xx their mistake — usually worth retrying with backoff.

- **Always set a timeout**; without one a stalled server hangs the program forever.
- Build query strings with `urlencode`, never by pasting values; resolve relative links with `urljoin`.
- In real projects use `httpx` or `requests` (`httpx` also supports async — see [[Python Concurrency Models]]).
- Scrape politely: `robots.txt`, terms of service, delays, caching, and prefer an API when one exists.

## JSON, XML and APIs

- `json.loads` gives dicts of *anything* — validate the shape before trusting it (Pydantic, see [[Python Type Hints and Dataclasses]]). Malformed input raises `json.JSONDecodeError`.
- `ElementTree`: `find` returns first match or `None`, `findall` a list. Use `defusedxml` for untrusted XML.
- API recipe: read docs for auth/rate limits/pagination; check status then parse; follow the `next` link or cursor until it runs out; cache responses during development.
- **Keep keys out of code**: read from the environment, keep `.env` out of git.

## Objects

- `s.party()` is shorthand for `PartyAnimal.party(s)`; instances hold attributes, the class holds shared methods. Subclasses call `super().__init__`.
- Keep hierarchies shallow; composition is usually more flexible than deep inheritance.
- Always define `__repr__`; default `__eq__` is identity. For data-holding classes use `@dataclass`.
- Write a class when several functions share state or you need many instances with the same behaviour; otherwise a module of functions is fine.

## Databases from Python (sqlite3)

The ingest pattern behind py4e's database projects. SQL itself is covered in [[SQL from Python]].

- **Normalise**: store each entity once, reference by `id`, join on query.
- **Get-or-create**: `INSERT OR IGNORE` then `SELECT id`, made re-runnable by a `UNIQUE` constraint.
- Many-to-many needs a join table with a composite primary key.
- Wrap the whole load in `with conn:` — one transaction per batch; committing per row is about 100× slower.
- Values always go through `?` parameters; only code-controlled identifiers (table names) may be interpolated.
- Crawlers and geocoders should store progress in the database so they resume after a crash or rate limit.

## Wilson on code standards for ML code

Wilson (*Machine Learning Engineering in Action*, ch09 and ch10) gives experience-based advice, not measured results:

- Prototype in notebooks but rewrite as modular code for the MVP. Wrapping logic in functions leaves its complexity unchanged and makes it less complicated to read, debug and test (his distinction); in his example, refactoring a script into a class changed neither runtime nor output.
- Use descriptive names with no single-letter or abbreviated variables, named constants instead of magic literals, and intermediate variables instead of dense one-liners. Use library functions such as scikit-learn's `mean_squared_error` rather than hand-rolling RMSE.
- Pull hardcoded tunables into constructor defaults overridable by keyword arguments, or into configuration.
- Return dictionaries or named tuples rather than positional or nested tuples, so the return structure can change without editing callers. He prefers static methods to global functions, to keep mutable global state out.
- Avoid wildcard imports, many parameters, and copied boilerplate for train, test and inference features (his "shotgun surgery"). Remove replaced code rather than commenting it out; put large isolated new functionality in a new module.
- Replace deep `if`/`elif` trees with computed mappings: merging 8 model scores of 5 buckets each needs about 821,570 lines by his formula, against a few lines when each model's score is bucketed and summed (illustrative listing).
- He allows plain printing for one-off throwaway checks, where tracker logging is not worth it.

Limits: his text has an internal inconsistency (a dictionary approach needing 32,768 conditions for 8 models, where 5 buckets give 5^8 = 390,625), and the listings use deprecated APIs (`squared=False` in `mean_squared_error`, later deprecated in scikit-learn).

## Wilson on over-engineered ML code

Wilson (*Machine Learning Engineering in Action*, ch13) advises writing for the team's skill level and teaching any advanced idioms through documentation, examples and pair programming rather than a style guide linked in a pull request. He sketches five developer personas on one column-casting task: Hacker, Mystic, Show-off, Mad Scientist and Good Samaritan, the last writing concise code that is complex only where needed. He advises explicit type casts over a catch-all String default for unmatched columns, which he says breeds fragile production failures (a Scala listing). He distinguishes premature generalisation (a framework before the patterns exist) from premature optimisation (tuning one stage before the whole runs). In his Scala generator example, `Seq` with positional lookup scaled worse than linearly (5,000 rows 0.6 s; 50 million rows roughly 2 h 54 min) against about 15 minutes after refactoring; hardware is not stated. His fix rate for tightly coupled imperative Spark code was under 40 percent, counting fixes made before predictions lapsed once an upstream column had changed (his experience, not a measurement). Examples are Scala and Spark, not directly reusable in Python, and the tool names are dated.

## What *Python for Data Analysis* adds

- `list.extend` is cheaper than `+`, which builds a new list; `collections.deque` suits inserting at both ends; `bisect` on an unsorted list returns a wrong answer without an error.
- `defaultdict(list)` or `setdefault` avoids a membership check when grouping; catch specific exceptions rather than a bare `except`; note that text mode defaults to UTF-8, and mind `seek` offsets on multibyte text; test iterability with `iter()`; compare with `None` using `is`.

## Limits

- The book (2nd ed., Python 3.6) calls dicts unordered, which is dated: they keep insertion order since 3.7. See [[IPython Timing and Profiling Workflow]] for the profiling tools.

## See Also
- [[Python Data Model and Idioms]] — extends
- [[Python Generators and Lazy Iteration]] — extends
- [[Python Exceptions and Context Managers]] — extends
- [[Python Type Hints and Dataclasses]] — extends
- [[SQL from Python]] — extends
- [[Programming Curriculum]] — related (course map)
- [[NumPy Vectorisation, Views and Fancy Indexing]] — related
