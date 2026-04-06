from abc import ABC, abstractmethod

from logre.record import LogreRecord

__all__ = ("AbstractSink",)


class AbstractSink(ABC):
    @abstractmethod
    def write(self, record: LogreRecord) -> None: ...

    def stop(self) -> None:
        return

    def tasks_to_complete(self) -> None:
        return
