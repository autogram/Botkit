from typing import TypeVar, Generic, Iterable, List

from pydantic import BaseModel

T = TypeVar("T")


class PaginationModel(Generic[T]):
    def __init__(self, all_items: Iterable[T] = None, items_per_page: int = 1):
        self.all_items = list(all_items or [])
        self._current_page = 0
        self.items_per_page = items_per_page

    @property
    def _begin(self):
        return self._current_page * self.items_per_page

    @property
    def _end(self):
        return min((self._current_page + 1) * self.items_per_page, self.item_count)

    @property
    def item_count(self):
        return len(self.all_items)

    @property
    def page_items(self) -> List[T]:
        return self.all_items[self._begin : self._end]

    @property
    def current_page_number(self) -> int:
        return self._current_page + 1

    @property
    def has_next_page(self) -> bool:
        return self._end < self.item_count

    @property
    def has_previous_page(self) -> bool:
        return self._begin > 0

    def flip_next_page(self):
        self._current_page += 1

    def flip_previous_page(self):
        self._current_page -= 1
