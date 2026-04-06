from logre.sink.console import StandardSink
from logre.console import default_console

__all__ = ("default_sink", )


default_sink = StandardSink(default_console)
