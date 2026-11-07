---
generated_by: src/librarian/slides/flashcards.py
decks:
- programming/python/01-foundations/slides/deck.yaml
- programming/python/02-informatics/slides/deck.yaml
- programming/python/03-language-for-engineers/slides/deck.yaml
cards:
- front: What do Python's arithmetic operators return?
  back: '`/` always returns a float, and `//` floors toward negative infinity rather than zero.'
  lesson: programming/python/01-foundations/notes/01-values-and-conditionals
- front: What counts as false in an if?
  back: Zero, empty containers and `None` are falsy. `and` and `or` short-circuit, so the guard goes first.
  lesson: programming/python/01-foundations/notes/01-values-and-conditionals
- front: How do you catch bad input?
  back: Wrap only the line that can fail and name the exception you expect.
  lesson: programming/python/01-foundations/notes/01-values-and-conditionals
- front: What does def do, and what does a call do?
  back: '`def` only binds a name. The body runs per call, and a function with no `return` returns `None`.'
  lesson: programming/python/01-foundations/notes/02-functions
- front: Why should a function return rather than print?
  back: Functions return values, so they can be tested and reused. Printing is for the edge of the program.
  lesson: programming/python/01-foundations/notes/02-functions
- front: Why is def f(xs=[]) a bug?
  back: A default is created once, at definition time, and shared by every call. Use `None` and build inside.
  lesson: programming/python/01-foundations/notes/02-functions
- front: Can a function change a global variable?
  back: Assignment inside a function creates a local name. Pass values in and return results instead of using `global`.
  lesson: programming/python/01-foundations/notes/02-functions
- front: What shape does every loop pattern share?
  back: Set up a variable before the loop, update it inside, use it after. Start "largest" from `None`, not `0`.
  lesson: programming/python/01-foundations/notes/03-loops
- front: Which built-in replaces each loop pattern?
  back: Reach for `sum`, `max`, `in`, `any` and comprehensions before you write the loop by hand.
  lesson: programming/python/01-foundations/notes/03-loops
- front: How do you loop with an index, or over two lists?
  back: Use `enumerate` for an index and `zip` for parallel sequences, never `range(len(xs))`.
  lesson: programming/python/01-foundations/notes/03-loops
- front: What does s[1:4] return?
  back: A slice includes the start and excludes the end. Strings are immutable, so every method returns a new one.
  lesson: programming/python/01-foundations/notes/04-strings-and-files
- front: Which string methods do you use constantly?
  back: '`split()` with no argument splits on any run of whitespace. `split(sep)` keeps empty fields.'
  lesson: programming/python/01-foundations/notes/04-strings-and-files
- front: How do you read a file safely, line by line?
  back: Use `with open(path, encoding="utf-8")` and iterate over lines, so memory stays constant and the file closes.
  lesson: programming/python/01-foundations/notes/04-strings-and-files
- front: Does b = a copy a list?
  back: '`b = a` makes a second name for the same list. Copy with `a.copy()`, and remember functions can mutate arguments.'
  lesson: programming/python/01-foundations/notes/05-collections
- front: What is the counting idiom?
  back: '`counts[k] = counts.get(k, 0) + 1` counts anything. `Counter` and `defaultdict` are the library versions.'
  lesson: programming/python/01-foundations/notes/05-collections
- front: Which collection should you pick?
  back: Only hashable values can be dict keys, so a tuple can be one and a list cannot.
  lesson: programming/python/01-foundations/notes/05-collections
- front: How do you sort by count, breaking ties by name?
  back: Have `key=` return a tuple such as `(-count, word)`, because tuples compare element by element.
  lesson: programming/python/01-foundations/notes/05-collections
- front: How do you handle return values, exceptions and files?
  back: Return values, name exceptions, use built-ins, and open files with `with` and an explicit encoding.
  lesson: programming/python/01-foundations/notes/02-functions
- front: Where do you go after foundations?
  back: Next is Python 02 informatics, with SQL 01 alongside. If an exercise file passes first try, move on.
  lesson: programming/python/01-foundations/notes/05-collections
- front: Which regex syntax covers most needs?
  back: Learn classes, repeats, anchors and groups, and always write patterns as raw strings like `r"\d+"`.
  lesson: programming/python/02-informatics/notes/01-regular-expressions
