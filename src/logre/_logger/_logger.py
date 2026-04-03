import logging
import os
import warnings
from multiprocessing import RLock as Lock
from typing import ClassVar, Mapping, TYPE_CHECKING

from typing_extensions import Self

from logre._logger._base import LoggerBase
from logre.handler import Handler, default_handler
from logre.level import Level
from logre.typedefs import ArgsType, ExcInfoType

if TYPE_CHECKING:
    from multiprocessing.synchronize import RLock as LockType

__all__ = ("Logger", "logger")


class Logger(LoggerBase):
    _lock: ClassVar["LockType"] = Lock()
    _instance: ClassVar[Self | None] = None

    def __new__(cls, *args, **kwargs) -> "Logger":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    _kwargs: dict[str, ...] = {}

    def __init__(self, name: str = None, level: int | str | Level = None):
        if level is None:
            level = Level.DEBUG if os.environ.get("DEBUG") else Level.INFO
        else:
            level = Level(level)
        super().__init__(name or "arko-logger", level)
        self.handlers = [default_handler]

    def addHandler(self, *args, **kwargs) -> None: ...

    def removeHandler(self, *args, **kwargs) -> None: ...

    @property
    def handler(self) -> Handler:
        return self.handlers[0]

    def add_sink(self, *args, **kwargs) -> None:
        return self.handler.add_sink(*args, **kwargs)

    def remove_sink(self, *args, **kwargs) -> bool:
        return self.handler.remove_sink(*args, **kwargs)

    @property
    def markup(self) -> Self:
        self._kwargs["markup"] = True
        return self

    def prefix(self, prefix: str) -> Self:
        self._kwargs["prefix"] = prefix
        return self

    def config(
        self, markup: bool | None = None, prefix: str | None = None, **kwargs
    ) -> Self:
        if markup is not None:
            kwargs["markup"] = markup
        if prefix:
            kwargs["prefix"] = prefix
        self._kwargs.update(kwargs)
        return self

    def _log(
        self,
        level: int | Level,
        msg: object,
        args: ArgsType,
        exc_info: ExcInfoType | None = None,
        extra: Mapping[str, object] | None = None,
        stack_info: bool = False,
        stacklevel: int = 1,
    ) -> None:
        extra = extra or {}
        extra.update(self._kwargs)
        self._kwargs = {}
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)

    def init(self) -> None:
        """Do Nothing"""


logger = Logger()
logging.basicConfig(handlers=[default_handler])
logging.getLogger("apscheduler").setLevel(
    logging.DEBUG if os.getenv("DEBUG") else logging.INFO
)


def _show_warning(message, category, filename, lineno, file=None, line=None):
    if file is None:
        warning = warnings.WarningMessage(
            message, category, filename, lineno, file, line
        )
        logger.warning(f"{warning.category.__name__}: {warning.message}", stacklevel=2)


warnings.showwarning = _show_warning
