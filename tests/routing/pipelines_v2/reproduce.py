from typing import List, Protocol, TypeVar
from typing import (
    Any,
    Callable,
    ClassVar,
    Generic,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    AbstractSet,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    MutableSet,
    Sequence,
    AsyncIterator,
    AsyncIterable,
    Coroutine,
    Collection,
    AsyncGenerator,
    Deque,
    Dict,
    List,
    Set,
    FrozenSet,
    NamedTuple,
    Generator,
    cast,
    overload,
    TYPE_CHECKING,
)
from typing_extensions import TypedDict

from injector import Binder, Injector, InstanceProvider, MultiBindProvider, inject
from injector import Binder, Provider, inject, provider, Module, Injector, multiprovider, singleton

T = TypeVar("T")

# region Callables


class FuncWithProtocol(Protocol[T]):
    def __call__(self, n: int) -> T:
        ...


class TypeUsingProtocol(FuncWithProtocol[T]):
    def __call__(self, n: int):
        pass


class UsesComplicated:
    @inject
    def __init__(self, c: List[FuncWithProtocol]):
        self.c = c


def complicated_thing(n: int) -> None:
    pass


def test_sth():
    def configure(binder: Binder):
        binder.bind(FuncWithProtocol, to=InstanceProvider(complicated_thing))

    inj = Injector([configure])
    c = inj.get(FuncWithProtocol)
    assert c is complicated_thing


def test_manual_multibind_provider_on_functions_matching_protocol_succeeds():
    def configure(binder: Binder):
        binder.bind(UsesComplicated)

        prov = MultiBindProvider()
        prov.append(InstanceProvider(complicated_thing))
        binder.multibind(List[UsesComplicated], to=prov)

    inj = Injector([configure])
    _using = inj.get(UsesComplicated)


# endregion

# region Generics

T = TypeVar("T")


def test_generic_module_without_initializer_injector_can_be_created():
    class GenericModuleNoInit(Module, Generic[T]):
        pass

    def configure(binder: Binder):
        binder.install(GenericModuleNoInit[str])

    Injector([configure])


def test_generic_module_injector_can_be_created():
    class GenericModule(Module, Generic[T]):
        def __init__(self):
            pass

    def configure(binder: Binder):
        binder.install(GenericModule[str])

    Injector([configure])


def test_useful_generic_module_finds_generic_type():
    class Foo(Generic[T]):
        pass

    class ClassUsingInt(Foo[int]):
        pass

    class ClassUsingStr(Foo[str]):
        pass

    class LibraryProvidedGenericModule(Module, Generic[T]):
        @provider
        def t_provider(self) -> List[T]:


    def configure(binder: Binder):
        binder.install(GenericModule[str])

    Injector([configure])


# endregion


# region Other collections


# endregion
