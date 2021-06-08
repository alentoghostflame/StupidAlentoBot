from alento_bot.storage_module.formats.save_format import SaveLoadConfig
from alento_bot.storage_module.formats.config_format import ConfigData
import logging


logger = logging.getLogger("main_bot")


class UserClass(SaveLoadConfig, path="you_shouldnt_see_this_user"):
    def __init__(self, config: ConfigData, user_id: int):
        super().__init__()
        self._data_path = f"{config.data_folder_path}/users/{user_id}/{self._data_path}"
        self._from_disk: bool = False

    @classmethod
    def __init_subclass__(cls, name: str = "default_user_name", **kwargs):
        super().__init_subclass__(path=name)
        cls._name: str = name


def user_data_transformer(name: str = "default_user_data_name"):
    def decorator(cls):
        class UserWrapperClass(cls, UserClass, name=name):
            def __init__(self, config: ConfigData, user_id: int, **kwargs):
                UserClass.__init__(self, config, user_id)
                cls.__init__(self, **kwargs)
        return UserWrapperClass
    return decorator
