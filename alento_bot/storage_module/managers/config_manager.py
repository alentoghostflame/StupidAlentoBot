from alento_bot.storage_module.formats import ConfigData
from pathlib import Path
import logging
import yaml


logger = logging.getLogger("main_bot")


class ConfigManager:
    def __init__(self, config_path: str = "config.yaml"):
        self._config_path: str = config_path
        self._config: ConfigData = ConfigData()

    def load(self):
        if Path(self._config_path).is_file():
            logger.debug(f"Loading config from path \"{self._config_path}\"...")
            file = open(self._config_path, "r")
            state = yaml.safe_load(file)
            file.close()
            self.from_dict(state)
            logger.debug("Config loaded.")
        else:
            logger.warning(f"Config doesn't exist on path \"{self._config_path}\", creating...")
            file = open(self._config_path, "w")
            yaml.safe_dump(self.to_dict(), file)
            file.close()
            logger.info("Config created.")

    def get_config(self) -> ConfigData:
        return self._config

    def from_dict(self, state: dict, strict: bool = True):
        for key in state:
            if strict:
                if key in self._config.__dict__:
                    self._config.__dict__[key] = state[key]
            else:
                self._config.__dict__[key] = state[key]

    def to_dict(self) -> dict:
        return self._config.__dict__
