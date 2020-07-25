import re
from abc import ABC

from abc import ABCMeta, abstractmethod
from typing import Optional, Union, Any


class IInlineModeContext(ABC):
    @abstractmethod
    def format_query(self, user_input: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def matches(self, query: str) -> Any:
        pass

    @abstractmethod
    def parse_input(
        self, query: str, match_result: Any = None
    ) -> Optional[Union[bool, str]]:
        pass


class DefaultInlineModeContext(IInlineModeContext):
    def format_query(self, user_input: Optional[str] = None) -> str:
        return user_input or ""

    def matches(self, query: str) -> Any:
        return True

    def parse_input(self, query: str, match_result: Any = None) -> Optional[str]:
        return query


class HashtagInlineModeContext(IInlineModeContext):
    def format_query(self, user_input: Optional[str] = None) -> str:
        return user_input or ""

    def matches(self, query: str) -> Any:
        return self.tag in query

    def parse_input(self, query: str, match_result: Any = None) -> Optional[str]:
        return query


class PrefixBasedInlineModeContext(IInlineModeContext):
    def __init__(self, prefix: str, delimiter: str = ": "):
        self.prefix = prefix.rstrip(delimiter).strip()
        self.delimiter = delimiter
        re_delimiter = re.escape(delimiter.strip())
        re_prefix = re.escape(self.prefix)
        self._pattern = re.compile(
            f"^{re_prefix}\\s*{re_delimiter}\\s*(.*)", re.IGNORECASE | re.DOTALL
        )

    def format_query(self, user_input: Optional[str] = None) -> str:
        return f"{self.prefix}{self.delimiter}{(user_input or '').strip()}"

    def matches(self, query: str) -> Union[bool, str]:
        match = self._pattern.match(query)
        if not match:
            return False
        return match.group(1).strip()

    def parse_input(self, query: str, match_result: Any = None) -> Union[bool, str]:
        return match_result
