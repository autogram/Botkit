from typing import Any, Callable, List, Type, TypeVar, Union, cast

import decorators
from haps import Egg, egg

from botkit.routing.route_builder.builder import RouteBuilder
from ._module import Module

# region types

egg.factories = cast(List[Egg], egg.factories)


class ModuleDecorator(decorators.Decorator):
    def __call__(self, *args, **kwargs) -> Type[Module]:
        return super().__call__(*args, **kwargs)

    def decorate_class(self, cls: Type[Module], *dec_args, **dec_kwargs) -> Type[Module]:
        if not issubclass(cls, Module):
            raise TypeError(
                f"Can only use the @module decorator on classes that inherit from {Module.__name__}."
            )
        egg.factories.append(
            Egg(type_=cls, qualifier=cls.__name__, egg_=cls, base_=Module, profile=None)
        )
        return cls

    def decorate_func(
        self, func: Callable[[RouteBuilder], Type[Module]], name: str = None, *args, **dec_kwargs
    ) -> Type[Module]:
        class_name = name if name else format_module_name(func.__name__)
        module_cls = type(
            class_name, (Module,), {"register": lambda self, routes: func(routes)},
        )
        egg.factories.append(
            Egg(
                type_=module_cls,
                qualifier=class_name,
                egg_=module_cls,
                base_=Module,
                profile=None,
            )
        )
        return func


""" Decorator for marking a register function or a `Module` class as a botkit module. """
module = ModuleDecorator


def format_module_name(any_str: str):
    return _snake_to_upper_camel(any_str)


def _snake_to_upper_camel(word: str):
    return "".join(x.capitalize() or "_" for x in word.split("_"))
