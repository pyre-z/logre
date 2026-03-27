import sysconfig
import sys
import os
from pathlib import Path

__all__ = (
    # env
    "GIL_ENABLED",
    "IS_RUNNING_IN_PYCHARM",
    "IS_WINDOWS",
    # path
    "PROJECT_ROOT",
    "PACKAGE_ROOT",
)

# env
GIL_ENABLED = not bool(sysconfig.get_config_vars().get("Py_GIL_DISABLED"))
IS_RUNNING_IN_PYCHARM = "PYCHARM_HOSTED" in os.environ
IS_WINDOWS = sys.platform in ("win32", "cygwin", "cli")

# path
PROJECT_ROOT = Path(os.curdir).resolve()
PACKAGE_ROOT = Path(__file__).joinpath("../..").resolve()
