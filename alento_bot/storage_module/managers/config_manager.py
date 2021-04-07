from alento_bot.storage_module.formats import ConfigData
import logging
import warnings


logger = logging.getLogger("main_bot")


class ConfigManager:
    def __init__(self, config_path: str = "ImIgnoredNow"):
        self._config_path = config_path
        self._config = ConfigData()
        warnings.warn("Init ConfigData instead.", DeprecationWarning)

    def load(self):
        self._config.load()
        if not self._config.from_disk:
            self._config.save()

    def get_config(self) -> ConfigData:
        warnings.warn("Grab ConfigData instead.", DeprecationWarning)
        return self._config

    def from_dict(self, state: dict):
        warnings.warn("What are you doing? Don't load the config like this.", DeprecationWarning)
        self._config._from_dict(state)

    def to_dict(self) -> dict:
        return self._config.to_dict()
