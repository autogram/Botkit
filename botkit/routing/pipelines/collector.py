from typing import Awaitable, Callable, Union

from botkit.views.botkit_context import Context

CollectorSignature = Callable[[Context], Union[None, Awaitable[None]]]
