import inspect
import sys
import threading

_trace_state = threading.local()


async def _call_and_jump(func, target, coro_locals, *args, kwargs):
    def _trace_global(frame, event, arg):
        # print(frame, event, arg)
        if event == "call" and frame.f_code is func.__code__:
            return _trace_local

    def _trace_local(frame, event, arg):
        # print(frame, event, arg)
        if event == "line" and frame.f_code is func.__code__:
            if getattr(_trace_state, "first", True):
                frame.f_lineno = frame.f_lineno + target - 1
                _trace_state.first = False
                return None
            else:
                _trace_state.first = True
        return _trace_local

    oldtrace = sys.gettrace()
    sys.settrace(_trace_global)
    inspect.currentframe().f_trace = _trace_global
    try:
        ret = func(*args, **kwargs)
        try:
            fut = ret.send(None)
        except StopIteration:
            fut = None
    finally:
        sys.settrace(oldtrace)
        inspect.currentframe().f_trace = oldtrace
    return ret, fut
