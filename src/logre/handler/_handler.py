import logging
from threading import RLock
from typing import Callable, TextIO, Union

from logre.const import IS_RUNNING_IN_PYCHARM
from logre.handler.base import HandlerBase
from logre.record import LogreRecord
from logre.sink.abc import AbstractSink
from logre.sink.callable import CallableSink
from logre.sink.standard import StandardSink
from logre.typedefs import StrOrPath, Writable

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logre.filter import Filter, BaseFilter

    FilterTYpe = Union[Filter, BaseFilter, logging.Filter]

__all__ = ("Handler",)

FileSinkArgsType = StrOrPath | TextIO | Writable
SinkArgsType = FileSinkArgsType | Callable[[LogreRecord], None] | AbstractSink

_LOCK = RLock()


class Handler(HandlerBase):
    def add_keywords(self, *keywords: str) -> None:
        for keyword in keywords:
            if keyword not in self._keywords:
                with _LOCK:
                    if keyword not in self._keywords:
                        self._keywords.append(keyword)

    def remove_keywords(self, *keywords: str) -> None:
        for keyword in keywords:
            if keyword in self._keywords:
                with _LOCK:
                    if keyword in self._keywords:
                        self._keywords.remove(keyword)

    def add_sink(self, sink: SinkArgsType) -> None:
        if sink is None:
            sink = StandardSink(width=180 if IS_RUNNING_IN_PYCHARM else None)
        elif isinstance(sink, AbstractSink):
            sink = sink
        elif callable(sink):
            sink = CallableSink(sink)  # ty:ignore[invalid-argument-type]
        # else:
        #     sink = FileSink(sink)

        self._sinks.append(sink)  # ty:ignore[invalid-argument-type]

    def remove_sink(self, sink: AbstractSink | None = None) -> bool:
        if sink is None:
            result = bool(self._sinks)
            self._sinks = []
            return result
        if sink in self._sinks:
            self._sinks.remove(sink)  # ty:ignore[invalid-argument-type]
            return True
        return False

    def close(self) -> None:
        for sink in self._sinks:
            sink.tasks_to_complete()

    def addFilter(self, filter: "FilterTYpe") -> None:
        super().addFilter(filter)
