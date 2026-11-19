---
title: Python Exceptions and Context Managers
tags: [programming, pattern]
summary: "Catch only what you can handle, chain re-raised errors with `raise … from err`, give each package one exception base class with fields callers can branch on, and put cleanup in `with`/`finally` — `@contextmanager` turns a try/finally around a `yield` into a reusable resource guard."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/programming--python--03-language-for-engineers--notes--04-errors-and-context-managers.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch10-standards-coding-creating-maintainable-ml-code.md
---

# Python Exceptions and Context Managers

Catch what you can handle, let everything else crash loudly, and put cleanup in `with` or
`finally` so it happens no matter what. (Sources: *A Whirlwind Tour of Python*; Python docs on
errors and `contextlib`.)

## try / except / else / finally

```python
try:
    cfg = json.loads(path.read_text())
except FileNotFoundError:
    cfg = {}                              # expected: fall back
except json.JSONDecodeError as err:
    raise ValueError(f"{path} is not valid JSON: {err}") from err
else:
    log.info("loaded %s", path)           # only if no exception
finally:
    ...                                   # always, even after return
```

- Catch the **narrowest** exception. A bare `except:` or `except Exception:` hides bugs like `NameError` (and a bare `except:` also catches `KeyboardInterrupt`).
- `raise ... from err` keeps the original traceback as the cause. Plain `raise` re-raises unchanged.
- Keep the `try` block small — only the line that can fail — so you don't catch errors from code you didn't mean to guard.
- `else` holds code that should run only on success, keeping it outside the guarded region.

## Your own exceptions

```python
class PipelineError(Exception):
    """Base for this package's errors."""

class SchemaError(PipelineError):
    def __init__(self, column: str, problem: str):
        super().__init__(f"{column}: {problem}")
        self.column = column
```

- **One base class per package** lets callers write `except PipelineError` without catching everything else.
- **Add fields** for anything a caller might branch on, instead of making them parse the message string.
- `ExceptionGroup` and `except*` (3.11+) handle several failures at once, e.g. from `asyncio.TaskGroup` ([[Python Concurrency Models]]).

## Context managers

`with` guarantees cleanup: the file is closed, the lock released, the transaction committed or
rolled back. Multiple managers fit in one statement: `with open(src) as fin, open(dst, "w") as fout:`.

Write your own with `contextlib.contextmanager`. Code before `yield` is setup, code after is
teardown, and the `try/finally` makes teardown run on error:

```python
@contextmanager
def env(**values):
    old = {k: os.environ.get(k) for k in values}
    os.environ.update(values)
    try:
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)   # it didn't exist before: remove, don't set to None
            else:
                os.environ[k] = v
```

- Without the `try/finally` around `yield`, an exception in the body skips the teardown.
- As a class, implement `__enter__` and `__exit__(exc_type, exc, tb)`. **Returning `True` from `__exit__` swallows the exception** — rarely what you want.
- Also useful: `contextlib.suppress(FileNotFoundError)`, `ExitStack` for a variable number of resources, `tempfile.TemporaryDirectory()`.
- `@contextmanager` is built on a generator, so the resource-lifetime caveats of [[Python Generators and Lazy Iteration]] apply.

## Logging, not print

```python
log = logging.getLogger(__name__)
log.info("loaded %d rows from %s", n, path)     # lazy %-formatting, not an f-string
log.exception("upload failed")                  # inside except: adds the traceback
```

Per-module loggers (`__name__`), lazy formatting arguments, and `log.exception` inside handlers
are the three habits.

## Wilson on exception eating in ML code

Wilson (*Machine Learning Engineering in Action*, ch10) calls a blind `try`/`except` with `pass` exception eating. In his example, dividing a list by a string base returned an empty list with no error. Catching only `ZeroDivisionError` dropped the zero element and returned 99 of 100 results; his fixed version substitutes 0.0 for that element and raises a custom `CalculationError` if input and output lengths differ. He advises logging time, exception type, values and function name, re-raising when input is invalid, and replacing print with logs sent to a central, parseable destination such as MLflow or a logging service. He says doing this costs about 30 extra minutes and finds a failure's source in minutes rather than days (his experience, no data). The examples are small synthetic cases.

## See Also
- [[Python Foundations Reference]] — prerequisite-for (basic try/except and `with open`)
- [[Python Data Model and Idioms]] — prerequisite-for (`__enter__`/`__exit__` are dunders)
- [[Python Concurrency Models]] — extends (TaskGroup failures surface as ExceptionGroup)
- [[Programming Curriculum]] — related (course map)
- [[Clean Code: Error Handling and Boundaries]] — extends (a Java-era argument for exceptions over error codes, and wrapping third-party errors)
