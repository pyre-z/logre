import linecache
import os
from pathlib import Path
from types import ModuleType, TracebackType

from pydantic_settings import BaseSettings
from pygments.style import Style as PyStyle
from pygments.token import (
    Comment,
    Keyword,
    Name,
    Number,
    Operator,
    String,
    Token,
)
from pygments.token import Text as TextToken

# noinspection PyProtectedMember
from rich._loop import loop_last
from rich.columns import Columns
from rich.console import Console, ConsoleOptions, ConsoleRenderable, RenderResult, group
from rich.constrain import Constrain
from rich.highlighter import ReprHighlighter
from rich.panel import Panel
from rich.scope import render_scope
from rich.style import Style
from rich.syntax import Syntax
from rich.text import Text
from rich.theme import Theme
from rich.traceback import (
    Frame,
    PathHighlighter,
    Stack,
    Trace,
)
from rich.traceback import Traceback as _Traceback
from typing_extensions import Iterable

from logre.const import IS_RUNNING_IN_DEBUGPY, IS_RUNNING_IN_PYCHARM

__all__ = ("Traceback", "TracebacksConfig")


class TracebacksConfig(BaseSettings):
    width: int | None = None
    code_with: int = 88
    extra_lines: int = 3
    theme: str | type[PyStyle] | None = None
    word_wrap: bool = True
    show_locals: bool = True
    indent_guides: bool = True
    suppress: Iterable[str | ModuleType] = ()
    max_frames: int | None = 20
    link_path: bool = True

    class LocalsConfig(BaseSettings):
        max_length: int = 10
        max_string: int = 80
        hide_dunder: bool = True
        hide_sunder: bool = False

    locals_config: LocalsConfig = LocalsConfig()


