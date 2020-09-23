from abc import ABC
from typing import Any, Iterable, NoReturn, Union


class IAsyncLoadUnload(ABC):
    async def load(self) -> Union[NoReturn, Any]:
        """
        Performs some asynchronous work on system startup. Telegram client instances will have been registered at this
        point, so running some initial startup tasks using live data is possible.

        Possible use-cases for `load`:
        - Starting worker futures on the event loop
        - Initializing caches
        - Anything that should happen on system start but requires async execution

        If you want an asynchronous load result to be available during module registration, you can return it here and
        it will be available under the `load_result` property of the route builder in the synchronous `Module.register`.
        If you decide to do so, make sure to annotate the generic `RouteBuilder` with the appropriate type. For
        example, if `load` returns an instance of `MyLoadResultType`, you want to annotate your module's `register`
        method with as `def register(self, routes: RouteBuilder[MyLoadResultType]): ...`.

        Returns:
            Either `None`, or any object that should be available under `routes.load_result`.
        """

    async def unload(self) -> NoReturn:
        """
        Reverts the actions taken by the `load` method. This is important for modules to deactivate correctly, as
        otherwise running workers might not terminate even if they should shut down together with the module.
        If you don't care about activation and deactivation of modules at runtime, you don't need this.
        """

    def _get_loadable_members(self) -> "Iterable[IAsyncLoadUnload]":
        ...
