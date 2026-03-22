from logre.record import LogRecord
from logre.sink.abc import AbstractSink


class FileSink(AbstractSink):
    def write(self, record: LogRecord) -> None:
        pass
