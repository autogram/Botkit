from botkit.abstractions._named import INamed
from botkit.builders.callbackbuilder import CallbackBuilder
from botkit.persistence.callback_store import MemoryDictCallbackStore
import pytest

SEP = "##"


class SomeEntity(INamed):
    def __init__(self, name: str):
        self.name = name

    @property
    def unique_name(self) -> str:
        return self.name


@pytest.fixture(scope="function")
def cb_builder():
    return CallbackBuilder(None, MemoryDictCallbackStore())


@pytest.fixture(scope="function")
def gen_named():
    wr = {0}

    def _inner():
        n = wr.pop()
        wr.add(n + 1)

        return SomeEntity(f"testing{n}")

    return _inner


def test_push(cb_builder, gen_named):
    assert cb_builder._current_action_prefix == ""
    cb_builder.push_scope(gen_named())
    assert cb_builder._current_action_prefix == "testing0"
    cb_builder.push_scope(gen_named())
    assert cb_builder._current_action_prefix == f"testing0{SEP}testing1"
    cb_builder.push_scope(gen_named())
    assert cb_builder._current_action_prefix == f"testing0{SEP}testing1{SEP}testing2"


def test_pop(cb_builder, gen_named):
    for i in range(3):
        cb_builder.push_scope(gen_named())

    assert cb_builder._current_action_prefix == f"testing0{SEP}testing1{SEP}testing2"
    cb_builder.pop_scope()
    assert cb_builder._current_action_prefix == f"testing0{SEP}testing1"
    cb_builder.pop_scope()
    assert cb_builder._current_action_prefix == "testing0"
    cb_builder.pop_scope()
    assert cb_builder._current_action_prefix == ""


def test_push_pop_root(cb_builder, gen_named):
    with cb_builder.scope(gen_named()):
        assert cb_builder._current_action_prefix == "testing0"
    assert cb_builder._current_action_prefix == ""


def test_push_pop_levels_deep(cb_builder, gen_named):
    with cb_builder.scope(gen_named()):
        assert cb_builder._current_action_prefix == "testing0"
        with cb_builder.scope(gen_named()):
            assert cb_builder._current_action_prefix == f"testing0{SEP}testing1"
            with cb_builder.scope(gen_named()):
                assert cb_builder._current_action_prefix == f"testing0{SEP}testing1{SEP}testing2"
    assert cb_builder._current_action_prefix == ""


def test_whitespace(cb_builder, gen_named):
    cb_builder.push_scope(SomeEntity("  aa f cc "))
    assert cb_builder._format_action(" k e k ") == f"aafcc{SEP}kek"
