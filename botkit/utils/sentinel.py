import enum

# See https://stackoverflow.com/questions/57959664/handling-conditional-logic-sentinel-value-with-mypy


class Sentinel(enum.Enum):
    sentinel = object()


NotSet = Sentinel.sentinel
