import logging
import os
import warnings
from contextvars import ContextVar
from multiprocessing import RLock as Lock
from queue import Queue
from typing import ClassVar, Mapping, TYPE_CHECKING

from typing_extensions import Self

from logre._logger._base import LoggerBase
from logre.handler import Handler, default_handler
from logre.level import Level
from logre.typedefs import ArgsType, ExcInfoType

if TYPE_CHECKING:
    from multiprocessing.synchronize import RLock as LockType

__all__ = ("Logger", "logger")

NONE = object()
EXTRA_CONTEXT_TOKEN = Queue()
EXTRA_CONTEXT = ContextVar("EXTRA_CONTEXT", default={})


class Logger(LoggerBase):
    _lock: ClassVar["LockType"] = Lock()
    _instance: ClassVar[Self | None] = None

    def __new__(cls, *args, **kwargs) -> "Logger":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

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
        kwargs = {}
        try:
            kwargs = EXTRA_CONTEXT.get()
            if not EXTRA_CONTEXT_TOKEN.empty():
                EXTRA_CONTEXT.reset(EXTRA_CONTEXT_TOKEN.get_nowait())
        except LookupError:
            pass
        kwargs["markup"] = True
        EXTRA_CONTEXT_TOKEN.put(EXTRA_CONTEXT.set(kwargs))
        return self

    def config(self, markup: bool | None = NONE, **kwargs) -> Self:
        if markup is not None:
            kwargs["markup"] = markup
        EXTRA_CONTEXT_TOKEN.put(EXTRA_CONTEXT.set(kwargs))
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
        extra.update(EXTRA_CONTEXT.get())
        if not EXTRA_CONTEXT_TOKEN.empty():
            EXTRA_CONTEXT.reset(EXTRA_CONTEXT_TOKEN.get_nowait())
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
        s = warnings.formatwarning(message, category, filename, lineno, line)
        logger.warning(str(s), stacklevel=2)


warnings.showwarning = _show_warning
