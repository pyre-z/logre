import logging
from enum import IntEnum
from threading import RLock

from rich.style import Style

from logre.style.monokai_pro import (
    DARK_GREY,
    GREEN,
    GREY,
    LIGHT_GREY,
    RED,
    WHITE,
    YELLOW,
)

__all__ = ("LogreLevel", "default_level")

logging.addLevelName(5, "TRACE")
logging.addLevelName(25, "SUCCESS")

LOCK: RLock = RLock()


class LogreLevel(IntEnum):
    NOTSET = 0
    TRACE = 5
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    WARN = WARNING
    ERROR = 40
    CRITICAL = 50
    FATAL = CRITICAL

    @property
    def icon(self) -> str:
        return LEVEL_MAP.get(self, ("", ""))[0]

    @icon.setter
    def icon(self, icon: str) -> None:
        if self not in LEVEL_MAP:
            with LOCK:
                if self not in LEVEL_MAP:
                    LEVEL_MAP[self] = (icon, Style.null())
        LEVEL_MAP[self] = (icon, LEVEL_MAP[self][1])

    @property
    def style(self) -> Style:
        return LEVEL_MAP.get(self, ("", Style.null()))[1]

    @style.setter
    def style(self, style: Style) -> None:
        if self not in LEVEL_MAP:
            with LOCK:
                if self not in LEVEL_MAP:
                    LEVEL_MAP[self] = ("", style)
        LEVEL_MAP[self] = (LEVEL_MAP[self][0], style)


LEVEL_MAP: dict[LogreLevel, tuple[str, Style]] = {
    LogreLevel.NOTSET: ("", Style(color=DARK_GREY, dim=True)),
    LogreLevel.TRACE: (":pencil2:", Style(color=GREY)),
    LogreLevel.DEBUG: (":bug:", Style(color=LIGHT_GREY, bold=True)),
    LogreLevel.INFO: (":information:", Style(color=WHITE)),
    LogreLevel.SUCCESS: (":white_heavy_check_mark:", Style(color=GREEN)),
    LogreLevel.WARNING: (":rotating_light:", Style(color=YELLOW)),
    LogreLevel.WARN: (":rotating_light:", Style(color=YELLOW)),
    LogreLevel.ERROR: (":cross_mark:", Style(color=RED)),
    LogreLevel.CRITICAL: (":pill:", Style(color=RED, bold=True, blink2=True)),
    LogreLevel.FATAL: (":pill:", Style(color=RED, bold=True, blink2=True)),
}

default_level = LogreLevel.NOTSET
