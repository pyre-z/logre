from typing import Callable

from logre.record import LogRecord
from logre.sink.abc import AbstractSink

__all__ = ("CallableSink", )


class CallableSink(AbstractSink):
    def __init__(self, function: Callable[[LogRecord], None]) -> None:
        self._function = function

    def write(self, record: LogRecord) -> None:
        self._function(record)

