from threading import RLock
from typing import Callable, TextIO

from logre.const import IS_RUNNING_IN_PYCHARM
from logre.handler.base import HandlerBase
from logre.record import LogRecord
from logre.sink.abc import AbstractSink
from logre.sink.callable import CallableSink
from logre.sink.standard import StandardSink
from logre.typedefs import StrOrPath, Writable

__all__ = ("Handler",)

SinkArgsType = TextIO | Writable | Callable[[LogRecord], None] | StrOrPath
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
        elif isinstance(sink, Callable):
            sink = CallableSink(sink)
        # else:
        #     sink = FileSink(sink)

        self._sinks.append(sink)

    def remove_sink(self, sink: AbstractSink) -> bool:
        if sink in self._sinks:
            self._sinks.remove(sink)
            return True
        return False

    def close(self) -> None:
        for sink in self._sinks:
            sink.tasks_to_complete()
