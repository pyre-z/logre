from datetime import datetime, timedelta
from multiprocessing import Value
from pathlib import Path
from typing import Callable, Iterable, TYPE_CHECKING

from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.containers import Renderables
from rich.table import Table
from rich.text import Text, TextType

from logre.const import IS_RUNNING_IN_PYCHARM, IS_WINDOWS
from logre.level import Level

if TYPE_CHECKING:
    from rich.console import ConsoleRenderable, RenderableType

__all__ = ("LogRenderConfig", "LogRender")

FormatTimeCallable = Callable[[datetime], Text]


class LogRenderConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LOG_RENDER_")

    show_time: bool = True
    show_level: bool = True
    show_level_icon: bool = IS_WINDOWS
    show_path: bool = True
    newline_time: bool = True
    time_format: str | FormatTimeCallable = "[%Y/%m/%d %X]"
    omit_times_part: bool = True
    omit_times_part_interval: float | int = 1
    level_width: int = max(map(len, Level.__members__.keys()))


LAST_LOG_TIME = Value("d", 0)
LAST_LOG_COUNT = Value("i", 0)


# noinspection D
class LogRender:
    def __init__(self, config: LogRenderConfig | None = None) -> None:
        self._config = config or LogRenderConfig()

    def __call__(
        self,
        renderables: Iterable["ConsoleRenderable"],
        log_time: datetime | None = None,
        time_format: str | FormatTimeCallable | None = None,
        level: Level | None = None,
        level_text: TextType = "",
        path: str | None = None,
        line_no: int | None = None,
        link_path: Path | str | None = None,
    ) -> list[Table]:
        linked_path = link_path is not None and not IS_RUNNING_IN_PYCHARM

        level = level or Level.NOTSET

        output_time = None
        output_main = Table.grid(padding=(0, 1), pad_edge=True)
        output_main.expand = True

        result = [output_main]

        if self._config.show_time:
            if self._config.newline_time:
                output_time = Table.grid(padding=(0, 1, 0, 1), pad_edge=True)
                output_time.add_column(style="logging.time")
                result.insert(0, output_time)
            else:
                output_main.add_column(style="logging.time")

        if self._config.show_level_icon:
            output_main.add_column(width=3)

        if self._config.show_level:
            output_main.add_column(
                style="logging.level",
                width=self._config.level_width + 1,
                justify="left",
            )

        output_main.add_column(ratio=1, style="logging.message", overflow="fold")

        if self._config.show_path and path:
            output_main.add_column(justify="right")

        row: list["RenderableType"] = []
        if self._config.show_time:
            log_time = log_time or datetime.now()
            time_format = time_format or self._config.time_format

            if callable(time_format):
                log_time_display = time_format(log_time)
            else:
                log_time_display = Text(log_time.strftime(time_format))

            time_need_omit = (
                self._config.omit_times_part
                and LAST_LOG_TIME.value
                and (
                    (log_time - datetime.fromtimestamp(LAST_LOG_TIME.value))
                    <= timedelta(seconds=self._config.omit_times_part_interval)
                )
            )
            if time_need_omit:
                log_time_display = Text(" " * len(log_time_display))

            if self._config.newline_time:
                if not time_need_omit:
                    if LAST_LOG_COUNT.value == 1:
                        output_time.add_row()
                    output_time.add_row(log_time_display)
                    LAST_LOG_COUNT.value = 0
            else:
                row.append(log_time_display)

            LAST_LOG_COUNT.value += 1
            LAST_LOG_TIME.value = log_time.timestamp()

        if self._config.show_level_icon:
            row.append(Text.from_markup(level.icon, style=level.style))

        if self._config.show_level:
            row.append(level_text)

        row.append(Renderables(renderables))
        if self._config.show_path and path:
            path_style = f"link file://{link_path}" if linked_path else ""
            if line_no:  # 如果显示行号
                if linked_path:
                    lineno_text = f"[logging.line_no][link=file://{link_path}#{line_no}]{line_no}[/link][/]"
                else:
                    lineno_text = str(line_no)

                path_table = Table.grid(pad_edge=True)
                path_table.add_column(style="logging.path", justify="right")  # 路径
                path_table.add_column()  # 分隔符
                path_table.add_column(width=4, justify="left")  # 行号

                path_table.add_row(Text(path, style=path_style), ":", lineno_text)

                row.append(path_table)
            else:  # 如果不显示行号
                row.append(Text(path, style=path_style))

        output_main.add_row(*row)
        return list(filter(bool, result))
