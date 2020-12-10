from typing import Awaitable, Callable, Union

from botkit.botkit_context import Context

CollectorSignature = Callable[[Context], Union[None, Awaitable[None]]]
