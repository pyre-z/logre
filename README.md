<div align="center">

# logre

一个融合了 [Loguru](https://github.com/Delgan/loguru) 的强大日志管理功能和 [Rich](https://github.com/Textualize/rich)
的华丽终端渲染的 Python 日志库。

</div>

> ⚠️ 注意：本项目还在开发中，不能保证正确运行

## ✨ 特性

- **🎨 华丽终端输出** - 基于 Rich 渲染，默认内置优雅的 Monokai Pro 主题
- **🔍 自动语法高亮** - 自动高亮邮件地址、快捷键、URL、日期等
- **🎯 Icon 化日志级别** - 每个日志级别都配有 Emoji 图标，一目了然
- **⏰ 智能时间格式化** - 自动省略重复的时间戳，让日志输出更干净
- **🔧 高度可定制** - 可配置显示选项，修改图标样式，添加自定义高亮器等
- **💫 美观的异常栈** - 由 Rich 渲染的增强版异常追溯栈，便于调试
- **🏷️ 前缀支持** - 可为日志记录器实例添加自定义前缀用于组件标识
- **📂 灵活输出目标** - 支持标准输出、可调用对象、文件轮转压缩（Loguru 风格）
- **⚙️ Pydantic 配置** - 通过环境变量配置，开箱即用
- **🔌 基于标准库** - 与 Python 标准日志生态集成
- **🤖 智能终端检测** - 自动检测终端能力选择最优渲染方式

## 📋 要求

- Python 3.13 或更高版本

## 📦 安装

```bash
# 使用 pip
pip install logre

# 使用 uv
uv add logre
```

### 从源码安装

```bash
git clone <repository-url>
cd logre
uv install
```

## 🚀 快速开始

```python
from logre import logger

# 不同级别的日志
logger.trace("Trace message")
logger.debug("Debug message")
logger.info("Information message")
logger.success("Success message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")

# 带自定义前缀
logger.prefix("MYAPP").info("Application started")

# 启用 Rich Markup
logger.markup.info("[blue]This is [bold blue]bold blue[/bold blue] text[/]")

# 记录异常
try:
    1 / 0
except Exception as e:
    logger.exception(e)
```

## 📖 详细使用

### 创建自定义日志记录器

```python
from logre._logger import Logger

# 创建启用 markup 的自定义日志记录器
logger = Logger(markup=True)

# 创建带前缀的日志记录器
logger = Logger(prefix="MYAPP")
```

### 日志级别

logre 默认提供以下日志级别：

| 级别         | 数值 | Icon | 说明   |
|------------|----|------|------|
| `NOTSET`   | 0  | -    | 未设置  |
| `TRACE`    | 5  | ✏️   | 详细追踪 |
| `DEBUG`    | 10 | 🐛   | 调试信息 |
| `INFO`     | 20 | ℹ️   | 一般信息 |
| `SUCCESS`  | 25 | ✅    | 成功消息 |
| `WARNING`  | 30 | 🚨   | 警告   |
| `ERROR`    | 40 | ❌    | 错误   |
| `CRITICAL` | 50 | 💊   | 严重错误 |

你可以自定义每个级别的图标和样式：

```python
from logre.level import LogreLevel
from rich.style import Style

# 修改图标
LogreLevel.INFO.icon = "ℹ️"

# 修改样式
LogreLevel.INFO.style = Style(color="blue", bold=True)
```

### 配置

输出渲染配置可以通过环境变量（前缀 `LOG_RENDER_`）或代码配置：

```python
from logre.handler.render import LogRenderConfig

config = LogRenderConfig(
    show_time=True,  # 显示时间戳
    show_level=True,  # 显示日志级别名称
    show_level_icon=True,  # 显示图标（Windows 默认为 True）
    show_path=True,  # 显示源文件和行号
    newline_time=True,  # 时间戳单独一行
    time_format="[%Y/%m/%d %X]",  # 时间格式
    omit_times_part=True,  # 在间隔内省略重复时间戳
    omit_times_part_interval=1,  # 间隔（秒）
    level_width=8,  # 级别名称列宽度
)
```

### 高亮特性

logre 自动高亮：

- **邮件** - `user@example.com` 自动高亮
- **快捷键** - `CTRL+K`, `CTRL+ALT+C` 对修饰键和按键分别高亮
- **URL** - 超链接高亮
- **日期** - ISO8601 时间戳高亮

你也可以添加自定义高亮器：

```python
from logre.highlighter import default_highlighter
from rich.highlighter import Highlighter


class MyHighlighter(Highlighter):
    def highlight(self, text):
        # 自定义高亮逻辑
        pass


default_highlighter.add_highlighter(MyHighlighter())
```

## 🛠️ 项目结构

```
src/logre/
├── _logger/           # 核心日志实现
├── config/            # 配置管理
├── handler/           # 日志处理器
│   ├── _base.py       # 基础处理器
│   ├── _handler.py    # 支持多个输出 sink 的主处理器
│   ├── render.py      # 日志渲染配置
│   └── traceback.py   # 增强的异常追溯栈渲染
├── sink/              # 输出目标
│   ├── abc.py         # 抽象基类
│   ├── standard.py    # 标准输出
│   ├── callable.py    # 可调用对象输出
│   └── file/          # 文件轮转压缩输出
├── render/            # 渲染组件
├── style/             # 主题和样式
│   └── monokai_pro/   # 默认 Monokai Pro 主题
├── console.py         # 扩展 Rich Console，自动终端检测
├── level.py           # 日志级别定义
├── filter.py          # 日志过滤
├── highlighter.py     # 语法高亮
├── record.py          # 日志记录扩展
└── __init__.py        # 导出默认日志记录器
```

[//]: # (## ⚠️ Windows 编码问题)

[//]: # ()

[//]: # (如果你遇到以下错误：)

[//]: # ()

[//]: # (```)

[//]: # (UnicodeEncodeError: 'gbk' codec can't encode character '\U0001f6a8' in position 0: illegal multibyte sequence)

[//]: # (```)

[//]: # ()

[//]: # (这是因为中文 Windows 默认使用 GBK 编码，而日志输出包含 Emoji 字符无法编码。解决方案：)

[//]: # ()

[//]: # (1. **切换终端编码为 UTF-8**：)

[//]: # (   ```cmd)

[//]: # (   chcp 65001)

[//]: # (   ```)

[//]: # ()

[//]: # (2. **禁用图标显示**：)

[//]: # (   ```python)

[//]: # (   from logre.handler.render import LogRenderConfig)

[//]: # (   LogRenderConfig.show_level_icon = False)

[//]: # (   ```)

[//]: # ()

[//]: # (3. **设置环境变量强制使用 UTF-8**：)

[//]: # (   ```cmd)

[//]: # (   set PYTHONIOENCODING=utf-8)

[//]: # (   ```)

[//]: # (## 🧪 测试)

[//]: # ()

[//]: # (项目包含完整的测试套件：)

[//]: # ()

[//]: # (```bash)

[//]: # (pytest tests/)

[//]: # (```)

## 📄 许可证

MIT License

## 🙏 致谢

- [Loguru](https://github.com/Delgan/loguru) - 灵感来自 Loguru 的强大日志管理
- [Rich](https://github.com/Textualize/rich) - 所有美丽都来自 Rich
