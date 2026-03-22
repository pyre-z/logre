# noinspection PyProtectedMember
from os import PathLike
from types import TracebackType
from typing import Literal, Mapping, TypeAlias, Union

from typing_extensions import Protocol

__all__ = (
    "StrOrPath",
    "SysExcInfoType",
    "ExcInfoType",
    "Writable",
    "ArgsType",
    "FormatStyle",
)

StrOrPath = Union[PathLike, str]

SysExcInfoType: TypeAlias = (
        tuple[type[BaseException], BaseException, TracebackType | None]
        | tuple[None, None, None]
)
ExcInfoType: TypeAlias = None | bool | SysExcInfoType | BaseException
ArgsType: TypeAlias = tuple[object, ...] | Mapping[str, object]
FormatStyle: TypeAlias = Literal["%", "{", "$"]


class Writable(Protocol):
    def write(self, content: str) -> None: ...
