from logre.record import LogRecord
from logre.sink.abc import AbstractSink
from logre.console import Console, default_console

__all__ = ("StandardSink", )


class StandardSink(AbstractSink):
    _console: Console

    @property
    def console(self) -> Console:
        return self._console

    def __init__(self, console: Console | None = None, **kwargs) -> None:
        if console is None:
            if kwargs:
                console = Console(**kwargs)
            else:
                console = default_console()
        self._console = console

    def write(self, record: LogRecord) -> None:
        self.console.print(*record.__getattribute__("renderables"))

    def stop(self) -> None:
        self.console.quiet = True
