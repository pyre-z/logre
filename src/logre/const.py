import sysconfig
import sys
import os
from pathlib import Path

__all__ = (
    # env
    "GIL_ENABLED",
    "IS_RUNNING_IN_PYCHARM",
    "IS_RUNNING_IN_DEBUGPY",
    "IS_WINDOWS",
    # path
    "PROJECT_ROOT",
    "PACKAGE_ROOT",
)

# env
GIL_ENABLED = not bool(sysconfig.get_config_vars().get("Py_GIL_DISABLED", True))

IS_RUNNING_IN_PYCHARM = bool(os.environ.get("PYCHARM_HOSTED", False))
IS_RUNNING_IN_DEBUGPY = bool(os.environ.get("DEBUGPY_RUNNING", False))

IS_WINDOWS = sys.platform in ("win32", "cygwin", "cli")

# path
PROJECT_ROOT = Path(os.curdir).resolve()
PACKAGE_ROOT = Path(__file__).joinpath("../..").resolve()
