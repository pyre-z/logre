import logging
import os
import warnings

from pydantic import BaseModel

from logre._logger._base import LoggerBase
from logre.const import PROJECT_ROOT
from logre.handler import default_handler
from logre.level import LogreLevel, default_level

__all__ = ("Logger", "logger")


class _LoggerConfig(BaseModel):
    markup: bool | None = False
    prefix: str | None = None


class _LogreLogger(LoggerBase):
    def __init__(self, name=None, level=None, *, config=None) -> None:
        self._config = config or _LoggerConfig()
        if level is None:
            level = LogreLevel.DEBUG if os.environ.get("DEBUG") else default_level
        else:
            level = LogreLevel(level if isinstance(level, int) else default_level)
        super().__init__(name or PROJECT_ROOT.name or "logre", level)

    def _log(
        self,
        level,
        msg,
        args,
        exc_info=None,
        extra=None,
        stack_info=False,
        stacklevel=1,
    ):
        extra = {
            k: v for k, v in self._config.model_dump().items() if v is not None
        } | dict(extra or {})
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)


_UN_SET = object()


class Logger:
    def __init__(
        self, markup=_UN_SET, prefix=_UN_SET, *, config: _LoggerConfig | None = None
    ) -> None:
        config = (config or _LoggerConfig()).model_copy(
            update={
                k: v
                for k, v in {"markup": markup, "prefix": prefix}.items()
                if v is not _UN_SET
            }
        )
        self._core = _LogreLogger(config=config)
        self._core.addHandler(default_handler)

    def trace(self, *args, **kwargs):
        self.log(LogreLevel.TRACE, *args, **kwargs)

    def debug(self, *args, **kwargs):
        self.log(LogreLevel.DEBUG, *args, **kwargs)

    def info(self, *args, **kwargs):
        self.log(LogreLevel.INFO, *args, **kwargs)

    def success(self, *args, **kwargs):
        self.log(LogreLevel.SUCCESS, *args, **kwargs)

    def warning(self, *args, **kwargs):
        self.log(LogreLevel.WARNING, *args, **kwargs)

    def warn(self, *args, **kwargs):
        self.log(LogreLevel.WARN, *args, **kwargs)

    def error(self, *args, **kwargs):
        self.log(LogreLevel.ERROR, *args, **kwargs)

    def exception(self, *args, exc_info=True, **kwargs) -> None:
        self.log(LogreLevel.ERROR, *args, exc_info=exc_info, **kwargs)

    def critical(self, *args, **kwargs):
        self.log(LogreLevel.CRITICAL, *args, **kwargs)

    def fatal(self, *args, **kwargs):
        self.log(LogreLevel.FATAL, *args, **kwargs)

    def log(self, *args, **kwargs):
        self._core.log(*args, **kwargs)

    @property
    def markup(self):
        return Logger(
            **self._core._config.model_copy(update={"markup": True}).model_dump()
        )

    def prefix(self, prefix=None):
        return Logger(
            **self._core._config.model_copy(update={"prefix": prefix}).model_dump()
        )


logging.basicConfig(handlers=[default_handler])
logging.setLoggerClass(_LogreLogger)
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
