import logging

from logre.filter import BaseFilter
from logre.handler._handler import Handler
from logre.level import default_level

__all__ = ("Handler", "default_handler")


default_handler = Handler()
default_handler.addFilter(BaseFilter())
logging.basicConfig(
    level=default_level.num, format="%(message)s", handlers=[default_handler]
)