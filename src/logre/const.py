import sysconfig
import sys
import os
from pathlib import Path

__all__ = (
    # env
    "GIL_ENABLED",
    "IS_RUNNING_IN_PYCHARM",
    "IS_WINDOWS",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    # path
    "PROJECT_ROOT",
    "PACKAGE_ROOT",
)

# env
GIL_ENABLED = not bool(sysconfig.get_config_vars().get("Py_GIL_DISABLED"))
IS_RUNNING_IN_PYCHARM = "PYCHARM_HOSTED" in os.environ
IS_WINDOWS = sys.platform in ("win32", "cygwin", "cli")
HTTP_PROXY = os.environ.get("HTTP_PROXY", None)
HTTPS_PROXY = os.environ.get("HTTPS_PROXY", None)

# path
PROJECT_ROOT = Path(__file__).joinpath("../../..").resolve()
PACKAGE_ROOT = PROJECT_ROOT.joinpath("src").resolve()
