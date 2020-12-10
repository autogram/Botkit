from injector import Binder, Provider, inject, provider, Module, Injector, multiprovider, singleton

from botkit.routing import MiddlewareModule
from botkit.routing.pipelines_v2.base import EventPipeline


def test_module():
    inj = Injector([MiddlewareModule()])
    # module = inj.get(EventPipeline[str])
