from haps import base, egg, SINGLETON_SCOPE, scope as haps_scope
import decorators
from typing import TypeVar

T = TypeVar("T")


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

    def decorate(self, cls: T, scope=SINGLETON_SCOPE, **kwargs) -> T:
        base(cls)
        egg(cls)
        haps_scope(scope)(cls)
        return cls


service = _ServiceDecorator
