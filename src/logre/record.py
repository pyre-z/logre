import logging

from rich.highlighter import Highlighter

from logre.level import Level
from logre.typedefs import ArgsType, SysExcInfoType

__all__ = ("LogRecord",)


class LogRecord(logging.LogRecord):
    level: Level

    markup: bool | None = None
    highlighter: Highlighter | None = None

    def __init__(
        self,
        name: str,
        level: int | Level,
        pathname: str,
        lineno: int,
        msg: object,
        args: ArgsType | None,
        exc_info: SysExcInfoType | None,
        func: str | None = None,
        sinfo: str | None = None,
    ) -> None:
        level = Level[level]
        super().__init__(
            name, level.num, pathname, lineno, msg, args, exc_info, func, sinfo
        )
        self.level = level
        self.levelname = level.name


logging.setLogRecordFactory(LogRecord)
