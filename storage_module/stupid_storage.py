from storage_module.storage_utils import DiskServerData
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
        self._servers: typing.Dict[int, DiskServerData] = {}

    def get_server(self, server_id: int):
        if server_id not in self._servers:
            self._servers[server_id] = DiskServerData()
            logger.debug("Created data for server with ID of {}".format(server_id))
        return self._servers[server_id]

    def load_servers(self, file=None):
        logger.debug("Loading servers from file {}".format(file.name))
        if file:
            self._servers = yaml.full_load(file)
            logger.debug("Loaded servers from file {}".format(file.name))
        else:
            logger.debug("File {} not found, starting from scratch.".format(file.name))

    def save_servers(self, file):
        logger.debug("Saving servers to file {}".format(file.name))
        yaml.dump(self._servers, file, default_flow_style=None)
        logger.debug("Saved servers to file {}".format(file.name))

