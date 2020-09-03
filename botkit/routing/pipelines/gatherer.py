from typing import Any, Awaitable, Callable, Type, Union

from botkit.routing.types import TState

# noinspection PyMissingTypeHints
from botkit.views.botkit_context import Context

GathererSignature = Union[
    Callable[[], Union[Any, Awaitable[TState]]],
    Callable[[Context], Union[Any, Awaitable[TState]]],
    Type,  # A state type to be instantiated (parameterless)
]
GathererSignatureExamplesStr = """
- def () -> TState
- def (context: Context) -> TState
- async def () -> TState
- async def (context: Context) -> TState
""".strip()
GathererSignatureExamplesStr = str(GathererSignature)
