from botkit.routing.route_builder.action_expression_base import ActionExpressionBase

from buslane.events import Event

from botkit.routing.route_builder.action_expression_base import ActionExpressionBase


# @dataclass
# class RegisterUserEvent(Event):
#     email: str
#     password: str
#
#
# class RegisterUserCommandHandler(EventHandler[RegisterUserEvent]):
#
#     def handle(self, command: RegisterUserEvent) -> None:
#         pass  # TODO


# event_bus.register(handler=RegisterUserCommandHandler())
# event_bus.publish(command=RegisterUserEvent(
#     email='john@lennon.com',
#     password='secret',
# ))


class PublishActionExpressionMixin(ActionExpressionBase):
    # _event_bus:  = Inject()

    def publish(self, event: Event):
        raise NotImplementedError()
        # self._routes.add_for_current_client()
        # pass


# async def build_handler()
