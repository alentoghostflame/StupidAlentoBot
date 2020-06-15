from alento_bot.storage_module.formats import ConfigData, UserClass
from pathlib import Path
import logging
import typing


logger = logging.getLogger("main_bot")


class AlreadyRegisteredUserName(Exception):
    """Raised when a user data type is already registered under that name."""


class UserNameNotRegistered(Exception):
    """Raised when a name is asked for that isn't registered yet."""


class UserManager:
    def __init__(self, config: ConfigData):
        self.config: ConfigData = config
        self._users: typing.Dict[int, typing.Dict[str, UserClass]] = dict()
        self._user_data_names: typing.Dict[str, type] = dict()

    def register_data_name(self, data_name: str, user_object: type):
        if not issubclass(user_object, UserClass):
            raise TypeError("Attempted to register a class that doesn't subclass UserClass.")
        elif data_name in self._user_data_names:
            raise AlreadyRegisteredUserName(f"\"{data_name}\" already registered.")
        else:
            self._user_data_names[data_name] = user_object
            logger.debug(f"User data \"{data_name}\" registered.")

    def get(self, user_id: int, data_name: str):
        if data_name not in self._user_data_names:
            raise UserNameNotRegistered("Attempted to use an unregistered data name")

        if user_id in self._users and data_name in self._users[user_id]:
            return self._users[user_id][data_name]
        else:
            users_folder_location = f"{self.config.data_folder_path}/users/{user_id}"
            Path(users_folder_location).mkdir(exist_ok=True)

            user_data_class_raw = self._user_data_names[data_name]
            user_data_class = user_data_class_raw(self.config, user_id)
            user_data_class.load()

            if user_id not in self._users:
                self._users[user_id] = dict()

            self._users[user_id][data_name] = user_data_class

            return self._users[user_id][data_name]

    def save(self):
        for server_id in self._users:
            for data_name in self._users[server_id]:
                self._users[server_id][data_name].save()

    def load(self):
        pass

