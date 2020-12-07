from typing import Any, TypeVar

import decorators
from haps import SINGLETON_SCOPE, base, egg, scope as haps_scope

T = TypeVar("T")


class _ServiceDecorator(decorators.Decorator):
    """
    Decorator for marking a class as an injectable service.
    Defaults to SINGLETON_SCOPE as opposed to INSTANCE_SCOPE.

    The following structure:

    ```
    @service
    class MyService: ...
    ```

    is equivalent to:

    ```
    @haps.base
    @haps.egg
    @haps.scope(haps.SINGLETON_SCOPE)
    class MyService: ...
    ```
    """

    def decorate_func(self, func, scope=SINGLETON_SCOPE, *decorator_args, **decorator_kwargs):
        base(func)
        egg(func)
        haps_scope(scope)(func)
        return func

    def decorate_class(
        self, klass, scope=SINGLETON_SCOPE, *decorator_args, **decorator_kwargs
    ) -> Any:
        base(klass)
        egg(klass)
        haps_scope(scope)(klass)
        return klass


service = _ServiceDecorator
