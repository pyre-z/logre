from typing import Mapping

from pydantic import BaseModel
from typing_extensions import Self

from logre._logger._base import LoggerBase
from logre.level import LogreLevel
from logre.typedefs import ArgsType, ExcInfoType

__all__ = ("Logger", "logger")

class _LoggerConfig(BaseModel):
    markup: bool | None = False
    prefix: str | None = None

class _LogreLogger(LoggerBase):
    _config: _LoggerConfig

    def __init__(
        self,
        name: str | None = None,
        level: int | str | LogreLevel | None = None,
        *,
        config: _LoggerConfig | None = None,
    ) -> None: ...
    def _log(
        self,
        level: int | LogreLevel,
        msg: object,
        args: ArgsType,
        exc_info: ExcInfoType | None = None,
        extra: Mapping[str, object] | None = None,
        stack_info: bool = False,
        stacklevel: int = 1,
    ) -> None: ...

_UN_SET = object()

class Logger:
    _core: _LogreLogger

    def __init__(
        self,
        markup: bool | None = _UN_SET,
        prefix: str | None = _UN_SET,
        *,
        config: _LoggerConfig | None = None,
    ) -> None: ...
    def trace(
        self,
        msg: object,
        *args: object,
        exc_info: ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None: ...
    def debug(
        self,
        msg: object,
        *args: object,
        exc_info: ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None: ...
    def info(
        self,
        msg: object,
        *args: object,
        exc_info: ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None: ...
    def success(
        self,
        msg: object,
        *args: object,
        exc_info: ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None: ...
    def warning(
        self,
        msg: object,
        *args: object,
        exc_info: ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None: ...
    def warn(
        self,
        msg: object,
        *args: object,
        exc_info: ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None: ...
    def error(
        self,
        msg: object,
        *args: object,
        exc_info: ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None: ...
    def exception(
        self,
        msg: object,
        *args: object,
        exc_info: ExcInfoType = True,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None: ...
    def critical(
        self,
        msg: object,
        *args: object,
        exc_info: ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None: ...
    def fatal(
        self,
        msg: object,
        *args: object,
        exc_info: ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None: ...
    def log(
        self,
        level: int,
        msg: object,
        *args: object,
        exc_info: ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None: ...
    @property
    def markup(self) -> Self: ...
    def prefix(self, prefix: str | None = None) -> Self: ...

logger: Logger
