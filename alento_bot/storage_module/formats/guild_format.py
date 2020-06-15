from alento_bot.storage_module.formats.config_format import ConfigData
from pathlib import Path
import warnings
import logging
import yaml


logger = logging.getLogger("main_bot")


class GuildClass:
    # def __init__(self, config: ConfigData, data_name: str, guild_id: int):
    #     self._config: ConfigData = config
    #     self._data_name: str = data_name
    #     self._guild_id: int = guild_id
    #     self._loaded: bool = False
    def __init__(self, config: ConfigData, guild_id: int):
        self._config: ConfigData = config
        self._guild_id: int = guild_id
        self._from_disk: bool = False

    @classmethod
    def __init_subclass__(cls, name: str = "default_cache_name", **kwargs):
        super().__init_subclass__(**kwargs)
        cls._data_name: str = name

    def loaded(self) -> bool:
        warnings.warn("Deprecated", DeprecationWarning)
        return self.from_disk()

    def from_disk(self) -> bool:
        return self._from_disk

    def save(self):
        guild_folder = f"{self._config.data_folder_path}/guilds/{self._guild_id}"
        logger.debug(f"Saving guild data for {guild_folder}/{self._data_name}.yaml...")
        Path(guild_folder).mkdir(exist_ok=True)
        file = open(f"{guild_folder}/{self._data_name}.yaml", "w")
        yaml.safe_dump(self.to_dict(), file)
        file.close()
        logger.debug("Saved.")

    def load(self):
        guild_file = f"{self._config.data_folder_path}/guilds/{self._guild_id}/{self._data_name}.yaml"
        if Path(guild_file).is_file():
            logger.debug(f"Found \"{guild_file}\" on disk, loading...")
            file = open(guild_file, "r")
            state = yaml.safe_load(file)
            file.close()
            self.from_dict(state)
            self._from_disk = True
            logger.debug("Loaded.")
        else:
            logger.debug(f"\"{guild_file}\" not on disk yet.")

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


def guild_data_transformer(name: str = "default_guild_data_name"):
    def decorator(cls):
        class GuildWrapperClass(cls, GuildClass, name=name):
            def __init__(self, config: ConfigData, guild_id: int, **kwargs):
                # GuildClass.__init__(self, config, name, guild_id)
                GuildClass.__init__(self, config, guild_id)
                cls.__init__(self, **kwargs)
        return GuildWrapperClass
    return decorator
