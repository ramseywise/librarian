"""tree-sitter driver — extracts symbols, import edges, and call edges from source files.

Language support is a registry (LANGUAGES, keyed by file extension) so adding a
second language later is a small addition, not a rewrite. Only Python is
registered today — no other grammar dependency is installed.

Symbol extraction: def_node_types-listed nodes become symbol records
(top-level functions/classes get kind='function'/'class'; nested functions
inside a class body get kind='method', tracked via a parent-scope stack).

Import extraction: import-shaped nodes become raw import-target strings;
resolving them to file_id targets within a repo is the indexer's job
(parser.py has no notion of a repo root or other files). The extraction body
itself is still Python-grammar-specific — not yet abstracted across
languages, since there's no second real grammar to validate a generic shape
against.

Call extraction: call-shaped nodes become raw callee-name strings, associated
with the enclosing symbol (if any) by byte offset. Resolving callee names to
symbol_ids is the indexer's job, same as imports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import tree_sitter_python as tspython
from tree_sitter import Language, Node, Parser

_PY_LANGUAGE = Language(tspython.language())


@dataclass(frozen=True)
class LanguageConfig:
    name: str
    extensions: tuple[str, ...]
    ts_language: Language
    def_node_types: dict[str, str]  # tree-sitter node type -> 'function' | 'class'
    import_node_types: tuple[str, ...]
    call_node_type: str | None = None


LANGUAGES: dict[str, LanguageConfig] = {
    ".py": LanguageConfig(
        name="python",
        extensions=(".py",),
        ts_language=_PY_LANGUAGE,
        def_node_types={"function_definition": "function", "class_definition": "class"},
        import_node_types=("import_statement", "import_from_statement"),
        call_node_type="call",
    ),
}


@dataclass
class Symbol:
    name: str
    kind: str  # 'function' | 'class' | 'method'
    signature: str
    docstring: str
    parent_scope: str | None
    start_line: int
    end_line: int
    start_byte: int
    end_byte: int


@dataclass
class ImportRef:
    target: str  # dotted module path as written, e.g. 'os.path' or '.manifest'


@dataclass
class CallRef:
    caller_symbol_start_byte: int | None  # start_byte of enclosing Symbol, None if module-level
    callee_name: str  # bare name, e.g. 'foo' or 'bar' (from self.bar() / obj.bar())


@dataclass
class ParseResult:
    symbols: list[Symbol] = field(default_factory=list)
    imports: list[ImportRef] = field(default_factory=list)
    calls: list[CallRef] = field(default_factory=list)


def _node_text(node: Node, source: bytes) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def _docstring(body: Node, source: bytes) -> str:
    """First statement of a block, if it's a bare string expression."""
    if body.child_count == 0:
        return ""
    first = body.children[0]
    if first.type != "expression_statement" or first.child_count == 0:
        return ""
    string_node = first.children[0]
    if string_node.type != "string":
        return ""
    text = _node_text(string_node, source)
    return text.strip("\"'").strip()


def _signature(def_node: Node, source: bytes) -> str:
    """Text of the def/class line up to (but not including) the trailing colon+body."""
    header_end = def_node.end_byte
    for child in def_node.children:
        if child.type == "block":
            header_end = child.start_byte
            break
    text = source[def_node.start_byte : header_end].decode("utf-8", errors="replace")
    return text.rstrip().rstrip(":").strip()


def _def_name(def_node: Node, source: bytes) -> str:
    for child in def_node.children:
        if child.type == "identifier":
            return _node_text(child, source)
    return "<anonymous>"


def _call_target_name(func_node: Node, source: bytes) -> str | None:
    """Bare callee name from a call's function node — the rightmost identifier
    for attribute access (self.bar() / obj.bar() -> 'bar'), matching how
    Symbol.name stores bare method names (not qualified)."""
    if func_node.type == "identifier":
        return _node_text(func_node, source)
    if func_node.type == "attribute":
        attr = next((c for c in reversed(func_node.children) if c.type == "identifier"), None)
        return _node_text(attr, source) if attr else None
    return None


def _walk(
    node: Node,
    source: bytes,
    result: ParseResult,
    scope_stack: list[tuple[str, str, int]],
    lang: LanguageConfig,
) -> None:
    """Recursively walk the AST, collecting symbols, imports, and calls.

    scope_stack holds (name, kind, start_byte) triples for enclosing def/class
    scopes so nested functions are correctly classified as methods vs. free
    functions, and so call sites can be attributed to their enclosing symbol.
    """
    for child in node.children:
        if child.type in lang.def_node_types:
            kind = lang.def_node_types[child.type]
            parent_scope = scope_stack[-1][0] if scope_stack else None
            if kind == "function" and scope_stack and scope_stack[-1][1] == "class":
                kind = "method"

            name = _def_name(child, source)
            body = next((c for c in child.children if c.type == "block"), None)
            docstring = _docstring(body, source) if body else ""

            result.symbols.append(
                Symbol(
                    name=name,
                    kind=kind,
                    signature=_signature(child, source),
                    docstring=docstring,
                    parent_scope=parent_scope,
                    start_line=child.start_point[0] + 1,
                    end_line=child.end_point[0] + 1,
                    start_byte=child.start_byte,
                    end_byte=child.end_byte,
                )
            )

            scope_stack.append((name, lang.def_node_types[child.type], child.start_byte))
            _walk(child, source, result, scope_stack, lang)
            scope_stack.pop()

        elif lang.name == "python" and child.type == "import_statement":
            for dotted in child.children:
                if dotted.type == "dotted_name":
                    result.imports.append(ImportRef(target=_node_text(dotted, source)))
                elif dotted.type == "aliased_import":
                    name_node = next((c for c in dotted.children if c.type == "dotted_name"), None)
                    if name_node:
                        result.imports.append(ImportRef(target=_node_text(name_node, source)))
            _walk(child, source, result, scope_stack, lang)

        elif lang.name == "python" and child.type == "import_from_statement":
            module_node = next(
                (c for c in child.children if c.type in ("dotted_name", "relative_import")),
                None,
            )
            if module_node:
                result.imports.append(ImportRef(target=_node_text(module_node, source)))
            _walk(child, source, result, scope_stack, lang)

        elif lang.call_node_type and child.type == lang.call_node_type:
            func_node = child.children[0] if child.children else None
            callee_name = _call_target_name(func_node, source) if func_node else None
            if callee_name:
                caller_start_byte = None
                for _, scope_kind, start_byte in reversed(scope_stack):
                    if scope_kind in ("function", "class"):
                        caller_start_byte = start_byte
                        break
                result.calls.append(
                    CallRef(caller_symbol_start_byte=caller_start_byte, callee_name=callee_name)
                )
            _walk(child, source, result, scope_stack, lang)

        else:
            _walk(child, source, result, scope_stack, lang)


def parse_source(source: bytes, ext: str = ".py") -> ParseResult:
    """Parse source bytes into symbols + import/call references.

    ext selects the language via the LANGUAGES registry (default .py).
    Raises ValueError if no language is registered for ext.
    """
    lang = LANGUAGES.get(ext)
    if lang is None:
        raise ValueError(f"no parser registered for extension {ext!r}")
    parser = Parser(lang.ts_language)
    tree = parser.parse(source)
    result = ParseResult()
    _walk(tree.root_node, source, result, [], lang)
    return result


def parse_file(path: str) -> ParseResult:
    ext = Path(path).suffix
    with open(path, "rb") as f:
        source = f.read()
    return parse_source(source, ext=ext)
