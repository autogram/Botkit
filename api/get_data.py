import inspect
from typing import Any, Callable

# from pyrogram.client.methods import Methods
#
#
# class APIMethods(Methods):
#     pass


def format_method_sig(name: str, method: Callable):
    sig = inspect.signature(method)
    return f"{method.__name__}{str(sig).replace('self, ', '')}"


def flt(m: Any) -> bool:
    if not inspect.isfunction(m):
        return False
    if m.__name__.startswith("_"):
        return False
    return True


if __name__ == "__main__":
    for m in inspect.getmembers(APIMethods, predicate=flt):
        print(format_method_sig(*m))
