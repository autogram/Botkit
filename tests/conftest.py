from haps import Container
from pytest import fixture


@fixture(scope="function", autouse=True)
def reset_container():
    Container._reset()
    yield
    Container._reset()
