from typing import Any, Dict, List, Literal, Optional, Type, Union, cast

import pytest
from asynctest import MagicMock
from boltons.iterutils import flatten
from injector import Binder, Injector, InstanceProvider, MultiBindProvider
from itertools import permutations

from botkit.routing.pipelines_v2.base import chain_middleware
from botkit.routing.pipelines_v2.eventpipeline import EventPipeline
from botkit.routing.pipelines_v2.base.middleware import (
    AbstractGenericMiddleware,
    MiddlewareChainer,
    MiddlewareSignature,
    NextDelegate,
    TContext,
)

pytestmark = pytest.mark.asyncio


async def test_async_delegate_dispatch_happy_path():
    CType = Dict[str, Optional[Literal[True]]]
    value: CType = dict()

    async def callback(ctx: CType, nxt: NextDelegate[CType]) -> None:
        assert ctx is value
        assert callable(next)
        assert "called" not in ctx
        ctx["called"] = True
        await nxt(ctx)
        assert ctx["called"] is True

    def make_context(x: Any, y: Any) -> CType:
        return value

    # TODO: Why the heck are these typings failing...
    pipeline = EventPipeline(
        [callback], context_initializer=make_context, injector=cast(Injector, None)
    )
    res = await pipeline.dispatch(value, None)
    assert res is None
    assert value["called"] is True


async def test_class_middleware_dispatch_happy_path():
    Context = Dict[str, Optional[Literal[True]]]
    value: Context = dict()

    class MyMiddleware(AbstractGenericMiddleware[Context]):
        async def __call__(self, ctx: Context, nxt: NextDelegate[Context]) -> Any:
            assert ctx is value
            assert callable(next)
            assert "called" not in ctx
            ctx["called"] = True
            await nxt(ctx)
            assert ctx["called"] is True

    delegates = [MyMiddleware]
    pipeline = EventPipeline(delegates, Injector(), lambda _1, _2: value)
    res = await pipeline.dispatch(value, None)
    assert res is None
    assert (
        value["called"] is True
    ), "Class-based middleware has likely only been instantiated, but not called afterwards"


async def test_coroutine_callback_gets_awaited_automatically():
    async def async_callback(ctx, nxt):  # type: ignore
        next(ctx)  # type: ignore

    delegates = [async_callback]  # type: ignore
    pipeline = EventPipeline(delegates, cast(Injector, None), context_initializer=lambda c, _: c)  # type: ignore

    with pytest.warns(None) as record:
        await pipeline.dispatch(dict(), None)
    assert len(record) == 0


async def test_call_without_context_raises():
    pipeline = EventPipeline([lambda _, nxt: nxt()], injector=cast(Injector, None), context_initializer=lambda c, _: c)  # type: ignore
    with pytest.raises(TypeError, match=".*has been called with incorrect arguments.*"):
        await pipeline.dispatch(dict(), None)


async def test_mix_sync_async_delegates_in_dispatch():
    async def async_callback(ctx, nxt):  # type: ignore
        print(next)
        await nxt(ctx)

    delegates = list(flatten(permutations([async_callback, lambda ctx, nxt: nxt(ctx)])))  # type: ignore
    pipeline = EventPipeline(delegates, cast(Injector, None), context_initializer=lambda c, _: c)  # type: ignore
    await pipeline.dispatch(dict(), None)


async def test_inject_():
    def configure(binder: Binder):
        binder.bind(MiddlewareChainer[TContext], to=InstanceProvider(chain_middleware))

    inj = Injector([configure])
    ch = inj.get(MiddlewareChainer[TContext])
    assert ch is chain_middleware


async def test_dispatch_with_dependency_injection():
    ctx = object()
    call_mock = MagicMock()

    def configure(binder: Binder):
        binder.bind(EventPipeline)
        binder.multibind(
            List[MiddlewareSignature[object]], to=InstanceProvider([call_mock])  # type: ignore
        )

    inj = Injector([configure])
    pipeline = inj.get(EventPipeline[object])
    await pipeline.dispatch(None, None)

    call_mock.assert_called_with(ctx)  # type: ignore


async def test_dispatch_switch_out_chain_algorithm():
    TCtx = Dict[str, object]
    call_mock = MagicMock()

    def chain_with_exc(_1, _2):
        raise ValueError("TEST SUCCESS")

    def configure(binder: Binder):
        binder.bind(EventPipeline)
        binder.bind(MiddlewareChainer[TCtx], to=InstanceProvider(chain_with_exc))

        prov = MultiBindProvider()
        prov.append(InstanceProvider(call_mock))
        binder.multibind(
            List[Union[MiddlewareSignature[TCtx], Type[MiddlewareSignature[TCtx]]]], to=prov
        )

    inj = Injector([configure])
    pipeline = inj.get(EventPipeline)
