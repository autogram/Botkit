from abc import ABC

from botkit.abstractions import IAsyncLoadUnload


class Service(IAsyncLoadUnload, ABC):
    pass
