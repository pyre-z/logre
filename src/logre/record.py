from typing import Self
import logging

from rich.highlighter import Highlighter

from logre.level import LogreLevel
from logre.typedefs import ArgsType, SysExcInfoType

__all__ = ("LogreRecord",)


class LogreRecord(logging.LogRecord):
    level: LogreLevel

    markup: bool | None = None
    highlighter: Highlighter | None = None

    @classmethod
    def from_record(cls, record: logging.LogRecord) -> Self:
        return cls(
            name=record.name,
            level=record.levelno,
            pathname=record.pathname,
            lineno=record.lineno,
            msg=record.msg,
            args=record.args,
            exc_info=record.exc_info,
            func=record.funcName,
            sinfo=record.stack_info,
        )

    def __init__(
        self,
        name: str,
        level: int | LogreLevel,
        pathname: str,
        lineno: int,
        msg: object,
        args: ArgsType | None,
        exc_info: SysExcInfoType | None,
        func: str | None = None,
        sinfo: str | None = None,
        # extra
        markup: bool | None = None,
        highlighter: Highlighter | None = None,
    ) -> None:
        self.level = LogreLevel(level) if isinstance(level, int) else level
        super().__init__(
            name, self.level, pathname, lineno, msg, args, exc_info, func, sinfo
        )
        self.markup = markup
        self.highlighter = highlighter


logging.setLogRecordFactory(LogreRecord)
