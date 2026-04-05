import itertools
import os
import site
import sys
from functools import lru_cache
from pathlib import Path

from logre.const import PROJECT_ROOT

__all__ = ("path2pkg", "resolve_path")

_SYS_PATH = []
for _p in sys.path:
    if (_p + os.sep + "Lib") not in sys.path:
        _SYS_PATH.append(Path(_p).resolve())

_SITE_PATH_LIST = sorted(map(Path, site.getsitepackages())) + [
    Path(site.getusersitepackages()),
    PROJECT_ROOT.joinpath(".venv/Lib/site-packages").resolve(),
    PROJECT_ROOT.joinpath("src").resolve(),
    PROJECT_ROOT,
]
_ALL_PATHS = list(
    filter(
        lambda x: x.exists(),
        itertools.chain.from_iterable([_SITE_PATH_LIST, _SYS_PATH]),
    )
)
_ALL_PATHS = sorted(set(_ALL_PATHS), key=lambda x: _ALL_PATHS.index(x))


@lru_cache(maxsize=64)
def resolve_path(path: str | Path, root: Path = PROJECT_ROOT) -> str:
    root = root.resolve().absolute()
    if path != "<input>":
        path = Path(path)
        _path = path2pkg(path, root=root)
        path_string = "<SITE>" if _path is None else _path
    else:
        path_string = "<INPUT>"
    return path_string


@lru_cache(128)
def path2pkg(
    path: str | Path,
    *,
    root: Path = PROJECT_ROOT,
    pkg_replace_map: dict[str, str] | None = None,
) -> str | None:
    path = Path(path).resolve().absolute().with_suffix("")
    root = root.resolve().absolute()

    new_path: Path | None = None

    for site_path in _ALL_PATHS:
        if path.is_relative_to(site_path):
            temp_path = path.relative_to(site_path)
            if new_path is None or len(temp_path.parts) < len(new_path.parts):
                new_path = temp_path

    if new_path is None:
        if path.is_relative_to(root):
            path_string = Path(path).relative_to(root).stem.replace(os.sep, ".")
        else:
            path_string = None
    else:
        path_string = str(new_path).replace(os.sep, ".")
    if path_string is not None:
        for old_str in ["lib.site-packages.", "Lib.site-packages."]:
            result = path_string.replace(old_str, "")
    else:
        result = "？"
    if pkg_replace_map:
        for k, v in pkg_replace_map.items():
            result = result.replace(k, v)
    return result
