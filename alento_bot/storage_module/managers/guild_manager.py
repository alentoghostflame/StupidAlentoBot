from alento_bot.storage_module.formats import ConfigData, GuildClass
from pathlib import Path
import logging
import typing


logger = logging.getLogger("main_bot")


class AlreadyRegisteredGuildName(Exception):
    """Raised when a guild data type is already registered under that name."""
    pass


class GuildNameNotRegistered(Exception):
    """Raised when a name is asked for that isn't registered yet."""


class GuildManager:
    def __init__(self, config: ConfigData):
        self.config: ConfigData = config
        self._guilds: typing.Dict[int, typing.Dict[str, GuildClass]] = dict()
        self._guild_data_names: typing.Dict[str, type] = dict()

    def register_data_name(self, data_name: str, guild_object: type):
        if not issubclass(guild_object, GuildClass):
            raise TypeError("Attempted to register a class that doesn't subclass GuildClass.")
        elif data_name in self._guild_data_names:
            raise AlreadyRegisteredGuildName(f"\"{data_name}\" already registered.")
        else:
            self._guild_data_names[data_name] = guild_object
            logger.debug(f"Guild data \"{data_name}\" registered.")

    def get(self, guild_id: int, data_name: str):
        if data_name not in self._guild_data_names:
            raise GuildNameNotRegistered("Attempted to use an unregistered data name")

        if guild_id in self._guilds and data_name in self._guilds[guild_id]:
            return self._guilds[guild_id][data_name]
        else:
            guilds_folder_location = f"{self.config.data_folder_path}/guilds/{guild_id}"
            Path(guilds_folder_location).mkdir(exist_ok=True)

            guild_data_class_raw = self._guild_data_names[data_name]
            guild_data_class = guild_data_class_raw(self.config, guild_id)
            guild_data_class.load()

            if guild_id not in self._guilds:
                self._guilds[guild_id] = dict()

            self._guilds[guild_id][data_name] = guild_data_class

            return self._guilds[guild_id][data_name]

    def save(self):
        for server_id in self._guilds:
            for data_name in self._guilds[server_id]:
                self._guilds[server_id][data_name].save()

    def load(self):
        pass
