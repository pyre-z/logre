from logre.console import LogreConsole, default_console
from logre.record import LogreRecord
from logre.sink.abc import AbstractSink

__all__ = ("StandardSink",)


class StandardSink(AbstractSink):
    _console: LogreConsole

    @property
    def console(self) -> LogreConsole:
        return self._console

    def __init__(self, console: LogreConsole | None = None) -> None:
        self._console = console or default_console

    def write(self, record: LogreRecord) -> None:
        self.console.print(*record.__getattribute__("renderables"))

    def stop(self) -> None:
        self.console.quiet = True
