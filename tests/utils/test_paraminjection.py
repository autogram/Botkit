import pytest

from botkit.utils.paraminjection import ParameterInjector


class AFoo:
    pass


class ABar(AFoo):
    pass


class B:
    pass


def test_initialization():
    ParameterInjector(dict())


def test_all_simple_parameters_injected_into_callback():
    # noinspection PyUnusedLocal
    async def callback(a: AFoo, b: B) -> None:
        pass

    references = {AFoo: AFoo(), B: B()}
    inj = ParameterInjector(references)
    kwargs = inj.map_kwargs(callback)

    assert kwargs.get("a") == references[AFoo]
    assert kwargs.get("b") == references[B]


def test_extra_nondefault_args_raises():
    # noinspection PyUnusedLocal
    async def callback(b: B, c: str) -> None:
        assert b is not None
        assert c is not None

    references = {B: B()}
    inj = ParameterInjector(references)

    with pytest.raises(ValueError):
        assert inj.map_kwargs(callback)


def test_extra_default_kwargs_param_ignored():
    # noinspection PyUnusedLocal
    async def callback(b: B, c: str = "") -> None:
        pass

    references = {B: B()}
    inj = ParameterInjector(references)
    kwargs = inj.map_kwargs(callback)

    assert kwargs.get("b") == references[B]
    assert "c" not in kwargs


def test_extra_none_default_kwargs_param_ignored():
    # noinspection PyUnusedLocal
    async def callback(b: B, c: str = None) -> None:
        pass

    references = {B: B()}
    inj = ParameterInjector(references)
    kwargs = inj.map_kwargs(callback)

    assert kwargs.get("b") == references[B]
    assert "c" not in kwargs


def test_covariant_arg_injected():
    # noinspection PyUnusedLocal
    async def callback(a: AFoo) -> None:
        pass

    references = {ABar: ABar()}
    inj = ParameterInjector(references)
    kwargs = inj.map_kwargs(callback)

    assert kwargs.get("a") == references[ABar]


def test_contravariant_arg_raises():
    # noinspection PyUnusedLocal
    async def callback(a: ABar, b: B) -> None:
        pass

    references = {type(AFoo): AFoo(), type(B): B()}
    inj = ParameterInjector(references)

    with pytest.raises(ValueError):
        kwargs = inj.map_kwargs(callback)
