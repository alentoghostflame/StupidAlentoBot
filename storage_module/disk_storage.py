import storage_module.server_data as server_data
import storage_module.config_data as config_data
# import storage_module.utils as utils
from discord.ext import commands
import universal_module.utils
import logging
import typing
import yaml
import sys


logger = logging.getLogger("Main")
sys.excepthook = universal_module.utils.log_exception_handler


class DiskStorage:
    def __init__(self):
        self._guilds: typing.Dict[int, server_data.DiskServerData] = {}
        self.config = config_data.ConfigData()

    def get_server(self, server_id: int):
        if server_id not in self._guilds:
            self._guilds[server_id] = server_data.DiskServerData()
            logger.debug("Created data for server with ID of {}".format(server_id))
        return self._guilds[server_id]

    def get_server_names(self, bot: commands.Bot) -> dict:
        return server_data.get_all_server_names(self._guilds, bot)

    def get_guild_ids(self) -> set:
        return set(self._guilds.keys())

    def load_server_data_from(self, file):
        logger.debug("Loading servers from file {}".format(file.name))
        self._guilds = yaml.full_load(file)
        logger.debug("Loaded servers from file {}".format(file.name))

    def save_server_data_to(self, file):
        logger.debug("Saving servers to file {}".format(file.name))
        yaml.dump(self._guilds, file, default_flow_style=None)
        logger.debug("Saved servers to file {}".format(file.name))

    # def clean_servers(self, bot: commands.Bot):
    #     # NOT SAFE.
    #     logger.debug("Cleaning server storage.")
    #     for guild_id in self._guilds.copy():
    #         if not bot.get_guild(guild_id):
    #             self._guilds.pop(guild_id)
    #             logger.debug("Removed server with ID {} from storage.".format(guild_id))
    #     logger.debug("Cleaned server storage.")

    def load_config_from(self, file):
        logger.debug("Loading config from file \"{}\"".format(file.name))
        self.config = yaml.full_load(file)
        logger.debug("Loaded config from file \"{}\"".format(file.name))
