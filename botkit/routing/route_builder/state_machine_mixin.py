import inspect
import importlib.util
import traceback
from io import StringIO
from typing import (
    Iterable,
    Optional,
    Union,
    overload,
)

from ast import literal_eval, parse, Constant, Assign, Call
from uuid import uuid4

from .has_route_collection import IRouteCollection
from .state_route_builder import StateRouteBuilder


class StateMachineMixin(IRouteCollection):
    @overload
    def state_machine(self, states: Iterable[str]) -> Iterable[StateRouteBuilder]:
        ...

    @overload
    def state_machine(self, num_states: int) -> Iterable[StateRouteBuilder]:
        ...

    @overload
    def state_machine(self) -> Iterable[StateRouteBuilder]:
        ...

    def state_machine(
        self, arg: Optional[Union[int, Iterable[str]]] = None
    ) -> Iterable[StateRouteBuilder]:

        if arg:
            machine_guid = uuid4()
            if isinstance(arg, int):
                for i in range(arg):
                    yield StateRouteBuilder(machine_guid, i, self._route_collection)
            else:
                for i, name in enumerate(arg):
                    yield StateRouteBuilder(machine_guid, i, self._route_collection, name=name)
        else:
            stack = inspect.stack()
            caller = stack[1]
            caller_frame = caller.frame
            caller_filename = caller.filename

            f_code = caller_frame.f_code
            f_locals = caller_frame.f_locals
            f_trace = caller_frame.f_trace
            f_trace_lines = caller_frame.f_trace_lines

            # spec = importlib.util.spec_from_file_location("module.name", caller_filename)
            # caller_module = importlib.util.module_from_spec(spec)
            # spec.loader.load_module(caller_module.__name__)

            # calling_function = getattr(caller_module, caller.function)

            frame = inspect.stack()[1]
            code = StringIO()
            deparse_code2str(frame.frame.f_code, out=code)
            func_code = code.getvalue()

            STATE_MACHINE_FUNC_NAME = "routes.state_machine"
            with open(caller_filename, "r") as f:
                con = f.read()

            parsed = parse(con)
            for node in parsed.body:
                line_no = node.end_lineno
                try:
                    if (
                        isinstance(node, Assign)
                        and not hasattr(node.targets[0], "id")
                        and isinstance(node.value, Call)
                        and node.value.func.id == STATE_MACHINE_FUNC_NAME
                    ):
                        amount_of_items = len(node.targets[0].elts)
                        node.value.args.append(
                            Constant(value=amount_of_items, lineno=0, col_offset=0)
                        )
                except Exception as ex:
                    traceback.print_exc(ex)
            code = compile(parsed, "", "exec")
            exec(code)


"""
TODO: - https://t.me/python_talk/19219


def test_stuff():
    from re import compile

    class a:
        pattern = compile("\d+")

        def __iter__(self):
            yield from (1, 2, 3)

        def __enter__(self):
            return self

        def __exit__(self, *exit):
            if exit[0] is ValueError:
                r = self.pattern.findall(str(exit[1]))
                n = int(r[0])
                print(n)
                return True

    a = a()
    with a:
        a, b, c, d = a
        print(a, b, c, d)
"""
