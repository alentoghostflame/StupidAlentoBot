import storage_module.disk_storage as disk_storage
import storage_module.ram_storage as ram_storage
# import storage_module.utils as utils
import universal_module.utils
# from discord.ext import commands
# import stupid_utils
import logging
# import typing
import yaml
import sys
import os


logger = logging.getLogger("Main")
sys.excepthook = universal_module.utils.log_exception_handler


class StorageManager:
    def __init__(self):
        self._ram_storage = ram_storage.RAMStorage()
        self._disk_storage = disk_storage.DiskStorage()

    def load_everything(self):
        if os.path.exists("config.yaml"):
            file = open("config.yaml", "r")
            self._disk_storage.load_config_from(file)
            file.close()
        else:
            file = open("config.yaml", "w")
            yaml.dump(self._disk_storage.config, file)

        os.makedirs(self._disk_storage.config.data_storage_path, exist_ok=True)
        server_data_path = self._disk_storage.config.data_storage_path + self._disk_storage.config.server_data_file_name
        if os.path.exists(server_data_path):
            file = open(server_data_path, "r")
            self._disk_storage.load_server_data_from(file)
            file.close()

    def save_everything(self):
        server_data_path = self._disk_storage.config.data_storage_path + self._disk_storage.config.server_data_file_name
        file = open(server_data_path, "w")
        self._disk_storage.save_server_data_to(file)

    def get_ram_storage(self) -> ram_storage.RAMStorage:
        return self._ram_storage

    def get_disk_storage(self) -> disk_storage.DiskStorage:
        return self._disk_storage
