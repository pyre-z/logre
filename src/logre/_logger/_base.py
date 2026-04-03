import inspect
import logging
import os
import sys
import traceback
from functools import lru_cache
from io import StringIO
from pathlib import Path
from types import FrameType
from typing import Mapping

from typing_extensions import Self

from logre.level import Level
from logre.record import LogRecord
from logre.typedefs import ArgsType, ExcInfoType, SysExcInfoType

if sys.version_info >= (3, 14):
    import _py_warnings

    _showwarnmsg = _py_warnings._showwarnmsg
else:
    import warnings

    _showwarnmsg = warnings._showwarnmsg

__all__ = ("LoggerBase",)


@lru_cache
def _is_internal_file(path: Path) -> bool:
    if path in set(map(Path, [__file__, logging.addLevelName.__code__.co_filename])):
        return True
    if "importlib" in str(path) and "_bootstrap" in str(path):
        return True
    if (
        Path(
            os.path.commonprefix(
                [path, parent := Path(__file__).joinpath("../../").resolve()]
            )
        )
        == parent
    ):
        return True
    return False


def _is_internal_frame(frame: FrameType) -> bool:
    # noinspection PyProtectedMember
    if (
        frame.f_code.co_filename == _showwarnmsg.__code__.co_filename
        and frame.f_code.co_firstlineno == _showwarnmsg.__code__.co_firstlineno
    ):
        return True
    filename = os.path.normcase(frame.f_code.co_filename)
    return _is_internal_file(Path(filename).resolve())


_srcfile = os.path.normcase(_is_internal_frame.__code__.co_filename)

_UNKNOWN_FUNCTION = "(unknown function)"
_UNKNOWN_FILE = "(unknown file)"

logging.addLevelName(5, "TRACE")
logging.addLevelName(25, "SUCCESS")


class LoggerBase(logging.Logger):
    level: Level

    # noinspection PyTypeChecker
    def __init__(self, name: str, level: Level | int | str = Level.NOTSET) -> None:
        level: Level = Level[level]
        super().__init__(name, level.num)
        self.level = level

    def makeRecord(
        self,
        name: str,
        level: int | Level,
        fn: str,
        lno: int,
        msg: object,
        args: ArgsType,
        exc_info: SysExcInfoType | None,
        func: str | None = None,
        extra: Mapping[str, object] | None = None,
        sinfo: str | None = None,
    ) -> LogRecord:
        # noinspection PyTypeChecker
        return super().makeRecord(
            name, level, fn, lno, msg, args, exc_info, func, extra, sinfo
        )

    def findCaller(
        self, stack_info: bool = False, stacklevel: int = 1
    ) -> tuple[str, int, str, str | None]:
        current_frame = inspect.currentframe()
        if not current_frame:
            return _UNKNOWN_FILE, 0, _UNKNOWN_FUNCTION, None
        f = current_frame
        while stacklevel > 0:
            next_f = f.f_back
            if next_f is None:
                break
            f = next_f
            if not _is_internal_frame(f):
                stacklevel -= 1
        co = f.f_code
        sinfo = None
        if stack_info:
            with StringIO() as sio:
                sio.write("Stack (most recent call last):\n")
                traceback.print_stack(f, file=sio)
                # noinspection PyUnresolvedReferences
                sinfo = sio.getvalue()
                if sinfo[-1] == "\n":
                    sinfo = sinfo[:-1]
        return co.co_filename, f.f_lineno, co.co_name, sinfo

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
        sinfo = None
        if _srcfile:
            try:
                fn, lno, func, sinfo = self.findCaller(stack_info, stacklevel)
            except ValueError:
                fn, lno, func = _UNKNOWN_FILE, 0, _UNKNOWN_FUNCTION
        else:  # pragma: no cover
            fn, lno, func = _UNKNOWN_FILE, 0, _UNKNOWN_FUNCTION
        if exc_info:
            if isinstance(exc_info, BaseException):
                exc_info = (type(exc_info), exc_info, exc_info.__traceback__)
            elif not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()
        # noinspection PyTypeChecker
        record = self.makeRecord(
            self.name, level, fn, lno, msg, args, exc_info, func, extra, sinfo
        )
        self.handle(record)

    def isEnabledFor(self, level: int | Level) -> bool:
        """
        Is this logger enabled for level 'level'?
        """
        return super().isEnabledFor(level if isinstance(level, int) else level.num)

    def trace(
        self,
        msg: object,
        *args: object,
        exc_info: ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        return self._log(
            Level.TRACE,
            msg,
            args,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=stacklevel,
        )

    def debug(
        self,
        msg: object,
        *args: object,
        exc_info: ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        return self._log(
            Level.DEBUG,
            msg,
            args,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=stacklevel,
        )

    def info(
        self,
        msg: object,
        *args: object,
        exc_info: ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        return self._log(
            Level.INFO,
            msg,
            args,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=stacklevel,
        )

    def warning(
        self,
        msg: object,
        *args: object,
        exc_info: ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        return self._log(
            Level.WARNING,
            msg,
            args,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=stacklevel,
        )

    def warn(
        self,
        msg: object,
        *args: object,
        exc_info: ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        warnings.warn(
            "The 'warn' method is deprecated, use 'warning' instead",
            DeprecationWarning,
            2,
        )
        return self._log(
            Level.WARN,
            msg,
            args,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=stacklevel,
        )

    def error(
        self,
        msg: object,
        *args: object,
        exc_info: ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        if self.isEnabledFor(Level.ERROR):
            return self._log(
                Level.ERROR,
                msg,
                args,
                exc_info=exc_info,
                extra=extra,
                stack_info=stack_info,
                stacklevel=stacklevel,
            )
        return None

    def exception(
        self,
        msg: object = None,
        *args: object,
        exc_info: ExcInfoType = True,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        return self._log(
            Level.ERROR,
            msg,
            args,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=stacklevel,
        )

    def critical(
        self,
        msg: object,
        *args: object,
        exc_info: ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        return self._log(
            Level.CRITICAL,
            msg,
            args,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=stacklevel,
        )

    def log(
        self,
        level: int | Level,
        msg: object,
        *args: object,
        exc_info: ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        return self._log(
            level,
            msg,
            args,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=stacklevel,
        )

    def success(
        self,
        msg: object,
        *args: object,
        exc_info: ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        return self._log(
            Level.SUCCESS,
            msg,
            args,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=stacklevel,
        )

    def getChild(self, suffix) -> Self:
        return self
