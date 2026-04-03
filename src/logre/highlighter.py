from threading import RLock as Lock

from rich.highlighter import Highlighter, ISO8601Highlighter, ReprHighlighter
from rich.text import Text

try:
    import regex as re
except ImportError:
    import re

__all__ = ("EmailHighlighter", "CombinedHighlighter", "default_highlighter")


class EmailHighlighter(ReprHighlighter):
    base_style = "email."
    highlights = [
        r"(?P<addr>[\w-]+)(?P<symbol>@)(?P<domain>[\w.-]+\.\w+)",
    ]


class ShortcutHighlighter(Highlighter):
    """高亮快捷键，如 CTRL+K、CTRL+ALT+C、SHIFT+TAB 等"""

    # 类属性：修饰键（保持大写）
    MODIFIER_KEYS = frozenset(["CTRL", "SHIFT", "ALT", "META", "WIN", "CMD"])

    # 类属性：功能键（保持大写）
    FUNCTION_KEYS = frozenset(
        [
            "TAB",
            "ENTER",
            "ESC",
            "BACKSPACE",
            "DELETE",
            "HOME",
            "END",
            "PGUP",
            "PGDN",
            "INSERT",
            "UP",
            "DOWN",
            "LEFT",
            "RIGHT",
            "SPACE",
            "F1",
            "F2",
            "F3",
            "F4",
            "F5",
            "F6",
            "F7",
            "F8",
            "F9",
            "F10",
            "F11",
            "F12",
        ]
    )

    # 预编译正则：一次性匹配整个快捷键
    # 格式：修饰键(CTRL|SHIFT|ALT...)+(+修饰键)*+普通键
    _SHORTCUT_RE = re.compile(
        rf"""
        (?P<shortcut>
            (?P<modifier1>{'|'.join(MODIFIER_KEYS)}) \+ 
            (?:(?P<modifier2>{'|'.join(MODIFIER_KEYS)}) \+)?
            (?:(?P<modifier3>{'|'.join(MODIFIER_KEYS)}) \+)?
            (?P<key>{'|'.join(FUNCTION_KEYS)}|[A-Z0-9])
        )
        """,
        re.VERBOSE | re.IGNORECASE,
    )

    def highlight(self, text: Text) -> None:
        """高亮文本中的快捷键"""
        for match in self._SHORTCUT_RE.finditer(text.plain):
            # 获取整个匹配的位置
            start, end = match.span("shortcut")

            # 为整个快捷键添加基础样式
            text.stylize("shortcut.modifier", start, end)

            # 为修饰键添加特殊样式
            for group in ["modifier1", "modifier2", "modifier3"]:
                if match.group(group):
                    m_start, m_end = match.span(group)
                    text.stylize("shortcut.plus", m_start, m_end)

            # 为最终按键添加样式
            key_start, key_end = match.span("key")
            text.stylize("shortcut.function", key_start, key_end)


class CombinedHighlighter(Highlighter):
    _lock = Lock()

    _highlighters: list[Highlighter] = [
        ReprHighlighter(),
        EmailHighlighter(),
        ShortcutHighlighter(),
        ISO8601Highlighter(),
    ]

    @property
    def highlighters(self) -> list[Highlighter]:
        return list(self._highlighters)

    def add_highlighter(self, highlighter: Highlighter) -> None:
        if highlighter not in self._highlighters:
            with self._lock:
                if highlighter not in self._highlighters:
                    self._highlighters.append(highlighter)

    def remove_highlighter(self, highlighter: Highlighter) -> None:
        if highlighter in self._highlighters:
            with self._lock:
                if highlighter in self._highlighters:
                    self._highlighters.remove(highlighter)

    def highlight(self, text: Text) -> None:
        with self._lock:
            for highlighter in self._highlighters:
                highlighter.highlight(text)


default_highlighter = CombinedHighlighter()
