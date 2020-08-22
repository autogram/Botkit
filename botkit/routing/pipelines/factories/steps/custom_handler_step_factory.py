import warnings
from typing import Any, Awaitable, Callable, Optional

from botkit.routing.pipelines.callbacks import HandlerSignature
from botkit.routing.pipelines.factories.factory_types import IStepFactory, TResult, TUserInput
from botkit.routing.pipelines.factories.steps._base import StepError
from botkit.utils.typed_callable import TypedCallable
from botkit.views.base import ModelViewBase
from botkit.views.botkit_context import BotkitContext
from botkit.views.views import MessageViewBase


class HandleStepError(StepError[HandlerSignature]):
    pass


class CustomHandlerStepFactory(
    IStepFactory[TypedCallable[HandlerSignature], Optional[Callable[[BotkitContext], Awaitable[Any]]]]
):
    @classmethod
    def create_step(cls, handler):
        if not handler:
            return None, None

        is_coroutine = handler.is_coroutine

        if is_coroutine:

            async def handle_async(update, context):
                # TODO: Use paraminjector library to make all args optional
                args = (context.client, update, context) if handler.num_parameters == 3 else (context.client, update)

                try:
                    result = await handler.func(*args)
                except Exception as e:
                    raise HandleStepError(handler) from e

                if isinstance(result, ModelViewBase):
                    # TODO
                    warnings.warn(
                        "Would be cool if handlers could directly return a view, right? "
                        "Well, drop me a note on GitHub that you'd also love this feature "
                        "and I'll make it happen :)"
                    )

                return result

            return handle_async, is_coroutine
        else:

            def handle(update, context):
                # TODO: Use paraminjector library to make all args optional
                args = (context.client, update, context) if handler.num_parameters == 3 else (context.client, update)

                try:
                    result = handler.func(*args)
                except Exception as e:
                    raise HandleStepError(handler) from e

                if isinstance(result, ModelViewBase):
                    # TODO
                    warnings.warn(
                        "Would be cool if handlers could directly return a view, right? "
                        "Well, drop me a note on GitHub that you'd also love this feature "
                        "and I'll make it happen :)"
                    )

                return result

            return handle, is_coroutine
