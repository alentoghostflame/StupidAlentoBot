from alento_bot.storage_module.formats import BaseCache, ConfigData
from inspect import isclass
import logging
from typing import Dict, Union, Optional, Type

logger = logging.getLogger("main_bot")


class AlreadyRegisteredName(Exception):
    """Raised when a cache is already registered under that name."""


class CacheNameNotRegistered(Exception):
    """Raised when a name is asked for that isn't registered yet."""


class CacheManager:
    def __init__(self, config: ConfigData):
        self._caches: Dict[str, BaseCache] = dict()
        self._config: ConfigData = config

    def register_cache(self, cache_name: str, cache: Union[Type[BaseCache], BaseCache]) -> Optional[BaseCache]:
        if cache_name in self._caches:
            raise AlreadyRegisteredName("\"{}\" already registered.".format(cache_name))
        elif isclass(cache) and issubclass(cache, BaseCache):
            logger.debug("Doing init of cache for you!")
            logger.debug("Cache \"{}\" registered".format(cache_name))
            self._caches[cache_name] = cache(self._config)
            return self._caches[cache_name]
        elif issubclass(type(cache), BaseCache):
            logger.debug("Cache \"{}\" registered".format(cache_name))
            self._caches[cache_name] = cache
            return self._caches[cache_name]
        else:
            raise TypeError("Attempted to register a class that doesn't subclass BaseCache.")

    def get_cache(self, cache_name: str) -> Optional[BaseCache]:
        return self._caches.get(cache_name, None)

    def save(self):
        logger.debug("Saving caches...")
        for cache in self._caches:
            self._caches[cache].save(exiting=True)
        logger.debug("Caches saved.")

    def load(self):
        logger.debug("Loading caches...")
        for cache in self._caches:
            self._caches[cache].load()
        logger.debug("Caches loaded.")
