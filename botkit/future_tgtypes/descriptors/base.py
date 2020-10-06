from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic.dataclasses import dataclass

from botkit.agnostic.annotations import IClient

T = TypeVar("T")


@dataclass
class Descriptor(ABC, Generic[T]):
    @abstractmethod
    async def resolve(self, client: IClient) -> T:
        ...
