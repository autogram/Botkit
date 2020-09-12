from functools import update_wrapper

from botkit.routing.pipelines.factory_types import ICallbackStepFactory
from botkit.routing.pipelines.steps._base import StepError
from botkit.routing.pipelines.reducer import ReducerSignature
from botkit.routing.pipelines.steps.helpers.state_generators import update_view_state_if_applicable
from botkit.utils.botkit_logging.setup import create_logger


class CollectStepError(StepError[ReducerSignature]):
    pass


# noinspection PyMissingTypeHints
class CollectStepFactory(ICallbackStepFactory[ReducerSignature]):
    @classmethod
    def create_step(cls, collector):
        if not collector:
            return None, None

        log = create_logger("collector")
        is_coroutine = collector.is_coroutine

        if is_coroutine:

            async def postprocess_data_async(context):
                try:
                    log.debug(f"Postprocessing state using collector {collector.name}")
                    return await collector.func(context)
                except Exception as e:
                    raise CollectStepError(e)

            return postprocess_data_async, is_coroutine
        else:

            def postprocess_data(context):
                try:
                    log.debug(f"Postprocessing state using collector {collector.name}")
                    return collector.func(context)
                except Exception as e:
                    raise CollectStepError(e)

            return postprocess_data, is_coroutine
