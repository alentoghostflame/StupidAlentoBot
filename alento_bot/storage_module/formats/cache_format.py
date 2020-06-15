from alento_bot.storage_module.formats.config_format import ConfigData
from pathlib import Path
import warnings
import logging
import yaml


logger = logging.getLogger("main_bot")


class BaseCache:
    # def __init__(self, config: ConfigData, data_name: str, save_on_exit: bool = True):
    #     self._config: ConfigData = config
    #     self._data_name: str = data_name
    #     self._save_on_exit: bool = save_on_exit
    #     self._loaded: bool = False
    def __init__(self, config: ConfigData):
        self._config: ConfigData = config
        self._from_disk: bool = False

    @classmethod
    def __init_subclass__(cls, name: str = "default_cache_name", save_on_exit: bool = True, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._data_name: str = name
        cls._save_on_exit: bool = save_on_exit

    def loaded(self) -> bool:
        warnings.warn("Deprecated", DeprecationWarning)
        return self.from_disk()

    def from_disk(self) -> bool:
        return self._from_disk

    def save(self, exiting: bool = False):
        if not exiting or (exiting and self._save_on_exit):
            # logger.debug("Saving cache {}".format(self._file_name))

            # cache_location = "{}/cache/{}.yaml".format(self._config.data_folder_path, self._file_name)
            cache_location = f"{self._config.data_folder_path}/cache/{self._data_name}.yaml"
            logger.debug(f"Saving cache data for {cache_location}...")
            file = open(cache_location, "w")
            yaml.safe_dump(self.to_dict(), file)
            file.close()
            # logger.debug("Saved {}".format(self._file_name))
            logger.debug("Saved.")
        else:
            # logger.debug("Cache {} disabled save on exit, ignoring.".format(self._file_name))
            logger.debug(f"Cache {self._data_name} disabled saving on exit, ignoring.")

    def load(self):
        # logger.debug("Loading cache {}".format(self._data_name))
        # cache_location = "{}/cache/{}".format(self._config.data_folder_path, self._data_name)
        cache_location = f"{self._config.data_folder_path}/cache/{self._data_name}.yaml"
        if Path(cache_location).is_file():
            logger.debug(f"Found \"{cache_location}\" on disk, loading...")
            file = open(cache_location, "r")
            state = yaml.safe_load(file)
            file.close()
            self.from_dict(state)
            self._from_disk = True
            # logger.debug("Loaded {}".format(self._data_name))
            logger.debug("Loaded.")
        else:
            # logger.debug("{} not on disk yet.".format(self._data_name))
            logger.debug(f"\"{cache_location}\" not on disk yet.")

    def from_dict(self, state: dict):
        for key in state:
            if key in self.__dict__:
                self.__dict__[key] = state[key]

    def to_dict(self) -> dict:
        output_dict = dict()
        for key in self.__dict__:
            if key[0] != "_":
                output_dict[key] = self.__dict__[key]
        return output_dict


def cache_transformer(name: str = "default_cache_name", save_on_exit: bool = True):
    def decorator(cls):
        class CacheWrapperClass(cls, BaseCache, name=name, save_on_exit=save_on_exit):
            def __init__(self, config: ConfigData, **kwargs):
                # BaseCache.__init__(self, config, name, save_on_exit=save_on_exit)
                BaseCache.__init__(self, config)
                cls.__init__(self, **kwargs)
        return CacheWrapperClass
    return decorator
