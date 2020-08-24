from typing import Any, Awaitable, Callable, Type, Union

from botkit.routing.types import TState

# noinspection PyMissingTypeHints
from botkit.views.botkit_context import BotkitContext

GathererSignature = Union[
    Callable[[], Union[Any, Awaitable[TState]]],
    Callable[[BotkitContext], Union[Any, Awaitable[TState]]],
    Type,  # A state type to be instantiated (parameterless)
]
GathererSignatureExamplesStr = """
- def () -> TState
- def (context: BotkitContext) -> TState
- async def () -> TState
- async def (context: BotkitContext) -> TState
""".strip()
GathererSignatureExamplesStr = str(GathererSignature)
