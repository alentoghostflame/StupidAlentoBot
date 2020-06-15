from alento_bot.storage_module.managers import ConfigManager, CacheManager, GuildManager, UserManager
from alento_bot.storage_module.formats import ConfigData
from pathlib import Path
import logging


logger = logging.getLogger("main_bot")


class StorageManager:
    def __init__(self):
        self._loaded: bool = False
        self._config_manager: ConfigManager = ConfigManager()
        self.config: ConfigData = self._config_manager.get_config()
        self.create_folder_structure()
        self.caches = CacheManager()
        self.guilds: GuildManager = GuildManager(self.config)
        self.users: UserManager = UserManager(self.config)

    def create_folder_structure(self):
        data_folder = self.config.data_folder_path
        Path(f"{data_folder}").mkdir(exist_ok=True)
        Path(f"{data_folder}/cache").mkdir(exist_ok=True)
        Path(f"{data_folder}/guilds").mkdir(exist_ok=True)
        Path(f"{data_folder}/users").mkdir(exist_ok=True)

    def load(self):
        logger.info("Loading storage...")
        self._config_manager.load()
        self.caches.load()
        self._loaded = True
        logger.info("Storage loaded.")

    def save(self):
        logger.info("Saving storage...")
        self.guilds.save()
        self.users.save()
        self.caches.save()
        logger.info("Saved.")

    def loaded(self) -> bool:
        return self._loaded
