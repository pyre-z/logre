from logging import LogRecord
from typing import Callable

__all__ = ("CallableSinkCallable",)


CallableSinkCallable = Callable[[LogRecord], None]
