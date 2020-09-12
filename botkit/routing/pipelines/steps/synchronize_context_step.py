from typing import Any, Awaitable

from haps import Inject

from botkit.persistence.data_store import IDataStore
from botkit.routing.pipelines.factory_types import IPipelineStep
from botkit.views.botkit_context import Context


class SynchronizeContextStep(IPipelineStep):
    data_store: IDataStore = Inject()

    def __call__(self, context: Context) -> Awaitable[Any]:
        return self.data_store.synchronize_context_data(context)
