import functools
import logging
import os
from concurrent.futures import ThreadPoolExecutor
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

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "")
        self._executor = ThreadPoolExecutor(max_workers=os.cpu_count() * 2)

    def filter(self, record: LogRecord) -> bool:
        def execute(_method: str) -> bool:
            return getattr(self, _method)(record)

        return any(self._executor.map(execute, self._filter_methods))


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
