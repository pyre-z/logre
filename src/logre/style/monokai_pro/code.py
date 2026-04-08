# ruff: noqa: F405
from pygments.style import Style as PyStyle
from pygments.token import (
    Comment,
    Error,
    Generic,
    Keyword,
    Literal,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Text,
)

from logre.style.monokai_pro.const import *  # noqa: F403

__all__ = ("MonokaiProCodeStyle",)


class MonokaiProCodeStyle(PyStyle):
    name = "Monokai Pro"
    background_color = BACKGROUND_COLOR
    highlight_color = HIGHLIGHT_COLOR

    styles = {
        Text: WHITE,  # class:  ''
        Error: "#fc618d bg:#1e0010",  # class: 'err'
        Comment: LIGHT_GREY,  # class: 'c'
        Comment.Multiline: YELLOW,  # class: 'cm'
        Keyword: RED,  # class: 'k'
        Keyword.Namespace: GREEN,  # class: 'kn'
        Operator: RED,  # class: 'o'
        Punctuation: WHITE,  # class: 'p'
        Name: WHITE,  # class: 'n'
        Name.Attribute: GREEN,  # class: 'na' - to be revised
        Name.Builtin: CYAN,  # class: 'nb'
        Name.Builtin.Pseudo: ORANGE,  # class: 'bp'
        Name.Class: GREEN,  # class: 'nc' - to be revised
        Name.Decorator: PURPLE,  # class: 'nd' - to be revised
        Name.Exception: GREEN,  # class: 'ne'
        Name.Function: GREEN,  # class: 'nf'
        Name.Property: ORANGE,  # class: 'py'
        Number: PURPLE,  # class: 'm'
        Literal: PURPLE,  # class: 'logging'
        Literal.Date: ORANGE,  # class: 'ld'
        String: YELLOW,  # class: 's'
        String.Regex: ORANGE,  # class: 'sr'
        Generic.Deleted: YELLOW,  # class: 'gd',
        Generic.Emph: "italic",  # class: 'ge'
        Generic.Inserted: GREEN,  # class: 'gi'
        Generic.Strong: "bold",  # class: 'gs'
        Generic.Subheading: LIGHT_GREY,  # class: 'gu'
    }
