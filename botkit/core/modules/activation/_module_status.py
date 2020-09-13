from enum import Enum, auto


class ModuleStatus(Enum):
    inactive = auto()
    active = auto()
    disabled = auto()
    failed = auto()
