from typing import Any, Callable, List, Type, TypeVar, Union

import decorators
from haps import Egg, egg

from botkit.routing.route_builder.builder import RouteBuilder
from ._module import Module

# region types

# noinspection PyTypeHints
egg.factories: List[Egg]
# endregion


class ModuleDecorator(decorators.Decorator):
    def __call__(self, *args, **kwargs) -> Type[Module]:
        return super().__call__(*args, **kwargs)

    def decorate_class(
        self, cls: Type[Module], *dec_args, **dec_kwargs
    ) -> Type[Module]:
        if not issubclass(cls, Module):
            raise TypeError(
                f"Can only use the @module decorator on classes that inherit from {Module.__name__}."
            )
        egg.factories.append(
            Egg(type_=cls, qualifier=cls.__name__, egg_=cls, base_=Module, profile=None)
        )
        return cls

    def decorate_func(
        self, func: Callable[[RouteBuilder], Any], name: str = None, *args, **dec_kwargs
    ) -> Type[Module]:
        class_name = name if name else format_module_name(func.__name__)
        module_cls = type(
            class_name,
            (Module,),
            {"register": lambda self, routes: func(routes=routes)},
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


# def module(decorated: Union[Callable, Type[M]]) -> Type[Module]:  # TODO: *args, profile: str = None
#     if inspect.isclass(decorated):
#         if not issubclass(decorated, Module):
#             raise TypeError(f"Can only use the @module decorator on classes that inherit from {Module.__name__}.")
#         egg.factories.append(
#             Egg(type_=decorated, qualifier=decorated.__name__, egg_=decorated, base_=Module, profile=None,)
#         )
#         return decorated
#     else:  # decorated function
#
#         class_name = _snake_to_camel(decorated.__name__)
#         module_cls = type(class_name, (Module,), {"register": lambda self, routes: decorated(routes=routes)},)
#         egg.factories.append(Egg(type_=module_cls, qualifier=class_name, egg_=module_cls, base_=Module, profile=None,))
#         return decorated


def format_module_name(word):
    return _snake_to_upper_camel(word)


def _snake_to_upper_camel(word):
    return "".join(x.capitalize() or "_" for x in word.split("_"))
