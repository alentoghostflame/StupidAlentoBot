from alento_bot.storage_module.formats.config_format import ConfigData
from pathlib import Path
import warnings
import logging
import yaml


logger = logging.getLogger("main_bot")


class UserClass:
    # def __init__(self, config: ConfigData, data_name: str, user_id: int):
    #     self._config: ConfigData = config
    #     self._data_name: str = data_name
    #     self._user_id: int = user_id
    #     self._loaded: bool = False
    def __init__(self, config: ConfigData, user_id: int):
        self._config: ConfigData = config
        self._user_id: int = user_id
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
        user_folder = f"{self._config.data_folder_path}/users/{self._user_id}"
        logger.debug(f"Saving user data for {user_folder}/{self._data_name}.yaml...")
        Path(user_folder).mkdir(exist_ok=True)
        file = open(f"{user_folder}/{self._data_name}.yaml", "w")
        yaml.safe_dump(self.to_dict(), file)
        file.close()
        logger.debug("Saved.")

    def load(self):
        user_file = f"{self._config.data_folder_path}/users/{self._user_id}/{self._data_name}.yaml"
        if Path(user_file).is_file():
            logger.debug(f"Found \"{user_file}\" on disk, loading...")
            file = open(user_file, "r")
            state = yaml.safe_load(file)
            file.close()
            self.from_dict(state)
            self._from_disk = True
            logger.debug(f"Loaded.")
        else:
            logger.debug(f"\"{user_file}\" not on disk yet.")

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


def user_data_transformer(name: str = "default_user_data_name"):
    def decorator(cls):
        class UserWrapperClass(cls, UserClass, name=name):
            def __init__(self, config: ConfigData, user_id: int, **kwargs):
                # UserClass.__init__(self, config, name, user_id)
                UserClass.__init__(self, config, user_id)
                cls.__init__(self, **kwargs)
        return UserWrapperClass
    return decorator