# noinspection D
class Traceback(_Traceback):
    def __init__(
        self, trace: Trace | None = None, *, config: TracebacksConfig | None = None
    ) -> None:
        config = config or TracebacksConfig()
        self.config = config
        super().__init__(
            trace,
            width=config.width,
            code_width=config.code_with,
            extra_lines=config.extra_lines,
            theme=config.theme,  # ty:ignore[invalid-argument-type]
            word_wrap=config.word_wrap,
            show_locals=config.show_locals,
            locals_max_length=config.locals_config.max_length,
            locals_max_string=config.locals_config.max_string,
            locals_hide_dunder=config.locals_config.hide_dunder,
            locals_hide_sunder=config.locals_config.hide_sunder,
            indent_guides=config.indent_guides,
            suppress=config.suppress,
            max_frames=config.max_frames,  # ty:ignore[invalid-argument-type]
        )

    # noinspection PyMethodOverriding
    @classmethod
    def from_exception(
        cls,
        exc_type: type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType | None,
        config: TracebacksConfig | None = None,
    ) -> "Traceback":
        config = TracebacksConfig() if config is None else config
        rich_traceback = cls.extract(
            exc_type,
            exc_value,
            traceback,
            show_locals=config.show_locals,
            locals_max_length=config.locals_config.max_length,
            locals_max_string=config.locals_config.max_string,
            locals_hide_dunder=config.locals_config.hide_dunder,
            locals_hide_sunder=config.locals_config.hide_sunder,
        )
        return cls(rich_traceback, config=config)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        theme = self.theme
        background_style = theme.get_background_style()
        token_style = theme.get_style_for_token

        traceback_theme = Theme(
            {
                "pretty": token_style(TextToken),
                "pygments.text": token_style(Token),  # NOSONAR
                "pygments.string": token_style(String),
                "pygments.function": token_style(Name.Function),  # NOSONAR
                "pygments.number": token_style(Number),  # NOSONAR
                "repr.indent": token_style(Comment) + Style(dim=True),
                "repr.str": token_style(String),
                "repr.brace": token_style(TextToken) + Style(bold=True),
                "repr.number": token_style(Number),
                "repr.bool_true": token_style(Keyword.Constant),
                "repr.bool_false": token_style(Keyword.Constant),
                "repr.none": token_style(Keyword.Constant),
                "scope.border": token_style(String.Delimiter),
                "scope.equals": token_style(Operator),
                "scope.key": token_style(Name),
                "scope.key.special": token_style(Name.Constant) + Style(dim=True),
            },
            inherit=False,
        )

        highlighter = ReprHighlighter()
        for last, stack in loop_last(reversed(self.trace.stacks)):
            if stack.frames:
                stack_renderable: ConsoleRenderable = Panel(
                    self._render_stack(stack),
                    title="[traceback.title]Traceback[/]",
                    style=background_style,
                    border_style="traceback.border",
                    expand=True,
                    padding=(0, 1),
                )
                stack_renderable = Constrain(stack_renderable, self.width)
                with console.use_theme(traceback_theme):
                    yield stack_renderable
            if stack.syntax_error is not None:
                with console.use_theme(traceback_theme):
                    yield Constrain(
                        Panel(
                            self._render_syntax_error(stack.syntax_error),
                            style=background_style,
                            border_style="traceback.border.syntax_error",
                            expand=True,
                            padding=(0, 1),
                            width=self.width,
                        ),
                        self.width,
                    )
                yield Text.assemble(
                    (f"{stack.exc_type}: ", "traceback.exc_type"),  # NOSONAR
                    highlighter(stack.syntax_error.msg),
                )
            elif stack.exc_value:
                yield Text.assemble(
                    (f"{stack.exc_type}: ", "traceback.exc_type"),
                    highlighter(stack.exc_value),
                )
            else:
                yield Text.assemble((f"{stack.exc_type}", "traceback.exc_type"))

            if not last:
                if stack.is_cause:
                    yield Text.from_markup(
                        "\n[i]The above exception was the direct cause of the following exception:\n",
                    )
                else:
                    yield Text.from_markup(
                        "\n[i]During handling of the above exception, another exception occurred:\n",
                    )

    @group()
    def _render_stack(self, stack: Stack) -> RenderResult:
        path_highlighter = PathHighlighter()
        theme = self.theme

        def read_code(filename: str) -> str:
            return "".join(linecache.getlines(filename))

        def render_locals(_frame: Frame) -> Iterable[ConsoleRenderable]:
            if _frame.locals:
                yield render_scope(
                    _frame.locals,
                    title="locals",
                    indent_guides=self.indent_guides,
                    max_length=self.locals_max_length,
                    max_string=self.locals_max_string,
                )

        exclude_frames: range | None = None
        if self.max_frames != 0:
            exclude_frames = range(
                self.max_frames // 2,
                len(stack.frames) - self.max_frames // 2,
            )

        excluded = False
        for frame_index, frame in enumerate(stack.frames):
            if exclude_frames and frame_index in exclude_frames:
                excluded = True
                continue

            if excluded:
                assert exclude_frames is not None
                yield Text(
                    f"\n... {len(exclude_frames)} frames hidden ...",
                    justify="center",
                    style="traceback.error",
                )
                excluded = False

            first = frame_index == 0
            frame_filename = frame.filename
            suppressed = any(frame_filename.startswith(path) for path in self.suppress)

            if os.path.exists(frame.filename):
                file_link = Path(frame.filename).as_uri()

                if self.config.link_path and not (
                    IS_RUNNING_IN_PYCHARM or IS_RUNNING_IN_DEBUGPY
                ):
                    filename_text = f"[link={file_link}]{frame.filename}[/link]"
                    lineno_text = (
                        f"[link={file_link}#{frame.lineno}]{frame.lineno}[/link]"
                    )
                else:
                    filename_text = frame.filename
                    lineno_text = frame.lineno

                text = Text.assemble(
                    path_highlighter(
                        Text.from_markup(f"[pygments.string]{filename_text}[/]")
                    ),
                    (":", "pygments.text"),
                    Text.from_markup(f"[pygments.number]{lineno_text}[/]"),
                    " in ",
                    (frame.name, "pygments.function"),
                    style="pygments.text",
                )
            else:
                text = Text.assemble(
                    "in ",
                    (frame.name, "pygments.function"),
                    (":", "pygments.text"),
                    (str(frame.lineno), "pygments.number"),
                    style="pygments.text",
                )
            if not frame.filename.startswith("<") and not first:
                yield ""
            yield text
            if frame.filename.startswith("<"):
                yield from render_locals(frame)
                continue
            if not suppressed:
                try:
                    code = read_code(frame.filename)
                    if not code:
                        # code may be an empty string if the file doesn't exist, OR
                        # if the traceback filename is generated dynamically
                        continue
                    lexer_name = self._guess_lexer(frame.filename, code)
                    syntax = Syntax(
                        code,
                        lexer_name,
                        theme=theme,
                        line_numbers=True,
                        line_range=(
                            frame.lineno - self.extra_lines,
                            frame.lineno + self.extra_lines,
                        ),
                        highlight_lines={frame.lineno},
                        word_wrap=self.word_wrap,
                        code_width=self.code_width,
                        indent_guides=self.indent_guides,
                        dedent=False,
                    )
                    yield ""
                except Exception as error:
                    yield Text.assemble(
                        (f"\n{error}", "traceback.error"),
                    )
                else:
                    yield (
                        Columns([syntax, *render_locals(frame)], padding=1)
                        if frame.locals
                        else syntax
                    )
