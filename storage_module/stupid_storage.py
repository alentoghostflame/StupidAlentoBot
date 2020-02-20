import storage_module.storage_utils as storage_utils
from discord.ext import commands
# import stupid_utils
import logging
import typing
import yaml
# import sys


logger = logging.getLogger("Main")
# sys.excepthook = stupid_utils.log_exception_handler


class RAMStorage:
    def __init__(self):
        pass


class DiskStorage:
    def __init__(self):
        self._guilds: typing.Dict[int, storage_utils.DiskServerData] = {}

    def get_server(self, server_id: int):
        if server_id not in self._guilds:
            self._guilds[server_id] = storage_utils.DiskServerData()
            logger.debug("Created data for server with ID of {}".format(server_id))
        return self._guilds[server_id]

    def get_server_names(self, bot: commands.Bot) -> dict:
        return storage_utils.get_all_server_names(self._guilds, bot)

    def load_servers(self, file=None):
        logger.debug("Loading servers from file {}".format(file.name))
        if file:
            self._guilds = yaml.full_load(file)
            logger.debug("Loaded servers from file {}".format(file.name))
        else:
            logger.debug("File {} not found, starting from scratch.".format(file.name))

    def save_servers(self, file):
        logger.debug("Saving servers to file {}".format(file.name))
        yaml.dump(self._guilds, file, default_flow_style=None)
        logger.debug("Saved servers to file {}".format(file.name))

    def clean_servers(self, bot: commands.Bot):
        logger.debug("Cleaning server storage.")
        for guild_id in self._guilds.copy():
            if not bot.get_guild(guild_id):
                self._guilds.pop(guild_id)
                logger.debug("Removed server with ID {} from storage.".format(guild_id))
        logger.debug("Cleaned server storage.")

