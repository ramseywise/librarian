from __future__ import annotations

import pytest

from tools.codemap import parser


@pytest.mark.unit
def test_registering_fake_language_dispatches_correctly() -> None:
    """Proves the LANGUAGES dispatch mechanism works for an extension other
    than .py, using the real Python grammar under a second registry key —
    no second grammar dependency required to validate the abstraction."""
    fake_config = parser.LanguageConfig(
        name="python-fake",
        extensions=(".fakepy",),
        ts_language=parser._PY_LANGUAGE,
        def_node_types={"function_definition": "function", "class_definition": "class"},
        import_node_types=("import_statement", "import_from_statement"),
    )
    parser.LANGUAGES[".fakepy"] = fake_config
    try:
        result = parser.parse_source(b"def hi():\n    pass\n", ext=".fakepy")
        assert any(s.name == "hi" and s.kind == "function" for s in result.symbols)
    finally:
        del parser.LANGUAGES[".fakepy"]


@pytest.mark.unit
def test_unregistered_extension_raises() -> None:
    with pytest.raises(ValueError, match="no parser registered"):
        parser.parse_source(b"", ext=".rs")


@pytest.mark.unit
def test_default_extension_is_python() -> None:
    result = parser.parse_source(b"def hi():\n    pass\n")
    assert any(s.name == "hi" for s in result.symbols)
