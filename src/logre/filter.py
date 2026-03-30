import functools
import logging
from functools import lru_cache
from typing import Callable, TypeVar

from logre.funcs import resolve_path
from logre.record import LogRecord

try:
    import regex as re
except ImportError:
    import re

__all__ = ("Filter", "BaseFilter", "filter_method", "default_filter")


FilterMethodType = Callable[["Filter", LogRecord], bool]
FT = TypeVar("FT", bound="Filter")


# noinspection PyProtectedMember
class FilterMethod:
    def __init__(self, func: FilterMethodType) -> None:
        self.name = None
        self.func = func

    def __set_name__(self, owner: type["Filter"], name: str) -> None:
        if not hasattr(owner, "_filter_methods"):
            setattr(owner, "_filter_methods", [])
        self.name = name
        owner._filter_methods.append(name)

    def __get__(
        self, instance: FT, owner: type[FT] | None = None
    ) -> Callable[[LogRecord], bool]:
        return functools.partial(self.func, instance)


def filter_method(method: FilterMethodType) -> FilterMethod:
    return FilterMethod(method)


class Filter(logging.Filter):
    _filter_methods: list[str]

    def filter(self, record: LogRecord) -> bool | LogRecord:
        for method_name in self._filter_methods:
            result = getattr(self, method_name)(record)
            if isinstance(result, LogRecord):
                record = result
                continue
            if not result:
                return False

        return record


class BaseFilter(Filter):
    _FILTERED_MODULE = []

    @lru_cache(maxsize=128)
    def _filter_for_module(self, module) -> bool:
        for regex in self._FILTERED_MODULE:
            if re.findall(regex, module):
                return True
        return False

    @filter_method
    def filter_module(self, record: LogRecord) -> bool:
        module = resolve_path(record.pathname)
        return not self._filter_for_module(module)


default_filter = BaseFilter()
