from __future__ import annotations

import pytest

from tools.codemap.parser import parse_source

FIXTURE = b'''\
"""Module docstring, not a symbol."""

import os
from pathlib import Path
from . import manifest as m


def top_level(y: int) -> int:
    """Top-level doc."""
    return y


class Foo:
    """A class."""

    def bar(self, x: int) -> int:
        """Bar doc."""
        return x

    def baz(self):
        def inner():
            return 1
        return inner()
'''


@pytest.mark.unit
def test_extracts_top_level_function() -> None:
    result = parse_source(FIXTURE)
    fn = next(s for s in result.symbols if s.name == "top_level")
    assert fn.kind == "function"
    assert fn.parent_scope is None
    assert fn.docstring == "Top-level doc."
    assert "def top_level(y: int) -> int" in fn.signature
    assert fn.start_line == 8


@pytest.mark.unit
def test_extracts_class() -> None:
    result = parse_source(FIXTURE)
    cls = next(s for s in result.symbols if s.name == "Foo")
    assert cls.kind == "class"
    assert cls.docstring == "A class."


@pytest.mark.unit
def test_extracts_method_with_parent_scope() -> None:
    result = parse_source(FIXTURE)
    method = next(s for s in result.symbols if s.name == "bar")
    assert method.kind == "method"
    assert method.parent_scope == "Foo"
    assert method.docstring == "Bar doc."


@pytest.mark.unit
def test_nested_function_is_function_not_method() -> None:
    result = parse_source(FIXTURE)
    inner = next(s for s in result.symbols if s.name == "inner")
    assert inner.kind == "function"
    assert inner.parent_scope == "baz"


@pytest.mark.unit
def test_extracts_imports() -> None:
    result = parse_source(FIXTURE)
    targets = {i.target for i in result.imports}
    assert "os" in targets
    assert "pathlib" in targets


@pytest.mark.unit
def test_byte_ranges_are_valid_and_ordered() -> None:
    result = parse_source(FIXTURE)
    for s in result.symbols:
        assert s.start_byte < s.end_byte
        assert s.start_line <= s.end_line


@pytest.mark.unit
def test_extracts_call_attributed_to_enclosing_symbol() -> None:
    result = parse_source(FIXTURE)
    baz = next(s for s in result.symbols if s.name == "baz")
    call = next(c for c in result.calls if c.callee_name == "inner")
    assert call.caller_symbol_start_byte == baz.start_byte


@pytest.mark.unit
def test_module_level_call_has_no_caller_symbol() -> None:
    src = b"foo()\n"
    result = parse_source(src)
    call = next(c for c in result.calls if c.callee_name == "foo")
    assert call.caller_symbol_start_byte is None


@pytest.mark.unit
def test_attribute_call_extracts_bare_method_name() -> None:
    src = b"def f():\n    self.bar()\n    obj.method()\n"
    result = parse_source(src)
    names = {c.callee_name for c in result.calls}
    assert names == {"bar", "method"}


@pytest.mark.unit
def test_nested_calls_are_both_extracted() -> None:
    src = b"def f():\n    outer(inner(x))\n"
    result = parse_source(src)
    names = {c.callee_name for c in result.calls}
    assert names == {"outer", "inner"}
