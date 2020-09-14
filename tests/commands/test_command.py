# import pytest
# from ensure import ensure
#
# from botkit.commands.command import CommandParser, _ParsedCommandDefinition
# from botkit.core.modules._module import Module
# from botkit.routing.route_builder.builder import RouteBuilder
#
#
# class TestModule(Module):
#     def register(self, routes: RouteBuilder):
#         routes.on_command(_ParsedCommandDefinition(trigger=CommandParser(name=["test"])))
#
#
# @pytest.mark.parametrize(
#     "trigger_value,exp_name,exp_aliases",
#     [
#         ("abc", "abc", []),
#         (("main", "secondary"), "main", ["secondary"]),
#         (["main", "secondary"], "main", ["secondary"]),
#     ],
# )
# def test_initialization(trigger_value, exp_name, exp_aliases):
#     c = _ParsedCommandDefinition(trigger=trigger_value)
#     assert isinstance(c.trigger, CommandParser)
#     assert c.trigger.name == exp_name
#     assert c.trigger.aliases == exp_aliases