- front: What does re.findall return if the pattern has a group?
  back: With a group, `findall` returns the group and not the full match. `search` returns a Match or `None`.
  lesson: programming/python/02-informatics/notes/01-regular-expressions
- front: What is the difference between greedy and non-greedy matching?
  back: Quantifiers are greedy by default. Add `?` to match as little as possible.
  lesson: programming/python/02-informatics/notes/01-regular-expressions
- front: What actually goes over the wire in HTTP?
  back: A request line and headers go out. A status line, headers, a blank line and a body come back.
  lesson: programming/python/02-informatics/notes/02-network-and-http
- front: What does each status class mean, and which do you retry?
  back: 4xx means your request is wrong, 5xx means the server failed. Retry 5xx with backoff, and slow down on `429`.
  lesson: programming/python/02-informatics/notes/02-network-and-http
- front: What must every network call set?
  back: Always set a timeout, because a stalled server otherwise hangs forever. Escape query values with `urlencode`.
  lesson: programming/python/02-informatics/notes/02-network-and-http
- front: How does text become data you can trust?
  back: Parse into Python objects, check the shape, then work with plain dicts and lists.
  lesson: programming/python/02-informatics/notes/03-web-data-json-xml
- front: What do find and findall return in ElementTree?
  back: '`find` returns the first match or `None`, `findall` returns a list. Use `defusedxml` on untrusted input.'
  lesson: programming/python/02-informatics/notes/03-web-data-json-xml
- front: What are the steps of calling an API?
  back: Read the docs, build the URL safely, check status before parsing, follow pagination, and cache while developing.
  lesson: programming/python/02-informatics/notes/03-web-data-json-xml
- front: Where should an API key live?
  back: Never put keys in code. Read them from the environment and keep `.env` files out of git.
  lesson: programming/python/02-informatics/notes/03-web-data-json-xml
- front: What is self?
  back: '`self` is the instance. `s.party()` is shorthand for `PartyAnimal.party(s)`, so attributes are per instance.'
  lesson: programming/python/02-informatics/notes/04-objects
- front: Which dunder method enables which syntax?
  back: Dunder methods hook a class into Python's syntax. Without `__eq__`, `==` compares identity.
  lesson: programming/python/02-informatics/notes/04-objects
- front: What are the steps of a re-runnable load?
  back: Normalise into tables, get-or-create parents with a `UNIQUE` key, and store progress so a crash can resume.
  lesson: programming/python/02-informatics/notes/05-databases
- front: How do you make get-or-create safe to re-run?
  back: '`INSERT OR IGNORE` plus `SELECT id` on a `UNIQUE` column is safe to run twice. Values go in as `?` parameters.'
  lesson: programming/python/02-informatics/notes/05-databases
- front: How often should you commit during a load?
  back: Commit once per batch, not per row, because every commit waits for the disk.
  lesson: programming/python/02-informatics/notes/05-databases
- front: What do you put on every call, parse, query and batch?
  back: Timeouts on every call, shape checks on every parse, parameters in every query, commits per batch.
  lesson: programming/python/02-informatics/notes/02-network-and-http
- front: Where do you go after informatics?
  back: Next is SQL 01 for queries and Python 03 for the language features that engineering code relies on.
  lesson: programming/python/02-informatics/notes/05-databases
- front: What is the difference between mutating and rebinding?
  back: Mutating changes the object, so every name sees it. Rebinding moves one label, so nothing else changes.
  lesson: programming/python/03-language-for-engineers/notes/01-data-model-and-idioms
- front: When do you use == and when do you use is?
  back: '`==` compares values and `is` compares identity. Use `is` only for `None`, `True`, `False` and sentinels.'
  lesson: programming/python/03-language-for-engineers/notes/01-data-model-and-idioms
- front: How does Python syntax map to methods?
  back: Syntax calls dunder methods, so implementing them plugs your objects into the language.
  lesson: programming/python/03-language-for-engineers/notes/01-data-model-and-idioms
- front: What does a for loop actually do?
  back: A `for` loop calls `iter()` once, then `next()` until `StopIteration`. Iterators are single-use, so a second pass yields nothing.
  lesson: programming/python/03-language-for-engineers/notes/02-generators-and-iteration
