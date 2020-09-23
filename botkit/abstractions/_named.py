from abc import ABC, abstractmethod


class INamed(ABC):
    @property
    @abstractmethod
    def unique_name(self) -> str:
        ...
