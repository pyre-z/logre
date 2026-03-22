from rich.theme import Theme

from logre.style.code import HikariCodeStyle
from logre.style.const import *
from logre.style.styles import HIKARI_STYLES

__all__ = (
    # theme
    "HikariTheme",
    # code
    "HikariCodeStyle",
    # style
    "HIKARI_STYLES",
    # const
    "BACKGROUND",
    "FOREGROUND",
    "BLACK",
    "GREY",
    "LIGHT_GREY",
    "DARK_GREY",
    "RED",
    "BRIGHT_RED",
    "MAGENTA",
    "BRIGHT_MAGENTA",
    "GREEN",
    "BRIGHT_GREEN",
    "YELLOW",
    "BRIGHT_YELLOW",
    "ORANGE",
    "PURPLE",
    "BLUE",
    "BRIGHT_BLUE",
    "CYAN",
    "BRIGHT_CYAN",
    "WHITE",
    "BRIGHT_WHITE",
)

HikariTheme = Theme(HIKARI_STYLES)
