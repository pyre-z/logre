import logging
import os
import warnings
from multiprocessing import RLock as Lock
from typing import TYPE_CHECKING, ClassVar, Mapping

from pydantic import BaseModel
from typing_extensions import Self

from logre._logger._base import LoggerBase
from logre.const import PROJECT_ROOT
from logre.handler import default_handler
from logre.level import LogreLevel, default_level
from logre.typedefs import ArgsType, ExcInfoType

if TYPE_CHECKING:
    from multiprocessing.synchronize import RLock as LockType

__all__ = ("Logger", "logger")


class _LoggerConfig(BaseModel):
    markup: bool | None = False
    prefix: str | None = None


class _Logger(LoggerBase):
    _lock: ClassVar["LockType"] = Lock()
    _instance: ClassVar[Self | None] = None

    def __new__(cls, *args, **kwargs) -> Self:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, name=None, level=None, *, config=None) -> None:
        self._config = config or _LoggerConfig()
        if level is None:
            level = LogreLevel.DEBUG if os.environ.get("DEBUG") else default_level
        else:
            level = LogreLevel(level if isinstance(level, int) else default_level)
        super().__init__(name or PROJECT_ROOT.name or "logre", level)
        self.addHandler(default_handler)

    def _log(
        self,
        level: int | LogreLevel,
        msg: object,
        args: ArgsType,
        exc_info: ExcInfoType | None = None,
        extra: Mapping[str, object] | None = None,
        stack_info: bool = False,
        stacklevel: int = 1,
    ) -> None:
        extra = self._config.model_dump() | dict(extra or {})
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)


class Logger:
    def __init__(self, *, _logger=None) -> None:
        self._core = _logger or _Logger()

    def trace(self, *args, **kwargs):
        return self.log(LogreLevel.TRACE, *args, **kwargs)

    def debug(self, *args, **kwargs):
        return self.log(LogreLevel.DEBUG, *args, **kwargs)

    def info(self, *args, **kwargs):
        return self.log(LogreLevel.INFO, *args, **kwargs)

    def success(self, *args, **kwargs):
        return self.log(LogreLevel.SUCCESS, *args, **kwargs)

    def warning(self, *args, **kwargs):
        return self.log(LogreLevel.WARNING, *args, **kwargs)

    def warn(self, *args, **kwargs):
        return self.log(LogreLevel.WARN, *args, **kwargs)

    def error(self, *args, **kwargs):
        return self.log(LogreLevel.ERROR, *args, **kwargs)

    def exception(self, *args, exc_info=True, **kwargs) -> None:
        return self.log(LogreLevel.ERROR, *args, exc_info=exc_info, **kwargs)

    def critical(self, *args, **kwargs):
        return self.log(LogreLevel.CRITICAL, *args, **kwargs)

    def fatal(self, *args, **kwargs):
        return self.log(LogreLevel.FATAL, *args, **kwargs)

    def log(self, *args, **kwargs):
        return self._core.log(*args, **kwargs)

    @property
    def markup(self):
        config = self._core._config
        config.markup = True
        return Logger(_logger=_Logger(config=config))

    def prefix(self, prefix=None):
        config = self._core._config
        config.prefix = prefix
        return Logger(_logger=_Logger(config=config))


logging.basicConfig(handlers=[default_handler])
logging.getLogger("apscheduler").setLevel(
    logging.DEBUG if os.getenv("DEBUG") else logging.INFO
)
logger = Logger()


def _show_warning(message, category, filename, lineno, file=None, line=None):
    if file is None:
        warning = warnings.WarningMessage(
            message, category, filename, lineno, file, line
        )
        logger.warning(f"{warning.category.__name__}: {warning.message}", stacklevel=2)


warnings.showwarning = _show_warning  # ty:ignore[invalid-assignment]