- front: Why would you write a generator?
  back: A function with `yield` runs only as values are requested and holds one item at a time, so memory stays constant.
  lesson: programming/python/03-language-for-engineers/notes/02-generators-and-iteration
- front: What must you do before `itertools.groupby`?
  back: '`groupby` only groups consecutive keys, so sort first.'
  lesson: programming/python/03-language-for-engineers/notes/02-generators-and-iteration
- front: What do closures capture?
  back: Closures capture variables, not values. Bind early with a default, and use `nonlocal` to rebind an outer name.
  lesson: programming/python/03-language-for-engineers/notes/03-functions-deeper
- front: What is a decorator?
  back: A decorator is a function that wraps a function. `@timed` means `load = timed(load)`, and arguments add one more level.
  lesson: programming/python/03-language-for-engineers/notes/03-functions-deeper
- front: How do you write a safe try/except?
  back: Catch the narrowest exception, keep the `try` small, and use `raise ... from err` to keep the cause.
  lesson: programming/python/03-language-for-engineers/notes/04-errors-and-context-managers
- front: How do you write your own context manager?
  back: With `@contextmanager`, code before `yield` is setup and code after is teardown. Use `try/finally` so teardown runs on error.
  lesson: programming/python/03-language-for-engineers/notes/04-errors-and-context-managers
- front: Who checks Python's type hints?
  back: Python ignores hints at runtime, so run a checker. `X | None` forces callers to handle the missing case.
  lesson: programming/python/03-language-for-engineers/notes/05-types-and-dataclasses
- front: When do you use a dataclass, and when Pydantic?
  back: Use dataclasses inside the program and a validator at every edge, such as API JSON, config and LLM output.
  lesson: programming/python/03-language-for-engineers/notes/05-types-and-dataclasses
- front: What are the parts of a modern Python project?
  back: A project is a `pyproject.toml`, `src/` and `tests/`, with uv, ruff and pytest. Never name a file after a standard-library module.
  lesson: programming/python/03-language-for-engineers/notes/06-modules-packaging-tooling
- front: Why do threads help waiting but not computing?
  back: The GIL lets one thread run Python bytecode at a time, and threads release it while waiting on I/O. So threads help with waiting, and processes help with computing.
  lesson: programming/python/03-language-for-engineers/notes/07-concurrency
- front: How does the event loop run two tasks on one thread?
  back: One thread runs ready tasks until each hits an `await`. Nothing preempts a task, so switching happens only at `await`.
  lesson: programming/python/03-language-for-engineers/notes/07-concurrency
- front: How do you limit concurrency in asyncio?
  back: Use a `Semaphore` to cap requests in flight and a `TaskGroup` to cancel the rest when one fails.
  lesson: programming/python/03-language-for-engineers/notes/07-concurrency
- front: What must you never do inside async def?
  back: Blocking calls inside `async def` freeze every task. Await an async client, or push the work to `asyncio.to_thread`.
  lesson: programming/python/03-language-for-engineers/notes/07-concurrency
- front: How should you retry a failed call?
  back: Back off exponentially with jitter, and retry only errors that can succeed next time, such as timeouts, 429 and 5xx.
  lesson: programming/python/03-language-for-engineers/notes/07-concurrency
- front: In `class ProdClient(Retrying, Logged)`, with both parents inheriting `BaseClient`, what does `super()` inside `Retrying` reach, and why?
  back: 'It reaches `Logged`: `super()` continues from the entry after the current class in the MRO of the instance''s type, so it can reach a sibling, not only a parent.'
  lesson: programming/python/03-language-for-engineers/notes/08-objects-inheritance-and-mro
- front: What is a memory leak in Python, and how do you find it?
  back: A Python leak is an object something can still reach, so diff two `tracemalloc` snapshots after warm-up, and don't trust RSS alone.
  lesson: programming/python/03-language-for-engineers/notes/09-memory-and-the-runtime
- front: What are the engineering rules?
  back: Treat names as labels, fail narrowly, validate at edges, and choose concurrency by what you are waiting on.
  lesson: programming/python/03-language-for-engineers/notes/01-data-model-and-idioms
---
