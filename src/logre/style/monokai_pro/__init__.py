from rich.theme import Theme

from logre.style.monokai_pro.code import MonokaiProCodeStyle
from logre.style.monokai_pro.const import *  # noqa: F403
from logre.style.monokai_pro.styles import MonokaiProStyles

__all__ = (  # noqa: F405
    # theme
    "MonokaiProTheme",
    # code
    "MonokaiProCodeStyle",
    # style
    "MonokaiProStyles",
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

MonokaiProTheme = Theme(MonokaiProStyles)
