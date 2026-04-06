from typing import Callable

from logre.record import LogreRecord
from logre.sink.abc import AbstractSink

__all__ = ("CallableSink", )


class CallableSink(AbstractSink):
    def __init__(self, function: Callable[[LogreRecord], None]) -> None:
        self._function = function

    def write(self, record: LogreRecord) -> None:
        self._function(record)

