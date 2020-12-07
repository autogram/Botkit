from injector import Binder

from .callbackbuilder import CallbackBuilder
from .htmlbuilder import HtmlBuilder
from .menubuilder import MenuBuilder
from .metabuilder import MetaBuilder
from .quizbuilder import QuizBuilder
from .viewbuilder import ViewBuilder


def configure_builders(binder: Binder) -> None:
    binder.bind(CallbackBuilder)
    binder.bind(QuizBuilder)
    binder.bind(HtmlBuilder)
    binder.bind(MenuBuilder)
    binder.bind(MetaBuilder)
    binder.bind(ViewBuilder)
