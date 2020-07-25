import inspect

from botkit.utils.typed_callable import TypedCallable
from botkit.views.botkit_context import BotkitContext


def test_num_non_optional_parameters():
    def my_func(ctx: BotkitContext):
        pass

    tc = TypedCallable(my_func)

    assert tc.num_non_optional_params == 1
