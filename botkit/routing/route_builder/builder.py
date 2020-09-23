from typing import Generic

from botkit.routing.route_builder.expressions import TLoadResult
from .route_builder_base import RouteBuilderBase
from .state_machine_mixin import StateMachineMixin


class RouteBuilder(RouteBuilderBase, StateMachineMixin, Generic[TLoadResult]):
    pass
