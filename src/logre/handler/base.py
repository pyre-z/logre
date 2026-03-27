import logging
from datetime import datetime
from typing import TYPE_CHECKING

from rich.highlighter import Highlighter, ReprHighlighter
from rich.text import Text

from logre.funcs import resolve_path
from logre.handler.render import LogRender
from logre.handler.traceback import Traceback
from logre.level import Level, default_level
from logre.record import LogRecord
from logre.sink import default_sink

if TYPE_CHECKING:
    from rich.console import ConsoleRenderable


__all__ = ("HandlerBase",)


class HandlerBase(logging.Handler):
    level: Level

    def setLevel(self, level: int | str | Level) -> None:
        self.level = Level[level]

    def __init__(
        self,
        level: Level | str | int = default_level,
    ) -> None:
        level = Level[level]
        logging.Handler.__init__(self, level.num)
        self.level = level

        self._sinks = [default_sink]

        self._keywords = []
        self._highlighter = ReprHighlighter()
        self._render = LogRender()

    def render_record(self, record: LogRecord) -> list["ConsoleRenderable"]:
        message = self.format(record)
        traceback = None
        if record.exc_info and record.exc_info != (None, None, None):
            exc_type, exc_value, exc_traceback = record.exc_info
            assert exc_type is not None
            assert exc_value is not None
            traceback = Traceback.from_exception(exc_type, exc_value, exc_traceback)
            if record.msg is not None:
                message = record.getMessage()
                if self.formatter:
                    record.message = record.getMessage()
                    formatter = self.formatter
                    if hasattr(formatter, "usesTime") and formatter.usesTime():
                        record.asctime = formatter.formatTime(record, formatter.datefmt)
                    message = formatter.formatMessage(record)
            else:
                message = ""

        message_renderable = self.render_message(record, message)
        return self.render(
            record=record, traceback=traceback, message_renderable=message_renderable
        )

    def emit(self, record: LogRecord) -> None:
        log_renderables = self.render_record(record)
        record.__setattr__("renderables", log_renderables)
        for sink in self._sinks:
            # noinspection PyBroadException
            try:
                sink.write(record)
            except Exception:
                self.handleError(record)

    def render_message(self, record: LogRecord, message: str) -> "ConsoleRenderable":
        use_markup: bool = getattr(record, "markup", False)
        style = record.level.style if hasattr(record, "level") else ""
        message_text = (
            Text.from_markup(message, style=style)
            if use_markup
            else Text(message, style=style)
        )
        prefix_text = Text()
        if prefix := getattr(record, "prefix", None):
            # noinspection dh
            prefix_text = (
                Text.styled("[", style="logging.prefix.brackets")
                + Text.styled(prefix, style="logging.prefix")
                + Text.styled("] ", style="logging.prefix.brackets")
            )
        message_text = prefix_text + message_text

        highlighter: "Highlighter" = getattr(record, "highlighter", self._highlighter)
        if highlighter:
            message_text = highlighter(message_text)

        if self._keywords:
            message_text.highlight_words(self._keywords, "logging.keyword")

        return message_text

    def render(
        self,
        *,
        record: LogRecord,
        traceback: Traceback | None,
        message_renderable: "ConsoleRenderable",
    ) -> list["ConsoleRenderable"]:
        path = resolve_path(record.pathname)
        level_name = record.levelname
        level_text = Text.styled(
            level_name.ljust(8), f"logging.level.{level_name.lower()}"
        )
        time_format = None if self.formatter is None else self.formatter.datefmt
        log_time = datetime.fromtimestamp(record.created)

        renderables = []
        if message_renderable:
            renderables.append(message_renderable)
        if traceback:
            renderables.append(traceback)

        log_renderable = self._render(
            renderables,
            log_time=log_time,
            time_format=time_format,
            level=record.level,
            level_text=level_text,
            path=path,
            line_no=record.lineno,
            link_path=record.pathname,
        )
        return log_renderable
