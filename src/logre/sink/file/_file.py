from logre.record import LogreRecord
from logre.sink.abc import AbstractSink


class FileSink(AbstractSink):
    def write(self, record: LogreRecord) -> None:
        pass
