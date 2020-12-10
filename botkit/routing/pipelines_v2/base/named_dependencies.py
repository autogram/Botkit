import inspect
from dataclasses import dataclass
from functools import reduce
from typing import Any, Awaitable, Callable, Generic, List, Type, TypeVar, Union, cast

from injector import Binder, Injector, _infer_injected_bindings, inject

from botkit.routing.pipelines_v2.base.middleware import (
    MiddlewareSignature,
    NextDelegate,
)
from botkit.routing.pipelines_v2.base.scopes import EventScope

T = TypeVar("T")


class _NamedDependency:
    pass


class Named(Generic[T]):
    def __class_getitem__(cls, dependency: T, name: str) -> T:
        try:
            bindings = _infer_injected_bindings(function, only_explicit_bindings=False)
            read_and_store_bindings(function, bindings)
        except _BindingNotYetAvailable:
            cast(Any, function).__bindings__ = "deferred"

        dependency.__


class Foo:
    pass


class Bar:
    @inject
    def __init__(self):
        pass


def configure(binder: Binder):
    binder.bind(Named[Foo])


inj = Injector()
inj.get(Named[Abc, "your_mome"])
