import logging

from logre.filter import default_filter
from logre.handler._handler import Handler
from logre.level import default_level

__all__ = ("Handler", "default_handler")


default_handler = Handler()
default_handler.addFilter(default_filter)
logging.basicConfig(
    level=default_level.num, format="%(message)s", handlers=[default_handler]
)
