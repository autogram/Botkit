from haps import base, egg, SINGLETON_SCOPE, scope as haps_scope
import decorators
from typing import Any, Callable, TypeVar, no_type_check, no_type_check_decorator, overload

T = TypeVar("T")


@no_type_check
class _ServiceDecorator(decorators.ClassDecorator):

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

    def decorate(self, klass, scope=SINGLETON_SCOPE, **kwargs) -> Any:
        base(klass)
        egg(klass)
        haps_scope(scope)(klass)
        return klass


service = _ServiceDecorator
