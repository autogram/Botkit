from typing import Any, Awaitable, Callable, Type, Union

from botkit.routing.types import TViewState

# noinspection PyMissingTypeHints
from botkit.botkit_context import Context

GathererSignature = Union[
    Callable[[], Union[Any, Awaitable[TViewState]]],
    Callable[[Context], Union[Any, Awaitable[TViewState]]],
    Type,  # A view_state type to be instantiated (parameterless)
]
GathererSignatureExamplesStr = """
- def () -> TViewState
- def (context: Context) -> TViewState
- async def () -> TViewState
- async def (context: Context) -> TViewState
""".strip()
