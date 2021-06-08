from alento_bot.storage_module.formats.save_format import SaveLoadConfig
from alento_bot.storage_module.formats.config_format import ConfigData
import logging


logger = logging.getLogger("main_bot")


class GuildClass(SaveLoadConfig, path="you_shouldnt_see_this_guild"):
    def __init__(self, config: ConfigData, guild_id: int):
        super().__init__()
        self._data_path = f"{config.data_folder_path}/guilds/{guild_id}/{self._data_path}"
        self._from_disk: bool = False

    @classmethod
    def __init_subclass__(cls, name: str = "default_guild_name", **kwargs):
        super().__init_subclass__(path=name)
        cls._name: str = name


def guild_data_transformer(name: str = "default_guild_data_name"):
    def decorator(cls):
        class GuildWrapperClass(cls, GuildClass, name=name):
            def __init__(self, config: ConfigData, guild_id: int, **kwargs):
                GuildClass.__init__(self, config, guild_id)
                cls.__init__(self, **kwargs)
        return GuildWrapperClass
    return decorator
