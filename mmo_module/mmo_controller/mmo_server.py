from mmo_module.mmo_data import BasicMMODataStorage, UserMMOConfig, GuildMMOConfig, CharacterSaveData, BaseCharacter
from alento_bot import StorageManager
from typing import Dict, Optional
import logging


logger = logging.getLogger("main_bot")


class MMOServer:
    def __init__(self, storage: StorageManager):
        self._storage: StorageManager = storage
        self._basic_storage: BasicMMODataStorage = self._storage.caches.get_cache("basic_mmo_data")
        self.guild: MMOGuildManager = MMOGuildManager(self._storage, self._basic_storage)
        self.user: MMOUserManager = MMOUserManager(self._storage, self._basic_storage)

    def full_tick(self):
        for user_id in self._basic_storage.enabled_users:
            pass
        for guild_id in self._basic_storage.enabled_guilds:
            pass


class MMOGuildManager:
    def __init__(self, storage: StorageManager, basic_storage: BasicMMODataStorage):
        self._storage: StorageManager = storage
        self._basic_storage: BasicMMODataStorage = basic_storage

    def add(self, guild_id: int) -> bool:
        guild_config: GuildMMOConfig = self._storage.guilds.get(guild_id, "mmo_config")
        if guild_config.enabled and guild_id in self._basic_storage.enabled_guilds:
            return False
        else:
            guild_config.enabled = True
            self._basic_storage.enabled_guilds.add(guild_id)
            return True

    def remove(self, guild_id: int) -> bool:
        guild_config: GuildMMOConfig = self._storage.guilds.get(guild_id, "mmo_config")
        if guild_config.enabled or guild_id in self._basic_storage.enabled_guilds:
            guild_config.enabled = True
            self._basic_storage.enabled_guilds.discard(guild_id)
            return True
        else:
            return False


class MMOUserManager:
    def __init__(self, storage: StorageManager, basic_storage: BasicMMODataStorage):
        self._storage: StorageManager = storage
        self._basic_storage: BasicMMODataStorage = basic_storage
        self._character_storage: Dict[int, BaseCharacter] = dict()

    def enabled(self, user_id: int) -> bool:
        if user_id in self._basic_storage.enabled_users:
            return True
        else:
            return False

    def enable(self, user_id: int) -> bool:
        user_config: GuildMMOConfig = self._storage.users.get(user_id, "mmo_config")
        if user_config.enabled and user_id in self._basic_storage.enabled_users:
            return False
        else:
            user_config.enabled = True
            self._basic_storage.enabled_users.add(user_id)
            return True

    def disable(self, user_id: int) -> bool:
        user_config: GuildMMOConfig = self._storage.users.get(user_id, "mmo_config")
        if user_config.enabled or user_id in self._basic_storage.enabled_users:
            user_config.enabled = False
            self._basic_storage.enabled_users.discard(user_id)
            return True
        else:
            return False

    def create_character(self):
        pass

    def get(self, user_id: int) -> Optional[BaseCharacter]:
        if user_id in self._basic_storage.enabled_users:
            if user_id not in self._character_storage:
                save_data = self._storage.users.get(user_id, "mmo_char_save")
                self._character_storage[user_id] = BaseCharacter(save_data)

            return self._character_storage[user_id]
        else:
            return None
