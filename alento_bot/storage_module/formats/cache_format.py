from alento_bot.storage_module.formats.save_format import SaveLoadConfig
from alento_bot.storage_module.formats.config_format import ConfigData
import logging


logger = logging.getLogger("main_bot")


class BaseCache(SaveLoadConfig, path="you_shouldnt_see_this_cache.yaml"):
    def __init__(self, config: ConfigData):
        super().__init__()
        self._data_path = f"{config.data_folder_path}/cache/{self._name}.yaml"
        self._from_disk: bool = False

    @classmethod
    def __init_subclass__(cls, name: str = "default_cache_name", save_on_exit: bool = True, **kwargs):
        super().__init_subclass__(path=name)
        cls._name = name
        cls._save_on_exit: bool = save_on_exit

    def save(self, exiting: bool = False):
        if not exiting or (exiting and self._save_on_exit):
            logger.debug(f"Saving cache data for {self._data_path}...")
            super().save()
        else:
            logger.debug(f"Cache {self._name} disabled saving on exit, ignoring.")


def cache_transformer(name: str = "default_cache_name", save_on_exit: bool = True):
    def decorator(cls):
        class CacheWrapperClass(cls, BaseCache, name=name, save_on_exit=save_on_exit):
            def __init__(self, config: ConfigData, **kwargs):
                BaseCache.__init__(self, config)
                cls.__init__(self, **kwargs)
        return CacheWrapperClass
    return decorator
