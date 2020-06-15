from alento_bot.storage_module.formats import BaseCache
import logging
import typing


logger = logging.getLogger("main_bot")


class AlreadyRegisteredName(Exception):
    """Raised when a cache is already registered under that name."""


class CacheNameNotRegistered(Exception):
    """Raised when a name is asked for that isn't registered yet."""


class CacheManager:
    def __init__(self):
        self._caches: typing.Dict[str, BaseCache] = dict()

    def register_cache(self, cache: BaseCache, cache_name: str):
        if not issubclass(type(cache), BaseCache):
            raise TypeError("Attempted to register a class that doesn't subclass BaseCache.")
        elif cache_name in self._caches:
            raise AlreadyRegisteredName("\"{}\" already registered.".format(cache_name))
        else:
            logger.debug("Cache \"{}\" registered".format(cache_name))
            self._caches[cache_name] = cache

    def get_cache(self, cache_name: str) -> typing.Optional[BaseCache]:
        return self._caches.get(cache_name, None)

    def save(self):
        logger.info("Saving caches...")
        for cache in self._caches:
            self._caches[cache].save(exiting=True)
        logger.info("Caches saved.")

    def load(self):
        logger.info("Loading caches...")
        for cache in self._caches:
            self._caches[cache].load()
        logger.info("Caches loaded.")
