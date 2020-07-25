import time
from typing import Callable, Any

from dataclasses import dataclass


@dataclass
class Measurement:
    func: Callable
    result: Any
    duration_ms: float

    def duration_str(self):
        if self.duration_ms > 1000:
            return "{:.1f}s".format(self.duration_ms / 1000)
        else:
            return "{:.5}ms".format(self.duration_ms)

    def __str__(self):
        return "{} function took {:.3f} ms".format(self.func.__name__, self.duration_ms)


def time_call(func: Callable, *args, **kwargs) -> Measurement:
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()

    return Measurement(func=func, result=result, duration_ms=(end - start) * 1000.0)
